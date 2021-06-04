import logging
from abc import abstractmethod, ABC
from collections import defaultdict
from time import sleep

import zmq
import pubsub


class BrokerType:
    DIRECT = "DIRECT"
    ROUTE = "ROUTE"


class AbstractBroker(ABC):
    """ Broker for abstracting pub/sub address

    The broker abstracts addresses by requiring publishers and subscribers
    to first register with it. It is assumed that the address of the broker
    is well-known to all publishers and subscribers.
    """
    context = zmq.Context()

    def __init__(self, registration_address, conn_sec=.5):
        self.conn_sec = conn_sec
        self.registration = self.context.socket(zmq.REP)

        self.connect_address = registration_address
        self.registration.bind(registration_address)

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

        logging.info(f"Broker processing {reg_type} to topic \"{topic}\" at address {address}")

        if reg_type == pubsub.REG_PUB:
            self.process_pub_registration(topic, address)
        elif reg_type == pubsub.REG_SUB:
            sleep(self.conn_sec)
            self.process_sub_registration(topic, address)
        else:
            logging.warning(f"Received registration message with unknown type: {reg_type}")

    @abstractmethod
    def process_pub_registration(self, topic, address):
        pass

    @abstractmethod
    def process_sub_registration(self, topic, address):
        pass


class RoutingBroker(AbstractBroker):
    """ Routing Broker implementation handles the routing of messages

    The Routing Broker contains the following sockets:
    - A socket that listen for incoming messages from publishers
    - A socket that publishes received messages to subscribers

    (These are in addition to the registration socket in the super class)

    There are two key events that happen that this broker must respond to
    - Registration messages from publishers and subscribers
    - Receiving messages from publishers to route to subscribers

    There is a method to process each of these events that must be run in
    loops in threads

    """

    def __init__(self, registration_address):
        """ Creates a routing broker instance

        :param registration_address: the address to use by this broker for publishers
        and subscribers to register with. Format: <scheme>://<ip_addr>:<port>
        """
        super().__init__(registration_address)
        self.message_in = self.context.socket(zmq.SUB)
        self.message_out = self.context.socket(zmq.PUB)

    def process(self):
        """ Process messages

        Receives messages from publishers and publishes
        messages to subscribers
        """
        logging.debug("Waiting to process message...")
        message = self.message_in.recv_multipart()
        logging.info(f"Received message: {message}")

        self.message_out.send_multipart(message)

    def process_pub_registration(self, topic, address):
        # Connect address to message receiving socket and
        # subscribe to topic
        self.message_in.connect(address)
        self.message_in.setsockopt_string(zmq.SUBSCRIBE, topic)

        # Complete registration with reply containing broker type
        self.registration.send_string(BrokerType.ROUTE)
        logging.debug(f"Connected to publisher at {address} for topic \"{topic}\"")

    def process_sub_registration(self, topic, address):
        # Connect the message sending socket to the new
        # subscriber
        self.message_out.connect(address)

        # Complete registration with reply containing broker type
        self.registration.send_string(BrokerType.ROUTE)
        logging.debug(f"Connected to subscriber at \"{address}\"")


class DirectBroker(AbstractBroker):

    def __init__(self, registration_address):
        # call super class constructor
        super().__init__(registration_address)

        # add data structure that maps a topic to a list of
        # publisher addresses publishing on that topic
        self.registry = defaultdict(list)

        # add socket that can publish newly registered publishers
        # to registered subscribers
        self.message_out = self.context.socket(zmq.PUB)
        logging.info(f"Created direct broker at {registration_address}")

    def process_pub_registration(self, topic, address):
        # add publisher to map of topics to addresses
        encoded_address = address.encode('utf-8')
        self.registry[topic].append(encoded_address)

        # publish topic and address of new publisher to subscribers
        self.message_out.send_string(topic, flags=zmq.SNDMORE)
        self.message_out.send_string(address)

        # Send broker type reply
        self.registration.send_string(BrokerType.DIRECT)

    def process_sub_registration(self, topic, address):
        # connect subscriber address to socket that publishes new
        # publisher connection information
        self.message_out.connect(address)

        # send multipart message with broker type, number of addresses
        # being sent, and a list of addresses
        self.registration.send_string(BrokerType.DIRECT, zmq.SNDMORE)
        self.registration.send_string(str(len(self.registry[topic])), zmq.SNDMORE)
        has_addresses = b'\x00' if len(self.registry[topic]) == 0 else b'\x01'
        messages = [has_addresses] + self.registry[topic]

        self.registration.send_multipart(messages)
