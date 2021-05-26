import logging
import zmq
import pubsub
from pubsub import util


def printing_callback(topic, message):
    print(f"Topic: {topic}, Message: {message}")


class Subscriber:
    ctx = zmq.Context()

    def __init__(self, address, registration_address):
        self.topics = []
        self.callback = printing_callback
        self.message_sub = self.ctx.socket(zmq.SUB)

        self.address = address
        self.message_sub.bind(util.bind_address(address))

        self.registration_pub = self.ctx.socket(zmq.PUB)
        self.registration_pub.connect(registration_address)

        logging.info(f"Subscriber bound to {address}. "
                     f"Registering with broker at {registration_address}.")

    def register(self, topic):
        logging.info(f"Subscriber subscribing to topic {topic} at address {self.address}")

        self.topics.append(topic)
        self.registration_pub.send_string(f"{pubsub.REG_SUB} {topic} {self.address}")

        self.message_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

    def notify(self, topic, message):
        """Receives message"""
        self.callback(topic, message)

    def wait_for_msg(self):
        topic, message = self.message_sub.recv_string().split()
        self.notify(topic, message)

    def register_callback(self, callback):
        self.callback = callback
