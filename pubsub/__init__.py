import logging
from pubsub.broker import RoutingBroker

broker = RoutingBroker("tcp://localhost:5555")

logging.basicConfig(filename="pubsub.log",  level=logging.DEBUG)
