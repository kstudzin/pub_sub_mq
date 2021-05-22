from Subscriber import Subscriber
from Publisher import Publisher


class Broker:

    def register_pub(self, topic, addr) -> Publisher:
        """Publisher factory"""
        pass

    def register_sub(self, topic, addr) -> Subscriber:
        """Subscriber factory"""
        pass

    def process(self):
        pass


class RoutingBroker(Broker):

    def __init__(self, addr):
        pass

    def register_pub(self, topic, addr) -> Publisher:
        """Creates and returns a publisher with the given address. Saves a subscriber connection."""
        pass

    def register_sub(self, topic, addr) -> Subscriber:
        """Creates and returns a subscriber with the given address. Connects new subscriber to
        broker's bound publish address"""
        pass

    def process(self):
        """Polls for message on incoming connections and routes to subscribers"""
        pass
