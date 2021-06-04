import logging
from collections import defaultdict
from datetime import datetime
from time import sleep

import zmq
import pubsub
from pubsub.broker import BrokerType
from pubsub.util import MessageType, TopicNotRegisteredError


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

    def __init__(self, address, registration_address, conn_sec=.5):
        """Creates a subscriber instance

        :param address: the address of this subscriber. String with
        format <scheme>://<ip_addr>:<port>
        :param registration_address: address of the broker with which this publisher
        registers topics. String with format <scheme>://<ip_addr>:<port>
        :param conn_sec: the number of seconds it takes this subscriber to
        connect to a publisher when using a direct broker. Optional. Default is .5 seconds
        """
        self.conn_sec = conn_sec
        self.address = address
        self.topics = []
        self.callback = printing_callback

        # The message sub socket receives messages. If using the
        # ROUTING broker it is bound to the address of this subscriber.
        # If using the DIRECT broker it will be connected directly to the
        # publisher address.
        self.message_sub = self.ctx.socket(zmq.SUB)

        # create socket that will subscribe to new publisher information
        # This socket will only be used with the DIRECT router. When it is
        # used it will be be bound to this subscribers address
        self.publisher_sub = self.ctx.socket(zmq.SUB)

        # Bind the address here to force the construction to fail if the address
        # is already bound. However if the broker is a ROUTING broker, we will need
        # to bind to the message subscriber. In that case, we will unbind this socket
        # and bind to the other once we know which subscriber we are using (in the
        # register method. To make sure that we only make that switch once, we use
        # the message_sub_bound flag
        self.publisher_sub.bind(self.address)
        self.message_sub_bound = False

        # move this bind
        # Because either this socket or the publisher registration notification
        # socket will be bound to this subscriber address, we cannot bind either
        # until we know which broker we are using. Luckily, the reply from the
        # registration request tells us which broker type is being used

        # add address bound flag
        # An address can only be bound once. Because we need to bind the address
        # in a place that will be called more than once, we can add a flag here
        # that gets switched once the address has been bound.

        self.registration = self.ctx.socket(zmq.REQ)
        self.registration.connect(registration_address)

        self.type2receiver = {MessageType.STRING: self.message_sub.recv_string,
                              MessageType.PYOBJ: self.message_sub.recv_pyobj,
                              MessageType.JSON: self.message_sub.recv_json}

        logging.info(f"Bound to {address}. Registering with broker at {registration_address}.")

    def register(self, topic):
        """ Registers a topic and address with the broker

        Registering a topic tells the broker to send messages about `topic` to this
        subscriber. This method must be called before any messages about the topic
        will be received.

        :param topic: a string topic
        """
        logging.info(f"Subscriber registering to topic {topic} at address {self.address}")

        self.topics.append(topic)

        self.registration.send_string(pubsub.REG_SUB, flags=zmq.SNDMORE)
        self.registration.send_string(topic, flags=zmq.SNDMORE)
        self.registration.send_string(self.address)

        self.message_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

        # socket listening for new publishers should also subscribe to the topic
        # This allows it to only receive notifications about publishers it wants to
        # connect to
        self.publisher_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

        broker_type = self.registration.recv_string()

        # process response from registration
        # If broker is ROUTING we need to the socket accepting messages to be bound
        # to this subscriber's address
        # If broker is DIRECT we need to connect the socket accepting messages to
        # each address received. Additionally, if we are using the DIRECT broker
        # we need to be able to receive notifications about new publishers so
        # we need to connect the appropriate socket to this subscriber's address
        if broker_type == BrokerType.ROUTE:
            if not self.message_sub_bound:
                self.publisher_sub.unbind(self.address)
                self.message_sub.bind(self.address)
                self.message_sub_bound = True
        elif broker_type == BrokerType.DIRECT:

            # Ensure that publisher_sub is receiving new publishers
            # before we get the list of existing publishers otherwise
            # we could miss a publisher registration
            sleep(self.conn_sec)

            self.registration.send_string(pubsub.REQ_PUB, flags=zmq.SNDMORE)
            self.registration.send_string(topic, flags=zmq.SNDMORE)
            self.registration.send_string(self.address)

            has_addresses = self.registration.recv()
            if has_addresses == b'\x01':
                addresses = self.registration.recv_multipart()
                for address in addresses:
                    self.message_sub.connect(address.decode('utf-8'))

        logging.info(f"Connected to {broker_type} broker")

    def unregister(self, topic):
        """ Unregisters a topic and address

        Unregistering a topic prevents the subscriber from receiving any
        further notifications about topic.

        :param topic: a string topic that has been registered
        """
        if topic not in self.topics:
            raise TopicNotRegisteredError(topic, self.address, "Topic has not been registered with subscriber. Cannot "
                                                               "unregister.")

        self.topics.remove(topic)
        self.message_sub.setsockopt_string(zmq.UNSUBSCRIBE, topic)

        # unsubscribe registration socket
        self.publisher_sub.setsockopt_string(zmq.UNSUBSCRIBE, topic)
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
        time_out = datetime.strptime(self.message_sub.recv_string(), "%m/%d/%Y, %H:%M:%S")
        message_type = self.message_sub.recv_string()
        message = self.type2receiver[message_type]()
        time_in = datetime.utcnow()
        delta_time = time_in - time_out
        logging.info(f"Transit delta: {delta_time} with topic size: {len(topic)} and message size: {len(message)}")
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

    def wait_for_registration(self):
        """ Waits for a registration to be published

        Blocks until a registration has been received and then connects the
        subscriber so that it can begin receiving messages on that address
        """
        # receive notification of new publisher
        message = self.publisher_sub.recv_multipart()
        address = message[1].decode('utf-8')

        # connect message receiving socket to new publisher address
        self.message_sub.connect(address)

