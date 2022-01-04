import logging
import os

from os.path import dirname, join

LOG = logging.getLogger('app.client')
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)-10s - %(message)s')

f_path = os.getcwd()

FILE_HANDLER = logging.FileHandler(f'{f_path}/logs/app.client.log', encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)

LOG.addHandler(FILE_HANDLER)
LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    LOG.debug('debug')
