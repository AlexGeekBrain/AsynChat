import logging
from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger('server')

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s ')

trfh = TimedRotatingFileHandler('log/server.log', interval=1, when='D', encoding='utf-8')
trfh.setLevel(logging.DEBUG)
trfh.setFormatter(formatter)

logger.addHandler(trfh)
logger.setLevel(logging.DEBUG)
