import tkinter as tk
import wikipediaapi
from bs4 import BeautifulSoup
import sys
import csv
import re
import zmq
import json


def csv_out(pkwd, skwd, txt):
    """Writes keyword inputs and text output to csv file"""

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['input_keywords', 'output_content'])
        writer.writerow([pkwd + ';' + skwd, txt])


def search_wiki(pkwd, skwd):
    """
    Searches Wikipedia for a paragraph containing pkwd and skwd
    Returns text if it exists, otherwise returns None
    """

    # init Wikipedia module to extract HTML content of page
    wiki = wikipediaapi.Wikipedia(
        language='en', extract_format=wikipediaapi.ExtractFormat.HTML)

    # if page exists, get its HTML content
    if wiki.page(pkwd).exists():
        page = wiki.page(pkwd)
        soup = BeautifulSoup(page.text, 'html.parser')
    else:
        return None

    # find paragraph containing pkwd and skwd
    for p in soup.find_all('p'):
        if re.search(r'\b' + pkwd + r'\b', p.text, re.IGNORECASE) \
                and re.search(r'\b' + skwd + r'\b', p.text, re.IGNORECASE):

            return p.text


def display_error_gui():
    """Displays an error on the GUI"""

    txt_out.configure(state='normal', fg='red')
    txt_out.delete(1.0, tk.END)
    txt_out.insert(1.0, 'Unable to generate content!')
    txt_out.configure(state='disabled')


def display_text_gui(txt):
    """Displays generated text on the GUI"""

    txt_out.configure(state='normal', fg='black')
    txt_out.delete(1.0, tk.END)
    txt_out.insert(1.0, txt)
    txt_out.configure(state='disabled')


def clear_text_gui():
    """Clears all text from the GUI"""

    txt_out.configure(state='normal')
    txt_out.delete(1.0, tk.END)
    txt_out.configure(state='disabled')

    ent_pkwd.delete(0, tk.END)
    ent_skwd.delete(0, tk.END)


def display_kwds_gui(pkwd, skwd):
    """Displays keywords on the GUI"""

    ent_pkwd.delete(0, tk.END)
    ent_pkwd.insert(0, pkwd)
    ent_skwd.delete(0, tk.END)
    ent_skwd.insert(0, skwd)


def gen_text_gui():
    """Generates text using keywords from GUI and writes to csv file"""

    pkwd, skwd = ent_pkwd.get(), ent_skwd.get()
    txt = search_wiki(pkwd, skwd)

    if txt:
        display_text_gui(txt)
        csv_out(pkwd, skwd, txt)
    else:
        display_error_gui()
        print('Unable to generate content!')


def gen_text_csv(file):
    """Generates text using keywords from csv and writes to csv file"""

    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            kwds = row['input_keywords'].split(';')
            pkwd, skwd = kwds[0], kwds[1]

    txt = search_wiki(pkwd, skwd)

    if txt:
        csv_out(pkwd, skwd, txt)
    else:
        print('Unable to generate content!')


def create_socket():
    """Returns a socket for microservice communication"""

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    return socket


def gen_text_mcrosvc():
    """Generates text using keywords from microservice"""

    socket = create_socket()
    print('Requesting data from life generator microservice...')

    message = socket.recv_json()
    print("Received reply: %s" % message)

    item_name = message[0].split()
    pkwd, skwd = item_name[0], item_name[1]
    txt = search_wiki(pkwd, skwd)

    display_kwds_gui(pkwd, skwd)

    send_txt_mcrosvc(txt, message, socket)


def send_txt_mcrosvc(txt, message, socket):
    """Sends generated text to microservice"""

    if txt is None:
        socket.send_string(json.dumps("NULL"))
        display_error_gui()
        print('Unable to generate content!')
    else:
        reply = f"{txt}\n\nThe {message[0]} received{message[2]} reviews \
            on Amazon with an average{message[1]} rating."
        display_text_gui(reply)
        print('Sending reply:\n%s' % reply)
        socket.send_string(json.dumps(reply))


