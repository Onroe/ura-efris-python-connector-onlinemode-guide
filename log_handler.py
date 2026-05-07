'''
Created on 19/11/2023

@author: lenin
'''

import logging
import logging.handlers as handlers
import time
import re
import os


class LogHandler():

    def logit():

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(BASE_DIR+'/logfiles'):
            try:
                os.makedirs(BASE_DIR+'/logfiles')
            except FileExistsError:
                pass

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # Here we define our formatter
        formatter = logging.Formatter(
            '%(asctime)s  - %(levelname)s - %(message)s',  "%Y-%m-%d %H:%M:%S")
        log_handler = handlers.TimedRotatingFileHandler(
            BASE_DIR+'/logfiles/dqs.log', when='midnight', interval=2, backupCount=5)
        log_handler.setLevel(logging.INFO)

        log_handler.setFormatter(formatter)

        # add a suffix which you want
        log_handler.suffix = "%Y%m%d"
        #  need to change the extMatch variable to match the suffix for it
        log_handler.extMatch = re.compile(r"^\d{8}$")

        logger.addHandler(log_handler)
        
        return logger

    def logger():
        if not os.path.exists('logfiles'):
            try:
                os.makedirs("logfiles")
            except FileExistsError:
                pass

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # Here we define our formatter
        formatter = logging.Formatter(
            '%(asctime)s  - %(levelname)s - %(message)s',  "%Y-%m-%d %H:%M:%S")
        log_handler = handlers.RotatingFileHandler(
            "logfiles/log.log", mode='a', maxBytes=10000, encoding=None, delay=False)
        log_handler.setLevel(logging.INFO)

        log_handler.setFormatter(formatter)

        # add a suffix which you want
        log_handler.suffix = "%Y%m%d"
        #  need to change the extMatch variable to match the suffix for it
        log_handler.extMatch = re.compile(r"^\d{8}$")

        logger.addHandler(log_handler)
        return logger







