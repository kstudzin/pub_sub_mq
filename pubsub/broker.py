import logging
import zmq
import pubsub
from pubsub import util
from pubsub.util import bind_address


class Broker:

    def process(self):
        pass


class RoutingBroker(Broker):
    context = zmq.Context()

    def __init__(self, registration_address):
        self.registration_sub = self.context.socket(zmq.SUB)
        self.message_in = self.context.socket(zmq.SUB)
        self.message_out = self.context.socket(zmq.PUB)

        self.bound_in = []
        self.bound_out = []

        self.topic2message_out = {}
        self.poller = zmq.Poller()
        self.connect_address = registration_address

        address = util.bind_address(self.connect_address)
        self.registration_sub.bind(address)
        self.registration_sub.setsockopt_string(zmq.SUBSCRIBE, pubsub.REG_PUB)
        self.registration_sub.setsockopt_string(zmq.SUBSCRIBE, pubsub.REG_SUB)

        self.poller.register(self.registration_sub, zmq.POLLIN)
        self.poller.register(self.message_in, zmq.POLLIN)

    def process(self):
        """Polls for message on incoming connections and routes to subscribers"""
        events = dict(self.poller.poll())
        for socket in events.keys():
            logging.debug(f"Processing event")
            if self.registration_sub == socket:
                message = self.registration_sub.recv_multipart()
                logging.info(f"Received message: {message}")
                self.process_registration(message)
            elif self.message_in == socket:
                message = self.message_in.recv_multipart()
                logging.info(f"Received message: {message}")
                self.message_out.send_multipart(message)
            else:
                logging.warning(f"Event on unknown socket {socket}")

    def process_registration(self, message):
        reg_type = message[0].decode('utf-8')
        topic = message[1].decode('utf-8')
        address = message[2].decode('utf-8')

        logging.info(f"Broker processing {reg_type} to topic {topic} at address {address}")

        if reg_type == pubsub.REG_PUB:
            if address not in self.bound_in:
                self.bound_in.append(address)
                self.message_in.bind(bind_address(address))
            self.message_in.setsockopt_string(zmq.SUBSCRIBE, topic)
        elif reg_type == pubsub.REG_SUB:
            if address not in self.bound_out:
                self.bound_out.append(address)
                self.message_out.bind(bind_address(address))

            logging.debug(f"Broker binding subscriber to socket {self.message_out}")
        else:
            logging.warning(f"Received registration message with unknown type: {reg_type}")