def create_window():
    """Creates and configures GUI window and returns it"""

    window = tk.Tk()
    window.title('Content Generator')
    window.geometry('1000x650')
    window['bg'] = '#F8F9F9'
    window.columnconfigure([0, 1], weight=1, minsize=50)
    window.rowconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=75)

    return window


def create_btn_widgets():
    """Creates and configures button widgets and returns them"""

    btn_clear = tk.Button(text='Clear Text', height=2, width=10, relief=tk.RAISED,
                          command=clear_text_gui, font=(None, 16), highlightbackground='#AEB6BF',
                          highlightcolor='#AEB6BF')

    btn_out = tk.Button(text='Generate Text', height=2, width=10, relief=tk.RAISED,
                        command=gen_text_gui, font=(None, 16), highlightbackground='#AEB6BF',
                        highlightcolor='#AEB6BF')

    btn_mcrosvc = tk.Button(text='Get Keywords', height=2, width=10, relief=tk.RAISED,
                            command=gen_text_mcrosvc, font=(None, 16), highlightbackground='#AEB6BF',
                            highlightcolor='#AEB6BF')

    return btn_out, btn_mcrosvc, btn_clear


def create_txt_widgets():
    """Creates and configures text widgets and returns them"""

    ent_pkwd = tk.Entry(relief=tk.SUNKEN, borderwidth=1,
                        highlightbackground='#5499C7', highlightcolor='#5499C7')

    ent_skwd = tk.Entry(relief=tk.SUNKEN, borderwidth=1,
                        highlightbackground='#5499C7', highlightcolor='#5499C7')

    txt_out = tk.Text(wrap='word', relief=tk.SUNKEN, borderwidth=1, font=('TkDefaultFont', 13),
                      highlightbackground='#5499C7', highlightcolor='#5499C7', state='disabled')
    txt_out.bind('<1>', lambda event: txt_out.focus_set())

    return ent_pkwd, ent_skwd, txt_out


def layout_widgets(widgets):
    """
    Configures the layout of the text and button widgets
    Widgets is a tuple containing the widgets to be configured
    """

    widgets[0].grid(row=1, column=1, sticky='w')
    widgets[1].grid(row=2, column=1, sticky='w')
    widgets[2].grid(row=3, column=1, sticky='w')
    widgets[3].grid(row=4, column=0, columnspan='2',
                    padx=20, pady=20, ipadx=5, ipady=5)
    widgets[4].grid(row=4, column=1, padx=20, pady=20, ipadx=5, ipady=5)
    widgets[5].grid(row=4, column=1, sticky='e',
                    padx=20, pady=20, ipadx=5, ipady=5)


def create_labels():
    """Creates and configures label widgets"""

    tk.Label(text='Content Generator', height=2, font=(None, 28),
             bg='#F8F9F9', pady=20).grid(row=0, column=0, columnspan=2)
    tk.Label(text='Enter primary keyword', bg='#F8F9F9',
             font=(None, 16)).grid(row=1, column=0, padx=10, pady=10)
    tk.Label(text='Enter secondary keyword', bg='#F8F9F9',
             font=(None, 16)).grid(row=2, column=0, padx=10, pady=10)
    tk.Label(text='Generated Text', bg='#F8F9F9',
             font=(None, 16)).grid(row=3, column=0)


if __name__ == '__main__':

    inputfile = sys.argv[1:]

    # input.csv file provided
    if len(inputfile) != 0:
        gen_text_csv(inputfile[0])

    # input.csv file not provided
    else:
        window = create_window()
        ent_pkwd, ent_skwd, txt_out = create_txt_widgets()
        btn_out, btn_mcrosvc, btn_clear = create_btn_widgets()
        layout_widgets((ent_pkwd, ent_skwd, txt_out,
                        btn_out, btn_mcrosvc, btn_clear))
        create_labels()
        window.mainloop()
