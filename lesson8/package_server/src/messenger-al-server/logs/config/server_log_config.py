import logging
import os
import logging.handlers
from os.path import dirname, join

LOG = logging.getLogger('app.server')
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)-10s - %(message)s')

f_path = os.getcwd()
print(f_path)
# FILE_HANDLER = logging.FileHandler(f'{f_path}/logs/app.server.log', encoding='utf-8')
FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(f'{f_path}/logs/app.server.log', encoding='utf-8',
                                                         interval=1, when='midnight')
FILE_HANDLER.setFormatter(FORMATTER)

LOG.addHandler(FILE_HANDLER)
LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    LOG.debug('debug')
