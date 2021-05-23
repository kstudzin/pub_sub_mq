import psserver
from pubsub.broker import RoutingBroker


class Publisher:
    topic = None
    address = None
    broker = psserver.broker

    def __init__(self, topic, address):
        self.topic = topic
        self.address = address
        self.broker.register_pub(topic, address)

    def publish(self, topic, message):
        """Publishes a message to socket(s)"""
        pass
