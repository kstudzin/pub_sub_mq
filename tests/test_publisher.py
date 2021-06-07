import logging
import re
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
import zmq

from pubsub import REG_PUB
from pubsub.publisher import Publisher
from pubsub.util import MessageType, TopicNotRegisteredError

ctx = zmq.Context()
PUB_ADDRESS = "tcp://127.0.0.1:2557"
BROKER_ADDRESS = "tcp://127.0.0.1:2558"

executor = ThreadPoolExecutor(max_workers=2)


class TestPublisher:

    @pytest.fixture(scope="module")
    def reply(self):
        reply = ctx.socket(zmq.REP)
        reply.bind(BROKER_ADDRESS)
        yield reply
        reply.unbind(BROKER_ADDRESS)

    def test_constructor(self):
        logging.debug("testing constructor")
        publisher = Publisher(PUB_ADDRESS, BROKER_ADDRESS)
        assert publisher.address == PUB_ADDRESS
        assert publisher.message_pub is not None
        assert publisher.registration is not None

    def broker_recv_reg(self, socket):
        reg_type = socket.recv_string()
        topic = socket.recv_string()
        address = socket.recv_string()
        socket.send_string("TEST_BROKER")
        return reg_type, topic, address

    def test_register(self, reply):
        logging.debug("running test")

        future = executor.submit(self.broker_recv_reg, reply)

        topic = "the topic name"
        publisher = Publisher(PUB_ADDRESS, BROKER_ADDRESS)
        publisher.register(topic)

        result = future.result(60)
        assert result[0] == REG_PUB
        assert result[1] == topic
        assert result[2] == PUB_ADDRESS

    @pytest.fixture()
    def broker_sub(self):
        sub = ctx.socket(zmq.SUB)
        sub.connect(PUB_ADDRESS)
        sub.setsockopt_string(zmq.SUBSCRIBE, "the topic name")
        return executor.submit(self.broker_msg_recv, sub)

    def broker_msg_recv(self, socket):
        type2receiver = {MessageType.STRING: socket.recv_string,
                         MessageType.PYOBJ: socket.recv_pyobj,
                         MessageType.JSON: socket.recv_json}

        topic = socket.recv_string()
        time = socket.recv_string()
        message_type = socket.recv_string()
        message = type2receiver[message_type]()
        return topic, time, message_type, message

    def test_publish(self, broker_sub):
        topic = "the topic name"
        message = "message here"
        publisher = Publisher(PUB_ADDRESS, BROKER_ADDRESS)
        publisher.topics.append(topic)
        sleep(.5)
        publisher.publish(topic, message)

        result = broker_sub.result(60)
        assert result[0] == topic
        time_stamp_regex = re.compile(r'\d{2}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}')  #"%m/%d/%Y %H:%M:%S"
        assert time_stamp_regex.match(result[1])
        assert result[2] == MessageType.STRING
        assert result[3] == message

    def test_publish_pyobj(self, broker_sub):
        topic = "the topic name"
        message = Person("Harry Potter", 41)
        publisher = Publisher(PUB_ADDRESS, BROKER_ADDRESS)
        publisher.topics.append(topic)
        sleep(.5)
        publisher.publish(topic, message, MessageType.PYOBJ)

        result = broker_sub.result(60)
        assert result[0] == topic
        assert result[1] == MessageType.PYOBJ
        assert result[2] == message

    def test_publish(self):
        with pytest.raises(TopicNotRegisteredError) as err:
            topic = "the topic name"
            message = "message here"
            publisher = Publisher(PUB_ADDRESS, BROKER_ADDRESS)
            publisher.publish(topic, message)
        assert "Topic has not been registered with publisher" in str(err.value)


class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age
