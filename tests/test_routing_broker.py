import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
import zmq

from pubsub import REG_PUB, REG_SUB
from pubsub.broker import RoutingBroker, BrokerType

ctx = zmq.Context()
broker_address = "tcp://127.0.0.1:5555"
address1 = "tcp://127.0.0.1:5556"
address2 = "tcp://127.0.0.1:5557"

executor = ThreadPoolExecutor(max_workers=2)


def test_constructor():
    broker = RoutingBroker(broker_address)
    assert broker.message_in is not None
    assert broker.message_out is not None


def wait_for_msg(socket):
    topic = socket.recv_string()
    message = socket.recv_string()
    return topic, message


def test_process_pub_registration():
    logging.info("Simulate registering publisher with broker")

    broker = RoutingBroker(broker_address)
    executor.submit(broker.process_registration)

    req = ctx.socket(zmq.REQ)
    req.connect(broker_address)

    req.send_string(REG_PUB, flags=zmq.SNDMORE)
    req.send_string("topic here", flags=zmq.SNDMORE)
    req.send_string(address1)

    broker_type = req.recv_string()
    assert broker_type == BrokerType.ROUTE

    logging.info("Test that registration configured broker properly")

    # Start waiting to recv the message in a thread
    future = executor.submit(wait_for_msg, broker.message_in)

    # Setup a socket to send the message
    pub = ctx.socket(zmq.PUB)
    pub.bind(address1)
    sleep(.5)
    pub.send_string("topic here", flags=zmq.SNDMORE)
    pub.send_string("message here")

    topic, message = future.result(60)

    assert topic == "topic here"
    assert message == "message here"

    pub.unbind(address1)


def test_process_sub_registration():
    logging.info("Simulate registering publisher with broker")

    broker = RoutingBroker(broker_address)
    executor.submit(broker.process_registration)

    req = ctx.socket(zmq.REQ)
    req.connect(broker_address)

    req.send_string(REG_SUB, flags=zmq.SNDMORE)
    req.send_string("topic here", flags=zmq.SNDMORE)
    req.send_string(address1)

    broker_type = req.recv_string()
    assert broker_type == BrokerType.ROUTE

    logging.info("Test that registration configured broker properly")

    sub = ctx.socket(zmq.SUB)
    sub.bind(address1)
    sub.setsockopt_string(zmq.SUBSCRIBE, "topic here")

    msg_future = executor.submit(sub.recv_string)
    sleep(.5)

    broker.message_out.send_string("topic here")

    logging.info("Waiting for message to arrive")
    topic = msg_future.result(60)
    assert topic == "topic here"

    sub.unbind(address1)


def test_process_message():
    topic = "topic here"

    broker = RoutingBroker(broker_address)

    logging.info("Register subscriber")
    executor.submit(broker.process_registration)

    req = ctx.socket(zmq.REQ)
    req.connect(broker_address)

    req.send_string(REG_SUB, flags=zmq.SNDMORE)
    req.send_string(topic, flags=zmq.SNDMORE)
    req.send_string(address1)

    broker_type = req.recv_string()
    assert broker_type == BrokerType.ROUTE

    logging.info("Register publisher")
    executor.submit(broker.process_registration)

    req.send_string(REG_PUB, flags=zmq.SNDMORE)
    req.send_string(topic, flags=zmq.SNDMORE)
    req.send_string(address2)

    broker_type = req.recv_string()
    assert broker_type == BrokerType.ROUTE

    logging.info("Send message")
    executor.submit(broker.process)

    logging.info("Create subscriber")
    sub = ctx.socket(zmq.SUB)
    sub.bind(address1)
    sub.setsockopt_string(zmq.SUBSCRIBE, topic)
    msg_future = executor.submit(sub.recv_multipart)

    logging.info("Create publisher")
    pub = ctx.socket(zmq.PUB)
    pub.bind(address2)
    sleep(.5)

    pub.send_string(topic, flags=zmq.SNDMORE)
    pub.send_string("message here")

    logging.info("Wait for message")
    result = msg_future.result(60)
    assert result[0].decode('utf-8') == topic
    assert result[1].decode('utf-8') == "message here"

    sub.unbind(address1)
    pub.unbind(address2)
