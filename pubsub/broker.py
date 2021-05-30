import logging
import zmq
import pubsub
from pubsub import util


class BrokerType:
    DIRECT = "DIRECT"
    ROUTE = "ROUTE"


class Broker:

    def process_registration(self):
        pass


class RoutingBroker(Broker):
    """ Routing Broker implementation handles the routing of messages

    The Routing Broker contains the following sockets:
    - A socket that subscribes to registration messages
    - Sockets that listen for incoming messages from publishers
    - A socket that publishes received messages to subscribers

    There are two key events that happen that this broker must respond to
    - Registration messages from publishers and subscribers
    - Receiving messages from publishers to route to subscribers

    """
    context = zmq.Context()

    def __init__(self, registration_address):
        """ Creates a routing broker instance

        :param registration_address: the address to use by this broker for publishers
        and subscribers to register with. Format: <scheme>://<ip_addr>:<port>
        """
        self.registration = self.context.socket(zmq.REP)
        self.message_in = self.context.socket(zmq.SUB)
        self.message_out = self.context.socket(zmq.PUB)

        self.topic2message_out = {}

        self.connect_address = registration_address
        self.registration.bind(registration_address)

    def process(self):
        """Polls for incoming messages

        Messages may be registration messages or publications.
        """
        message = self.message_in.recv_multipart()
        logging.info(f"Received message: {message}")

        self.message_out.send_multipart(message)

    def process_registration(self):
        """ Process registration messages

        Blocks until a registration message is received. Once received, performs
        operations so that this broker can receive publications from or send
        publications to the appropriate address

        Each registration message consists of 3 string parts:
        - registration type: string with value REGISTER_PUB or REGISTER_SUB
        - a topic that it wants to send or receive
        - an address to receive publications from or send publications to
        """
        message = self.registration.recv_multipart()

        reg_type = message[0].decode('utf-8')
        topic = message[1].decode('utf-8')
        address = message[2].decode('utf-8')

        logging.info(f"Broker processing {reg_type} to topic {topic} at address {address}")

        if reg_type == pubsub.REG_PUB:
            self.message_in.connect(address)
            self.message_in.setsockopt_string(zmq.SUBSCRIBE, topic)
        elif reg_type == pubsub.REG_SUB:
            self.message_out.connect(address)
        else:
            logging.warning(f"Received registration message with unknown type: {reg_type}")

        self.registration.send_string(BrokerType.ROUTE)
