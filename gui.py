#!/usr/bin/python3

# Built-in modules
import logging


def task():
    print("Hello")
    logger.error("ERROR")
    root.after(100, task)
# Sample usage
if __name__ == '__main__':
    # Create the GUI
    root = tkinter.Tk()
    app = Application(master=root)    

    # Create textLogger
    text_handler = TextHandler(app.log_display)

    # Add the handler to logger
    logger = logging.getLogger()
    logger.addHandler(text_handler)

    # Log some messages
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    root.after(100, task)
    root.mainloop()


