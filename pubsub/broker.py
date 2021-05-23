from urllib.parse import urlparse

import zmq


class Broker:

    def register_pub(self, topic, addr):
        """Publisher factory"""
        pass

    def register_sub(self, topic, addr):
        """Subscriber factory"""
        pass

    def process(self):
        pass


class RoutingBroker(Broker):
    context = zmq.Context()
    registration_req = context.socket(zmq.REQ)
    registration_rep = context.socket(zmq.REP)

    connect_address = None

    def __init__(self, registration_address):
        self.connect_address = registration_address
        self.registration_req.connect(registration_address)

    def is_server(self):
        reg_url = urlparse(self.connect_address)
        bind_address = "{0}://*:{1}".format(reg_url.scheme, reg_url.port)
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
        message = self.registration_rep.recv()
        print(message)
        self.registration_rep.send_string("received")
