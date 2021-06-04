
import logging
application_formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
message_formatter = logging.Formatter('%(message)s')


def setup_logger(name, log_file, formatter, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


APP_LOGGER = setup_logger('app_logger', 'application_logfile.log', application_formatter)
MESSAGE_LOGGER = setup_logger('message_logger', 'message_logfile.log', message_formatter)

REG_PUB = "REGISTER_PUBLISHER"
REG_SUB = "REGISTER_SUBSCRIBER"
REQ_PUB = "REQUEST_PUBLISHERS"
