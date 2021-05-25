import logging
import zmq
from pubsub import util


REG_PUB = "REGISTER_PUBLISHER"
REG_SUB = "REGISTER_SUBSCRIBER"

class Broker:

    def register_pub(self, topic, address):
        """Publisher factory"""
        pass

    def register_sub(self, topic, address):
        """Subscriber factory"""
        pass

    def process(self):
        pass


class RoutingBroker(Broker):
    context = zmq.Context()
    registration_pub = context.socket(zmq.PUB)
    registration_sub = context.socket(zmq.SUB)

    poller = zmq.Poller()

    connect_address = None

    topic2socket = {}

    def __init__(self, registration_address):
        self.connect_address = registration_address
        self.registration_pub.connect(registration_address)

    def is_server(self):
        bind_address = util.bind_address(self.connect_address)
        self.registration_sub.bind(bind_address)
        self.registration_sub.setsockopt_string(zmq.SUBSCRIBE, REG_PUB)
        self.registration_sub.setsockopt_string(zmq.SUBSCRIBE, REG_SUB)
        self.poller.register(self.registration_sub, zmq.POLLIN)

    def register_pub(self, topic, address):
        """Creates and returns a publisher with the given address. Saves a subscriber connection."""
        logging.info(f"Broker registering publisher for topic {topic} at address {address}")
        self.registration_pub.send_string(f"{REG_PUB} {topic} {address}")

    def register_sub(self, topic, address):
        """Creates and returns a subscriber with the given address. Connects new subscriber to
        broker's bound publish address"""
        logging.info(f"Broker registering subscriber for topic {topic} at address {address}")
        self.registration_pub.send_string(f"{REG_SUB} {topic} {address}")

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

        if reg_type == REG_PUB:
            socket = self.context.socket(zmq.SUB)
            socket.connect(address)
            socket.setsockopt(zmq.SUBSCRIBE, b"")
            self.poller.register(socket, zmq.POLLIN)
            logging.info(f"Broker subscribed to topic {topic} on address {address}")
        elif reg_type == REG_SUB:
            if topic in self.topic2socket:
                socket = self.topic2socket[topic]
            else:
                socket = self.context.socket(zmq.PUB)
                self.topic2socket[topic] = socket

            bind_address = util.bind_address(address)
            socket.bind(bind_address)
            logging.info(f"Broker publishing topic {topic} on address {bind_address}. (socket {socket})")

    def process_message(self, message):
        decoded = message.decode('utf-8')
        logging.info(f"Broker received message: {decoded}")

        topic, value = decoded.split()
        socket = self.topic2socket[topic]

        logging.info(f"Broker Sending message on topic {topic} to socket {socket}")
        socket.send_string(decoded)
