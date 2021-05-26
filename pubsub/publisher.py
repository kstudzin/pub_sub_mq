import logging
import zmq
import pubsub
from pubsub import util


class Publisher:
    broker = pubsub.broker
    ctx = zmq.Context()

    def __init__(self, address):
        self.topics = []
        self.socket = self.ctx.socket(zmq.PUB)

        self.address = address
        self.socket.bind(util.bind_address(self.address))
        logging.info(f"Publisher bound to {self.address}")

    def register(self, topic):
        self.topics.append(topic)
        self.broker.register_pub(topic, self.address)

    def publish(self, topic, message):
        """Publishes a message to socket(s)"""
        self.socket.send_string(f"{topic} {message}")
