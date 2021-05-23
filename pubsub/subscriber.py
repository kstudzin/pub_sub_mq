import psserver
from pubsub.broker import RoutingBroker


class Subscriber:
    topic = None
    address = None
    broker = psserver.broker

    def __init__(self, topic, address):
        self.topic = topic
        self.address = address
        self.broker.register_sub(topic, address)

    def notify(self, topic, message):
        """Receives message"""
        pass

    def wait_for_msg(self):
        pass
