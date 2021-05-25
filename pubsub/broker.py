import logging
import zmq
from pubsub import util


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
    registration_req = context.socket(zmq.REQ)
    registration_rep = context.socket(zmq.REP)

    poller = zmq.Poller()

    connect_address = None

    topic2socket = {}

    def __init__(self, registration_address):
        self.connect_address = registration_address
        self.registration_req.connect(registration_address)
        self.poller.register(self.registration_rep, zmq.POLLIN)

    def is_server(self):
        bind_address = util.bind_address(self.connect_address)
        self.registration_rep.bind(bind_address)

    def register_pub(self, topic, address):
        """Creates and returns a publisher with the given address. Saves a subscriber connection."""
        self.registration_req.send_string(f"pub {topic} {address}")
        message = self.registration_req.recv()
        print(message)

    def register_sub(self, topic, address):
        """Creates and returns a subscriber with the given address. Connects new subscriber to
        broker's bound publish address"""
        self.registration_req.send_string(f"sub {topic} {address}")
        message = self.registration_req.recv()
        print(message)

    def process(self):
        """Polls for message on incoming connections and routes to subscribers"""
        events = dict(self.poller.poll())
        for socket in events.keys():
            if self.registration_rep == socket:
                message = self.registration_rep.recv()
                self.process_registration(message)
                self.registration_rep.send_string("received")
            else:
                message = socket.recv()
                self.process_message(message)

    def process_registration(self, message):
        reg_type, topic, address = message.decode('utf-8').split()

        if reg_type == "pub":
            socket = self.context.socket(zmq.SUB)
            socket.connect(address)
            socket.setsockopt(zmq.SUBSCRIBE, b"")
            self.poller.register(socket, zmq.POLLIN)
            logging.info(f"Broker subscribed to topic {topic} on address {address}")
        else:
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
