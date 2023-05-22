import logging


logger = logging.getLogger('client')

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s ')

fh = logging.FileHandler('log/client.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.setLevel(logging.DEBUG)
