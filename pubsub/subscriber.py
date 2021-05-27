import logging
import zmq
import pubsub
from pubsub import util
from pubsub.util import MessageType


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

        self.type2receiver = {MessageType.STRING: self.message_sub.recv_string,
                              MessageType.PYOBJ: self.message_sub.recv_pyobj,
                              MessageType.JSON: self.message_sub.recv_json}

        logging.info(f"Subscriber bound to {address}. "
                     f"Registering with broker at {registration_address}.")

    def register(self, topic):
        logging.info(f"Subscriber registering to topic {topic} at address {self.address}")

        self.topics.append(topic)

        self.registration_pub.send_string(pubsub.REG_SUB, flags=zmq.SNDMORE)
        self.registration_pub.send_string(topic, flags=zmq.SNDMORE)
        self.registration_pub.send_string(self.address)

        self.message_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

    def notify(self, topic, message):
        """Receives message"""
        self.callback(topic, message)

    def wait_for_msg(self):
        topic = self.message_sub.recv_string()
        message_type = self.message_sub.recv_string()
        message = self.type2receiver[message_type]()
        self.notify(topic, message)

    def register_callback(self, callback):
        self.callback = callback
