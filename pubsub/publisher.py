import logging
import zmq
import pubsub
from pubsub import util


class Publisher:
    ctx = zmq.Context()

    def __init__(self, address, registration_address):
        self.topics = []
        self.message_pub = self.ctx.socket(zmq.PUB)

        self.address = address
        self.message_pub.bind(util.bind_address(self.address))

        self.registration_pub = self.ctx.socket(zmq.PUB)
        self.registration_pub.connect(registration_address)

        logging.info(f"Publisher bound to {self.address}. "
                     f"Registering with broker at {registration_address}.")

    def register(self, topic):
        logging.info(f"Publisher registering for topic {topic} at address {self.address}")

        self.topics.append(topic)
        self.registration_pub.send_string(f"{pubsub.REG_PUB} {topic} {self.address}")

    def publish(self, topic, message):
        """Publishes a message to socket(s)"""
        self.message_pub.send_string(f"{topic} {message}")
