import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest

from pubsub.broker import BrokerType, RoutingBroker, DirectBroker
from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

broker_address = "tcp://127.0.0.1:5562"
sub_address = "tcp://127.0.0.1:5563"
pub_address = "tcp://127.0.0.1:5564"

executor = ThreadPoolExecutor(max_workers=3)


def wait_loop(func, max_iters=0):
    iters = 0
    while max_iters == 0 or iters < max_iters:
        func()
        iters += 1

    logging.debug(f"Exiting")


nl = []


def test_publish_routing():
    topic = "numbers"
    num_msg = 100
    nl.clear()

    broker = RoutingBroker("tcp://127.0.0.1:5562")
    executor.submit(wait_loop, broker.process, num_msg)
    executor.submit(wait_loop, broker.process_registration, 2)

    logging.info("setting up subscriber")
    sub = Subscriber(sub_address, broker_address)
    future = executor.submit(wait_loop, sub.wait_for_msg, num_msg)

    sub.register_callback(add_number)
    sub.register(topic)

    logging.info("setting up publisher")
    pub = Publisher(pub_address, broker_address)
    pub.register(topic)

    sleep(.5)
    numbers = []
    for i in range(num_msg):
        pub.publish(topic, str(i))
        numbers.append(str(i))

    future.result(60)
    logging.info(f"nl: {nl}")
    logging.info(f"nu: {numbers}")
    assert nl == numbers


def test_publish_direct():
    topic = "numbers"
    num_msg = 100
    nl.clear()

    broker = DirectBroker("tcp://127.0.0.1:5565")
    executor.submit(wait_loop, broker.process_registration, 3)

    logging.info("setting up subscriber")
    sub = Subscriber(sub_address, "tcp://127.0.0.1:5565")
    future = executor.submit(wait_loop, sub.wait_for_msg, num_msg)
    executor.submit(wait_loop, sub.wait_for_registration, 1)

    sub.register_callback(add_number)
    sub.register(topic)

    logging.info("setting up publisher")
    pub = Publisher(pub_address, "tcp://127.0.0.1:5565")
    pub.register(topic)

    sleep(.5)
    numbers = []
    for i in range(num_msg):
        pub.publish(topic, str(i))
        numbers.append(str(i))

    future.result(60)
    logging.info(f"nl: {nl}")
    logging.info(f"nu: {numbers}")
    assert nl == numbers


def add_number(topic, message):
    if topic == "numbers":
        nl.append(message)
