from enum import Enum, auto
from urllib.parse import urlparse


def bind_address(address):
    bind_url = urlparse(address)
    return "{0}://*:{1}".format(bind_url.scheme, bind_url.port)


class MessageType:
    STRING = "STRING"
    PYOBJ = "PYOBJ"
    JSON = "JSON"
