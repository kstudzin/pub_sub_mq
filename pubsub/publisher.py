import logging
from collections import defaultdict

import zmq
import pubsub
from pubsub.util import MessageType


class Publisher:
    ctx = zmq.Context()

    def __init__(self, registration_address):
        self.topics = defaultdict(set)
        self.message_pub = self.ctx.socket(zmq.PUB)

        self.registration_pub = self.ctx.socket(zmq.PUB)
        self.registration_pub.connect(registration_address)

        self.type2sender = {MessageType.STRING: self.message_pub.send_string,
                            MessageType.PYOBJ: self.message_pub.send_pyobj,
                            MessageType.JSON: self.message_pub.send_json}

        logging.info(f"Registering with broker at {registration_address}.")

    def register(self, topic, address):
        logging.info(f"Publisher registering for topic {topic} at address {address}")

        self.topics[topic].add(address)
        self.message_pub.connect(address)

        self.registration_pub.send_string(pubsub.REG_PUB, flags=zmq.SNDMORE)
        self.registration_pub.send_string(topic, flags=zmq.SNDMORE)
        self.registration_pub.send_string(address)

    def publish(self, topic, message, message_type=MessageType.STRING):
        """Publishes a message to socket(s)"""
        self.message_pub.send_string(topic, flags=zmq.SNDMORE)
        self.message_pub.send_string(message_type, flags=zmq.SNDMORE)
        self.type2sender[message_type](message)
