import logging
import zmq
import pubsub
from pubsub import util


class Publisher:
    topics = []
    address = None
    broker = pubsub.broker
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)

    def __init__(self, address):
        self.address = address
        bind_address = util.bind_address(self.address)
        self.socket.bind(bind_address)
        logging.info(f"Publisher bound to {bind_address}")

    def register(self, topic):
        self.topics.append(topic)
        self.broker.register_pub(topic, self.address)

    def publish(self, topic, message):
        """Publishes a message to socket(s)"""
        self.socket.send_string(f"{topic} {message}")
