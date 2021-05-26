import logging
import zmq
import pubsub
from pubsub import util


def printing_callback(topic, message):
    print(f"Topic: {topic}, Message: {message}")


class Subscriber:
    topics = []
    address = None
    broker = pubsub.broker
    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)

    def __init__(self, address):
        self.callback = printing_callback

        self.address = address
        self.socket.bind(util.bind_address(address))
        logging.info(f"Subscriber connected to {address}")

    def register(self, topic):
        self.topics.append(topic)
        self.broker.register_sub(topic, self.address)

        logging.info(f"Subscriber subscribing to topic {topic}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def notify(self, topic, message):
        """Receives message"""
        self.callback(topic, message)

    def wait_for_msg(self):
        topic, message = self.socket.recv_string().split()
        self.notify(topic, message)

    def register_callback(self, callback):
        self.callback = callback
