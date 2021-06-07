import logging
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
import zmq

from pubsub import REG_PUB, REG_SUB
from pubsub.broker import RoutingBroker, BrokerType

ctx = zmq.Context()
BROKER_ADDRESS = "tcp://127.0.0.1:3554"
SUB_ADDRESS = "tcp://127.0.0.1:3560"
PUB_ADDRESS = "tcp://127.0.0.1:3561"

executor = ThreadPoolExecutor(max_workers=2)


class TestRoutingBroker:

    @pytest.fixture(scope="module")
    def publisher(self):
        pub = ctx.socket(zmq.PUB)
        pub.bind(PUB_ADDRESS)
        yield pub
        pub.unbind(PUB_ADDRESS)

    @pytest.fixture(scope="module")
    def subscriber(self):
        sub = ctx.socket(zmq.SUB)
        sub.bind(SUB_ADDRESS)
        yield sub
        sub.unbind(SUB_ADDRESS)

    def test_constructor(self):
        broker = RoutingBroker(BROKER_ADDRESS)
        assert broker.message_in is not None
        assert broker.message_out is not None

    def wait_for_msg(self, socket):
        topic = socket.recv_string()
        message = socket.recv_string()
        return topic, message

    def test_process_pub_registration(self, publisher):
        logging.info("Simulate registering publisher with broker")

        broker = RoutingBroker(BROKER_ADDRESS)
        executor.submit(broker.process_registration)

        req = ctx.socket(zmq.REQ)
        req.connect(BROKER_ADDRESS)

        req.send_string(REG_PUB, flags=zmq.SNDMORE)
        req.send_string("topic here", flags=zmq.SNDMORE)
        req.send_string(PUB_ADDRESS)

        broker_type = req.recv_string()
        assert broker_type == BrokerType.ROUTE

        logging.info("Test that registration configured broker properly")

        # Start waiting to recv the message in a thread
        future = executor.submit(self.wait_for_msg, broker.message_in)

        # Setup a socket to send the message

        sleep(.5)
        publisher.send_string("topic here", flags=zmq.SNDMORE)
        publisher.send_string("message here")

        topic, message = future.result(60)

        assert topic == "topic here"
        assert message == "message here"

    def test_process_sub_registration(self, subscriber):
        logging.info("Simulate registering publisher with broker")

        broker = RoutingBroker(BROKER_ADDRESS)
        executor.submit(broker.process_registration)

        req = ctx.socket(zmq.REQ)
        req.connect(BROKER_ADDRESS)

        req.send_string(REG_SUB, flags=zmq.SNDMORE)
        req.send_string("topic here", flags=zmq.SNDMORE)
        req.send_string(SUB_ADDRESS)

        broker_type = req.recv_string()
        assert broker_type == BrokerType.ROUTE

        logging.info("Test that registration configured broker properly")

        subscriber.setsockopt_string(zmq.SUBSCRIBE, "topic here")

        msg_future = executor.submit(subscriber.recv_string)
        sleep(.5)

        broker.message_out.send_string("topic here")

        logging.info("Waiting for message to arrive")
        topic = msg_future.result(60)
        assert topic == "topic here"

        subscriber.setsockopt_string(zmq.UNSUBSCRIBE, "topic here")

    def test_process_message(self, publisher, subscriber):
        topic = "topic here"

        broker = RoutingBroker(BROKER_ADDRESS)

        logging.info("Register subscriber")
        executor.submit(broker.process_registration)

        req = ctx.socket(zmq.REQ)
        req.connect(BROKER_ADDRESS)

        req.send_string(REG_SUB, flags=zmq.SNDMORE)
        req.send_string(topic, flags=zmq.SNDMORE)
        req.send_string(SUB_ADDRESS)

        broker_type = req.recv_string()
        assert broker_type == BrokerType.ROUTE

        logging.info("Register publisher")
        executor.submit(broker.process_registration)

        req.send_string(REG_PUB, flags=zmq.SNDMORE)
        req.send_string(topic, flags=zmq.SNDMORE)
        req.send_string(PUB_ADDRESS)

        broker_type = req.recv_string()
        assert broker_type == BrokerType.ROUTE

        logging.info("Send message")
        executor.submit(broker.process)

        logging.info("Create subscriber")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        msg_future = executor.submit(subscriber.recv_multipart)

        logging.info("Create publisher")
        sleep(.5)

        publisher.send_string(topic, flags=zmq.SNDMORE)
        publisher.send_string("message here")

        logging.info("Wait for message")
        result = msg_future.result(60)
        assert result[0].decode('utf-8') == topic
        assert result[1].decode('utf-8') == "message here"
