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

    poller = zmq.Poller()

    connect_address = None

    topic2socket = {}

    def __init__(self, registration_address):
        self.connect_address = registration_address
        self.registration_req.connect(registration_address)
        self.poller.register(self.registration_rep, zmq.POLLIN)

    def is_server(self):
        bind_address = self.bind_address(self.connect_address)
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
                reg_type, topic, address = self.registration_rep.recv().split()

                if reg_type == "pub":
                    socket = self.context.socket(zmq.SUB)
                    socket.connect(address)
                    socket.setsockopt(zmq.SUBSCRIBE, b"")
                    self.poller.register(socket, zmq.POLLIN)
                else:
                    bind_address = self.bind_address(address.decode('utf-8'))
                    if topic in self.topic2socket:
                        socket = self.topic2socket[topic]
                        socket.bind(bind_address)
                    else:
                        socket = self.context.socket(zmq.PUB)
                        socket.bind(bind_address)
                        self.topic2socket[topic] = socket

                self.registration_rep.send_string("received")

    @staticmethod
    def bind_address(address):
        bind_url = urlparse(address)
        return "{0}://*:{1}".format(bind_url.scheme, bind_url.port)
