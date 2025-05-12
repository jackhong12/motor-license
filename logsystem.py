import logging

def loggerInit ():
    logger = logging.getLogger("booking system")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    # Create a file handler
    fileHandler = logging.FileHandler(".system.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    # Create a console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    return logger

def info (msg):
    __logger.info(msg)

def debug (msg):
    __logger.debug(msg)

__logger = loggerInit()
