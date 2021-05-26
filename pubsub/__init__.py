import logging
from pubsub.broker import RoutingBroker

broker = RoutingBroker("tcp://localhost:5555")

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(filename="pubsub.log",
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(asctime)s %(name)s %(levelname)-8s %(message)s')
REG_PUB = "REGISTER_PUBLISHER"
REG_SUB = "REGISTER_SUBSCRIBER"