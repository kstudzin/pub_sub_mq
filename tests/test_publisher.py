import concurrent
import concurrent.futures
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from unittest import mock

import pytest
import zmq

from pubsub import REG_PUB
from pubsub.publisher import Publisher
from pubsub.util import MessageType, TopicNotRegisteredError

ctx = zmq.Context()
pub_address = "tcp://127.0.0.1:5556"
broker_address = "tcp://127.0.0.1:5555"

executor = ThreadPoolExecutor(max_workers=2)


def test_constructor():
    logging.debug("testing constructor")
    publisher = Publisher(pub_address, broker_address)
    assert publisher.address == pub_address
    assert publisher.message_pub is not None
    assert publisher.registration is not None


@pytest.fixture()
def broker_rep():
    reply = ctx.socket(zmq.REP)
    reply.bind(broker_address)
    result = executor.submit(broker_recv_reg, reply)
    return result


def broker_recv_reg(socket):
    reg_type = socket.recv_string()
    topic = socket.recv_string()
    address = socket.recv_string()
    socket.send_string("TEST_BROKER")
    return reg_type, topic, address


def test_register(broker_rep):
    logging.debug("running test")
    topic = "the topic name"
    publisher = Publisher(pub_address, broker_address)
    publisher.register(topic)

    result = broker_rep.result(60)
    assert result[0] == REG_PUB
    assert result[1] == topic
    assert result[2] == pub_address


@pytest.fixture()
def broker_sub():
    sub = ctx.socket(zmq.SUB)
    sub.connect(pub_address)
    sub.setsockopt_string(zmq.SUBSCRIBE, "the topic name")
    return executor.submit(broker_msg_recv, sub)


def broker_msg_recv(socket):
    type2receiver = {MessageType.STRING: socket.recv_string,
                     MessageType.PYOBJ: socket.recv_pyobj,
                     MessageType.JSON: socket.recv_json}

    topic = socket.recv_string()
    message_type = socket.recv_string()
    message = type2receiver[message_type]()
    return topic, message_type, message


def test_publish(broker_sub):
    topic = "the topic name"
    message = "message here"
    publisher = Publisher(pub_address, broker_address)
    publisher.topics.append(topic)
    sleep(.5)
    publisher.publish(topic, message)

    result = broker_sub.result(60)
    assert result[0] == topic
    assert result[1] == MessageType.STRING
    assert result[2] == message


def test_publish_pyobj(broker_sub):
    topic = "the topic name"
    message = Person("Harry Potter", 41)
    publisher = Publisher(pub_address, broker_address)
    publisher.topics.append(topic)
    sleep(.5)
    publisher.publish(topic, message, MessageType.PYOBJ)

    result = broker_sub.result(60)
    assert result[0] == topic
    assert result[1] == MessageType.PYOBJ
    assert result[2] == message


def test_publish():
    with pytest.raises(TopicNotRegisteredError) as err:
        topic = "the topic name"
        message = "message here"
        publisher = Publisher(pub_address, broker_address)
        publisher.publish(topic, message)
    assert "Topic has not been registered with publisher" in str(err.value)


class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age
