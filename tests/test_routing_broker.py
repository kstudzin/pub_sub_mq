import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
import zmq

from pubsub import REG_PUB
from pubsub.broker import RoutingBroker, BrokerType

ctx = zmq.Context()
broker_address = "tcp://127.0.0.1:5555"
pub_address = "tcp://127.0.0.1:5556"

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
    logging.info("Simulate registering with broker")

    broker = RoutingBroker(broker_address)
    executor.submit(broker.process_registration)

    req = ctx.socket(zmq.REQ)
    req.connect(broker_address)

    req.send_string(REG_PUB, flags=zmq.SNDMORE)
    req.send_string("topic here", flags=zmq.SNDMORE)
    req.send_string(pub_address)

    broker_type = req.recv_string()
    assert broker_type == BrokerType.ROUTE

    logging.info("Test that registration configured broker properly")

    # Start waiting to recv the message in a thread
    future = executor.submit(wait_for_msg, broker.message_in)

    # Setup a socket to send the message
    pub = ctx.socket(zmq.PUB)
    pub.bind(pub_address)
    sleep(.5)
    pub.send_string("topic here", flags=zmq.SNDMORE)
    pub.send_string("message here")

    topic, message = future.result(60)

    assert topic == "topic here"
    assert message == "message here"

    pub.unbind(pub_address)
