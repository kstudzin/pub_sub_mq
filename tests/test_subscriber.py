import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
import zmq

from pubsub import REG_SUB
from pubsub.broker import BrokerType
from pubsub.subscriber import Subscriber
from pubsub.util import MessageType

ctx = zmq.Context()
SUB_ADDRESS = "tcp://127.0.0.1:4556"
BROKER_ADDRESS = "tcp://127.0.0.1:4555"

executor = ThreadPoolExecutor(max_workers=2)


class TestSubscriber:

    @pytest.fixture(scope="module")
    def reply(self):
        reply = ctx.socket(zmq.REP)
        reply.bind(BROKER_ADDRESS)
        yield reply
        reply.unbind(BROKER_ADDRESS)

    notifications = []

    def test_constructor(self):
        subscriber = Subscriber(SUB_ADDRESS, BROKER_ADDRESS)
        assert subscriber.address == SUB_ADDRESS
        assert subscriber.callback is not None
        assert subscriber.message_sub is not None
        assert subscriber.registration is not None
        assert len(subscriber.topics) == 0

    def broker_recv_reg(self, socket):
        reg_type = socket.recv_string()
        topic = socket.recv_string()
        address = socket.recv_string()
        socket.send_string(BrokerType.ROUTE)
        return reg_type, topic, address

    def test_register(self, reply):
        future = executor.submit(self.broker_recv_reg, reply)

        topic = "the topic name"
        subscriber = Subscriber(SUB_ADDRESS, BROKER_ADDRESS)
        subscriber.register(topic)

        result = future.result(60)
        assert result[0] == REG_SUB
        assert result[1] == topic
        assert result[2] == SUB_ADDRESS

    def callback(self, topic, message):
        self.notifications.append(Notification(topic, message))

    def test_receive_message(self, reply):
        reg_future = executor.submit(self.broker_recv_reg, reply)

        subscriber = Subscriber(SUB_ADDRESS, BROKER_ADDRESS)
        subscriber.register("the topic name")
        subscriber.register_callback(self.callback)
        notify_future = executor.submit(subscriber.wait_for_msg)

        topic = "the topic name"
        message = "the message here"

        result = reg_future.result(60)
        assert result[0] == REG_SUB
        assert result[1] == topic
        assert result[2] == SUB_ADDRESS

        pub = ctx.socket(zmq.PUB)
        pub.connect(SUB_ADDRESS)
        sleep(1)

        pub.send_string(topic, flags=zmq.SNDMORE)
        pub.send_string(MessageType.STRING, flags=zmq.SNDMORE)
        pub.send_string(message)

        notify_future.result(60)

        assert len(self.notifications) == 1
        assert self.notifications[0].topic == topic
        assert self.notifications[0].message == message


class Notification:

    def __init__(self, topic, message):
        self.topic = topic
        self.message = message
