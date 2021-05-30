import datetime
import logging
from collections import defaultdict

import zmq
import pubsub
from pubsub.util import MessageType, PublisherTopicNotRegisteredError


class Publisher:
    """ Publisher for publishing messages

    After registering with a broker, a publisher publishes messages about
    registered topics.

    Sample usage:
    publisher = Publisher("http://127.0.0.1:5555")
    publisher.register("topic1", "http://127.0.0.1:5556")
    publisher.publish("topic1", "message goes here")
    """
    ctx = zmq.Context()

    def __init__(self, address, registration_address):
        """ Creates a publisher instance

        :param registration_address: address of the broker with which this publisher
        registers topics with format <scheme>://<ip_addr>:<port>
        """
        self.address = address
        self.topics = []
        self.message_pub = self.ctx.socket(zmq.PUB)
        self.message_pub.bind(address)

        self.registration_pub = self.ctx.socket(zmq.PUB)
        self.registration_pub.connect(registration_address)

        self.type2sender = {MessageType.STRING: self.message_pub.send_string,
                            MessageType.PYOBJ: self.message_pub.send_pyobj,
                            MessageType.JSON: self.message_pub.send_json}

        logging.info(f"Registering with broker at {registration_address}.")

    def register(self, topic):
        """ Register a topic and address with the broker

        Registering a topic and address tells the broker to expect messages about `topic`
        on `address`. This method must be called before publishing an messages about the
        topic on the address.

        :param topic: a string topic
        :param address: an address string with format <scheme>://<ip_addr>:<port>
        """

        self.topics.append(topic)

        logging.info(f"Publisher registering for topic {topic} at address {self.address}")
        self.registration_pub.send_string(pubsub.REG_PUB, flags=zmq.SNDMORE)
        self.registration_pub.send_string(topic, flags=zmq.SNDMORE)
        self.registration_pub.send_string(self.address)

    def publish(self, topic, message, message_type=MessageType.STRING):
        """ Publishes message with the given topic

        :param topic: the topic of the message to publish, should be a registered string
        :param message: the message to publish
        :param message_type: the type of the message to send. Default = MessageType.STRING
        (valid values are MessageType.STRING, MessageType.PYOBJ, and MessageType.JSON)
        """
        time = datetime.datetime.utcnow()
        if topic not in self.topics:
            raise PublisherTopicNotRegisteredError(topic, self.address)

        print(f"Publishing message: {time} : {topic} : {message}")
        self.message_pub.send_string(topic, flags=zmq.SNDMORE)
        self.message_pub.send_string(message_type, flags=zmq.SNDMORE)
        self.type2sender[message_type](message)


# *****************************************************************************
# *                       Direct Publisher                                    *
# *****************************************************************************


class DirectPublisher:
    ENDPOINT = "tcp://{address}:{port}"

    def __init__(self, topic, address="127.0.0.1", port=5555):
        self.topic = topic
        self.registry = {topic: defaultdict(list)}
        self.callback = None
        self.context = zmq.Context()
        self.message_pub = self.context.socket(zmq.REQ)
        self.location = self.ENDPOINT.format(address=address, port=port)
        self.message_pub.connect(self.location)
        self.register(self.topic, self.location)

        self.type2receiver = {MessageType.STRING: self.message_pub.recv_string,
                              MessageType.PYOBJ: self.message_pub.recv_pyobj,
                              MessageType.JSON: self.message_pub.recv_json}

    def register(self, topic, location):
        location = location if location else self.location
        # todo ensure addresses are unique?
        logging.info(f"Publisher registering for topic {topic} at address {location}")
        self.message_pub.send_string(pubsub.REG_PUB, flags=zmq.SNDMORE)
        self.message_pub.send_string(topic, flags=zmq.SNDMORE)
        self.message_pub.send_string(location)
        self.wait_for_msg()

    def wait_for_msg(self):
        topic = self.message_pub.recv_string()
        logging.info(f"Publisher has registered for topic {topic}")
        # todo compare time to message timestamp?
        message_type = self.message_pub.recv_string()
        message = self.type2receiver[message_type]()
        self.notify(topic, message)

    def notify(self, topic, message):
        self.callback(topic, message)

    def publish(self, topic, message, message_type=MessageType.STRING):
        subscribers = self.registry[topic]
        for subscriber in subscribers:
            time = datetime.datetime.utcnow()
            print(f"Publishing message: {time} : {topic} : {message}")
            self.message_pub.connect(subscriber)
            self.message_pub.send_string(topic, flags=zmq.SNDMORE)
            self.message_pub.send_string(message_type, flags=zmq.SNDMORE)
            self.type2sender[message_type](message)
            reply = self.message_pub.recv_string()
