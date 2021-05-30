import logging
from collections import defaultdict

import zmq
import pubsub
from pubsub.util import MessageType, SubscriberTopicNotRegisteredError


def printing_callback(topic, message):
    print(f"Topic: {topic}, Message: {message}")


class Subscriber:
    """ Subscriber for subscribing to messages

    After registering with a broker, a subscriber notifies an application
    when it receives messages on registered topics.

    Sample usage:
    subscriber = Subscriber("http://127.0.0.1:5555"")
    subscriber.register("topic1", "http://127.0.0.1:5557")
    subscriber.register_callback(callback_name)
    subscriber.wait_for_msg()

    The code above should be running in a thread, the application will supply the
    code the notify the application through the registered callback
    """
    ctx = zmq.Context()

    def __init__(self, address, registration_address):
        """Creates a subscriber instance

        :param registration_address: address of the broker with which this publisher
        registers topics with format <scheme>://<ip_addr>:<port>
        """
        self.address = address
        self.topics = []
        self.callback = printing_callback
        self.message_sub = self.ctx.socket(zmq.SUB)
        self.message_sub.connect(address)

        self.registration_pub = self.ctx.socket(zmq.PUB)
        self.registration_pub.connect(registration_address)

        self.type2receiver = {MessageType.STRING: self.message_sub.recv_string,
                              MessageType.PYOBJ: self.message_sub.recv_pyobj,
                              MessageType.JSON: self.message_sub.recv_json}

        logging.info(f"Registering with broker at {registration_address}.")

    def register(self, topic):
        """ Registers a topic and address with the broker

        Registering a topic and address tells the broker to send messages about `topic`
        to `address`. This method must be called before any messages about the topic
        will be received.

        :param topic: a string topic
        :param address: an address string with format <scheme>://<ip_addr>:<port>
        """
        logging.info(f"Subscriber registering to topic {topic} at address {self.address}")

        self.topics.append(topic)

        self.registration_pub.send_string(pubsub.REG_SUB, flags=zmq.SNDMORE)
        self.registration_pub.send_string(topic, flags=zmq.SNDMORE)
        self.registration_pub.send_string(self.address)

        self.message_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

    def unregister(self, topic):
        """ Unregisters a topic and address

        Unregistering a topic and address prevents the subscriber from receiving any
        further notifications about topic on the given address.

        :param topic: a string topic that has been registered
        :param address: an address string with format <scheme>://<ip_addr>:<port> that
        has been registered
        """
        if topic not in self.topics:
            raise SubscriberTopicNotRegisteredError(topic, self.address)

        self.topics.remove(topic)
        self.message_sub.setsockopt_string(zmq.UNSUBSCRIBE, topic)

        # For now, we won't worry about unbinding the address on the broker
        # There could be other subscribers listening to that topic. Because
        # we've disconnected the address and unsubscribed from the topic here,
        # we shouldn't get those messages, which is the main concern.

    def notify(self, topic, message):
        """ Notifies the application that a message has been received

        Notify is implemented by the user through registering a callback

        :param topic: the string topic of the message
        :param message: the message content
        """
        self.callback(topic, message)

    def wait_for_msg(self):
        """ Waits for a message to be received

        Block until a message has been received and then invoke the callback to
        notify the application code.
        """
        topic = self.message_sub.recv_string()
        message_type = self.message_sub.recv_string()
        message = self.type2receiver[message_type]()
        self.notify(topic, message)

    def register_callback(self, callback):
        """ Register the call back to notify the application of a message

        Accepts a function or method to be called when a message is received. The
        callback should accept two arguments, the topic and the message, and handle
        that information appropriately

        The default callback is `printing_callback` which prints the topic and
        message to stdout

        :param callback: the function or method to call when a message is received
        """
        self.callback = callback

# *****************************************************************************
# *                       Direct Subscriber                                   *
# *****************************************************************************


class DirectSubscriber:
    ENDPOINT = "tcp://{address}:{port}"

    def __init__(self, topic, address="127.0.0.1", port="5556"):
        self.topic = topic
        self.topics = [topic]
        self.callback = printing_callback
        self.context = zmq.Context()
        self.message_sub = self.context.socket(zmq.REP)
        self.ipaddress = self.ENDPOINT.format(address=address, port=port)
        self.message_sub.bind(self.ipaddress)
        self.register(self.topic)

        self.type2receiver = {MessageType.STRING: self.message_sub.recv_string,
                              MessageType.PYOBJ: self.message_sub.recv_pyobj,
                              MessageType.JSON: self.message_sub.recv_json}

    def register(self, topic):
        handshake_socket = self.context.socket(zmq.REQ)
        location = self.ENDPOINT.format(address="127.0.0.1", port="5555")
        handshake_socket.connect(location)
        # todo ensure addresses are unique?
        logging.info(f"Subscriber registering to topic {topic} at address {location}")
        handshake_socket.send_string(pubsub.REG_SUB, flags=zmq.SNDMORE)
        handshake_socket.send_string(topic, flags=zmq.SNDMORE)
        handshake_socket.send_string(location)

    def unregister(self, topic):
        if topic not in self.topics:
            raise SubscriberTopicNotRegisteredError(topic, self.address)

        self.topics.remove(topic)
        # todo remove subscriber from publisher

    def wait_for_msg(self):
        topic = self.message_sub.recv_string()
        logging.info(f"Subscriber has registered for topic {topic}")
        # todo compare time to message timestamp?
        message_type = self.message_sub.recv_string()
        message = self.type2receiver[message_type]()
        self.notify(topic, message)

    def notify(self, topic, message):
        self.callback(topic, message)
