# Content Generator

A microservice built with Python which generates a paragraph of text containing a user defined primary and secondary keyword obtained via the GUI or through inter-process communication with an external microservice.

![Content Generator in Action](/assets/img/demo.gif)

## High-level Architecture
![Architecture](/assets/img/architecture.png)

## Running the Microservice using the GUI

1. `cd` into the project directory
2. Run `pip3 install -r requirements.txt` to install the project dependencies
3. Run the program from the terminal command line by entering `python3 content_generator.py`
4. Enter both a primary and secondary keyword and click on the `Generate Text` button
4. The GUI will display text containing both the primary and secondary keyword or an error message if no text could be generated
