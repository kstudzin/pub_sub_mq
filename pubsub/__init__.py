import logging


logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(filename="pubsub.log",
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

REG_PUB = "REGISTER_PUBLISHER"
REG_SUB = "REGISTER_SUBSCRIBER"
REQ_PUB = "REQUEST_PUBLISHERS"
