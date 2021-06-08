import logging
default_formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
perf_formatter = logging.Formatter('%(message)s')


def setup_logger(name, log_file, formatter, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


LOGGER = setup_logger('app_logger', 'pubsub.log', default_formatter)
PERF_LOGGER = setup_logger('message_logger', 'pubsub_perf.log', perf_formatter)

REG_PUB = "REGISTER_PUBLISHER"
REG_SUB = "REGISTER_SUBSCRIBER"
