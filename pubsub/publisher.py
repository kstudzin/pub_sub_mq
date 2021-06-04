from datetime import datetime
import zmq
import pubsub
from pubsub import APP_LOGGER
from pubsub.util import MessageType, TopicNotRegisteredError


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

        :param address: the address of this publisher. String with format <scheme>://<ip_addr>:<port>
        :param registration_address: address of the broker with which this publisher
        registers topics. String with format <scheme>://<ip_addr>:<port>
        """
        self.address = address
        self.topics = []
        self.message_pub = self.ctx.socket(zmq.PUB)
        self.message_pub.bind(address)

        self.registration = self.ctx.socket(zmq.REQ)
        self.registration.connect(registration_address)

        self.type2sender = {MessageType.STRING: self.message_pub.send_string,
                            MessageType.PYOBJ: self.message_pub.send_pyobj,
                            MessageType.JSON: self.message_pub.send_json}

        APP_LOGGER.info(f"Bound to {address}. Registering with broker at {registration_address}.")

    def register(self, topic):
        """ Register a topic and address with the broker

        Registering a topic tells the broker to expect messages about `topic`
        to be published by this publisher. This method must be called before publishing
        an messages about the topic on the address.

        :param topic: a string topic
        """
        APP_LOGGER.info(f"Publisher registering for topic {topic} at address {self.address}")

        self.topics.append(topic)

        self.registration.send_string(pubsub.REG_PUB, flags=zmq.SNDMORE)
        self.registration.send_string(topic, flags=zmq.SNDMORE)
        self.registration.send_string(self.address)

        broker_type = self.registration.recv_string()
        APP_LOGGER.info(f"Connected to {broker_type} broker")

    def publish(self, topic, message, message_type=MessageType.STRING):
        """ Publishes message with the given topic

        :param topic: the topic of the message to publish, should be a registered string
        :param message: the message to publish
        :param message_type: the type of the message to send. Optional. Default = MessageType.STRING
        (valid values are MessageType.STRING, MessageType.PYOBJ, and MessageType.JSON)
        """

        if topic not in self.topics:
            raise TopicNotRegisteredError(topic, self.address, "Topic has not been registered with publisher. Cannot "
                                                               "be published")

        self.message_pub.send_string(topic, flags=zmq.SNDMORE)
        self.message_pub.send_string(datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"), flags=zmq.SNDMORE)
        self.message_pub.send_string(message_type, flags=zmq.SNDMORE)
        self.type2sender[message_type](message)
