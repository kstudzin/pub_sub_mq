import logging
from collections import defaultdict

import zmq
import pubsub
from pubsub.util import MessageType


def printing_callback(topic, message):
    print(f"Topic: {topic}, Message: {message}")


class Subscriber:
    ctx = zmq.Context()

    def __init__(self, registration_address):
        self.topics = defaultdict(set)
        self.addresses = defaultdict(set)
        self.callback = printing_callback
        self.message_sub = self.ctx.socket(zmq.SUB)

        self.registration_pub = self.ctx.socket(zmq.PUB)
        self.registration_pub.connect(registration_address)

        self.type2receiver = {MessageType.STRING: self.message_sub.recv_string,
                              MessageType.PYOBJ: self.message_sub.recv_pyobj,
                              MessageType.JSON: self.message_sub.recv_json}

        logging.info(f"Registering with broker at {registration_address}.")

    def register(self, topic, address):
        logging.info(f"Subscriber registering to topic {topic} at address {address}")

        self.topics[topic].add(address)
        self.addresses[address].add(topic)
        self.message_sub.connect(address)

        self.registration_pub.send_string(pubsub.REG_SUB, flags=zmq.SNDMORE)
        self.registration_pub.send_string(topic, flags=zmq.SNDMORE)
        self.registration_pub.send_string(address)

        self.message_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

    def unregister(self, topic, address):
        if address in self.topics[topic]:
            self.topics[topic].remove(address)

            if len(self.topics[topic]) == 0:
                self.message_sub.setsockopt_string(zmq.UNSUBSCRIBE, topic)

        if topic in self.addresses[address]:
            self.addresses[address].remove(topic)

            if len(self.addresses[address]) == 0:
                self.message_sub.disconnect(address)

        # For now, we won't worry about unbinding the address on the broker
        # There could be other subscribers listening to that topic. Because
        # we've disconnected the address and unsubscribed from the topic here,
        # we shouldn't get those messages, which is the main concern.

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
