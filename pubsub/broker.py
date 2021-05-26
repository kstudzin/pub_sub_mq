import logging
import zmq
import pubsub
from pubsub import util


class Broker:

    def process(self):
        pass


class RoutingBroker(Broker):
    context = zmq.Context()

    def __init__(self, registration_address):
        self.registration_sub = self.context.socket(zmq.SUB)
        self.message_in = self.context.socket(zmq.SUB)

        self.topic2message_out = {}
        self.poller = zmq.Poller()
        self.connect_address = registration_address

        bind_address = util.bind_address(self.connect_address)
        self.registration_sub.bind(bind_address)
        self.registration_sub.setsockopt_string(zmq.SUBSCRIBE, pubsub.REG_PUB)
        self.registration_sub.setsockopt_string(zmq.SUBSCRIBE, pubsub.REG_SUB)

        self.poller.register(self.registration_sub, zmq.POLLIN)
        self.poller.register(self.message_in, zmq.POLLIN)

    def process(self):
        """Polls for message on incoming connections and routes to subscribers"""
        events = dict(self.poller.poll())
        for socket in events.keys():
            if self.registration_sub == socket:
                message = self.registration_sub.recv()
                self.process_registration(message)
            else:
                message = socket.recv()
                self.process_message(message)

    def process_registration(self, message):
        reg_type, topic, address = message.decode('utf-8').split()
        logging.info(f"Broker processing {reg_type} to topic {topic} at address {address}")

        if reg_type == pubsub.REG_PUB:
            self.message_in.connect(address)
            self.message_in.setsockopt_string(zmq.SUBSCRIBE, topic)
        elif reg_type == pubsub.REG_SUB:

            if topic in self.topic2message_out:
                socket = self.topic2message_out[topic]
            else:
                socket = self.context.socket(zmq.PUB)
                self.topic2message_out[topic] = socket

            logging.debug(f"Broker binding subscriber to socket {socket}")
            socket.connect(address)

    def process_message(self, message):
        decoded = message.decode('utf-8')
        logging.info(f"Broker received message: {decoded}")

        topic, value = decoded.split()
        if topic in self.topic2message_out.keys():
            socket = self.topic2message_out[topic]

            logging.info(f"Broker Sending message on topic {topic} to socket {socket}")
            socket.send_string(decoded)
        else:
            logging.info(f"No subscribers listening for topic: {topic}")
