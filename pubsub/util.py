from enum import Enum, auto
from urllib.parse import urlparse


def bind_address(address):
    bind_url = urlparse(address)
    return "{0}://*:{1}".format(bind_url.scheme, bind_url.port)


class MessageType:
    STRING = "STRING"
    PYOBJ = "PYOBJ"
    JSON = "JSON"


class TopicNotRegisteredError(Exception):

    def __init__(self, name, topic, address):
        self.name = name
        self.address = address
        self.topic = topic


class PublisherTopicNotRegisteredError(TopicNotRegisteredError):

    def __init__(self, topic, address):
        super.__init__("Publisher", topic, address)


class SubscriberTopicNotRegisteredError(TopicNotRegisteredError):

    def __init__(self, topic, address):
        super.__init__("Subscriber", topic, address)
