import logging
from abc import abstractmethod, ABC
from collections import defaultdict
import zmq
import pubsub
from pubsub import APP_LOGGER


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

    def __init__(self, registration_address):
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

        APP_LOGGER.info(f"Broker processing {reg_type} to topic \"{topic}\" at address {address}")

        if reg_type == pubsub.REG_PUB:
            self.process_pub_registration(topic, address)
        elif reg_type == pubsub.REG_SUB:
            self.process_sub_registration(topic, address)
        else:
            APP_LOGGER.warning(f"Received registration message with unknown type: {reg_type}")

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

        :param str registration_address: the address to use by this broker for publishers
            and subscribers to register with Format: <scheme>://<ip_addr>:<port>
        """
        super().__init__(registration_address)
        self.message_in = self.context.socket(zmq.SUB)
        self.message_out = self.context.socket(zmq.PUB)

    def process(self):
        """ Process messages

        Receives messages from publishers and publishes
        messages to subscribers
        """
        APP_LOGGER.debug("Waiting to process message...")
        message = self.message_in.recv_multipart()
        APP_LOGGER.info(f"Received message: {message}")

        self.message_out.send_multipart(message)

    def process_pub_registration(self, topic, address):
        """
        Connect publisher address to message receiving socket and subscribe to topic.
        A reply is then sent to the publisher with the type of the broker configuration.

        :param str topic: A string containing a topic the publisher will publish.
        :param str address: The publishers address Format: <scheme>://<ip_addr>:<port>
        """
        self.message_in.connect(address)
        self.message_in.setsockopt_string(zmq.SUBSCRIBE, topic)

        self.registration.send_string(BrokerType.ROUTE)
        APP_LOGGER.debug(f"Connected to publisher at {address} for topic \"{topic}\"")

    def process_sub_registration(self, topic, address):
        """
        Connect the message sending socket to the new subscriber and
        reply to the subscriber with the type of the broker configuration.

        :param str topic: A string containing a registration topic from the subscriber.
        :param str address: The subscribers address Format: <scheme>://<ip_addr>:<port>
        """
        self.message_out.connect(address)

        self.registration.send_string(BrokerType.ROUTE)
        logging.debug(f"Connected to subscriber at \"{address}\"")


class DirectBroker(AbstractBroker):
    """ Direct Broker implementation handles creating a record of publishers
    for each topic. This enables subscribers to create a direct connection to all of
    the publishers for which they choose to subscribe.

    The Direct Broker contains the following socket:
    - A socket that publishes received publisher registration to all subscribers.

    (This is in addition to the registration socket in the super class)

    The Direct Broker contains a registration dictionary that keeps a
    record of all topics with a list of all publishers addresses for that topic.

    There are two key events that happen that this broker must respond to
    - Registration messages from publishers and those from subscribers

    There is a method to process each of these events that must be run in
    loops in threads

    """
    def __init__(self, registration_address):
        """ Creates a direct broker instance with a dictionary to record all
        registered topics and a list of the publisher's for each topic. A socket
        is then created to publish newly registered publishers to the existing subscribers.

        :param str registration_address: the address to use by this broker for publishers
            and subscribers to register. Format: <scheme>://<ip_addr>:<port>
        """
        super().__init__(registration_address)

        self.registry = defaultdict(list)

        self.message_out = self.context.socket(zmq.PUB)
        APP_LOGGER.info(f"Created direct broker at {registration_address}")

    def process_pub_registration(self, topic, address):
        """
        Adds the publisher to the brokers registry table and then sends
        the publisher's topic and address to all subscribers. The broker then
        sends a reply to the publisher with the broker's type(DIRECT).

        :param str topic: A string containing a topic the publisher will publish.
        :param str address: The publishers address Format: <scheme>://<ip_addr>:<port>
        """
        encoded_address = address.encode('utf-8')
        self.registry[topic].append(encoded_address)

        self.message_out.send_string(topic, flags=zmq.SNDMORE)
        self.message_out.send_string(address)

        self.registration.send_string(BrokerType.DIRECT)

    def process_sub_registration(self, topic, address):
        """
        Creates a connection to the subscriber that will publish new
        publisher registration information. The broker then sends a reply
        to the publisher with the broker's type(DIRECT) and if present,
        a list of addresses for that `topic`.

        :param str topic: A string containing the topic a subscriber is registering.
        :param str address: The publishers address Format: <scheme>://<ip_addr>:<port>
        """
        self.message_out.connect(address)

        self.registration.send_string(BrokerType.DIRECT, zmq.SNDMORE)
        has_addresses = b'\x00' if len(self.registry[topic]) == 0 else b'\x01'
        messages = [has_addresses] + self.registry[topic]

        self.registration.send_multipart(messages)
