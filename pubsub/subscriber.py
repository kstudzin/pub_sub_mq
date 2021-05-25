import logging
import zmq
import pubsub


class Subscriber:
    topics = []
    address = None
    broker = pubsub.broker
    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)

    def __init__(self, address):
        self.address = address
        self.socket.connect(self.address)
        logging.info(f"Subscriber connected to {address}")

    def register(self, topic):
        self.topics.append(topic)
        self.broker.register_sub(topic, self.address)

        logging.info(f"Subscriber subscribing to topic {topic}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def notify(self, topic, message):
        """Receives message"""
        pass

    def wait_for_msg(self):
        topic, message = self.socket.recv_string().split()
        return topic, message
