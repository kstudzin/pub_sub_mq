import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest

from pubsub.broker import BrokerType, RoutingBroker, DirectBroker
from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

executor = ThreadPoolExecutor(max_workers=3)


def wait_loop(func, max_iters=0):
    iters = 0
    while max_iters == 0 or iters < max_iters:
        func()
        iters += 1

    logging.debug(f"Exiting wait loop")


nl = []


def test_publish_routing():
    broker_address = "tcp://127.0.0.1:5510"
    sub_address = "tcp://127.0.0.1:5520"
    pub_address = "tcp://127.0.0.1:5530"
    topic = "numbers"
    num_msg = 100
    nl.clear()

    broker = RoutingBroker(broker_address)
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
    broker_address = "tcp://127.0.0.1:5511"
    sub_address = "tcp://127.0.0.1:5521"
    pub_address = "tcp://127.0.0.1:5531"
    topic = "numbers"
    num_msg = 100
    nl.clear()

    broker = DirectBroker(broker_address)
    executor.submit(wait_loop, broker.process_registration, 2)

    logging.info("setting up subscriber")
    sub = Subscriber(sub_address, broker_address)
    future = executor.submit(wait_loop, sub.wait_for_msg, num_msg)
    executor.submit(wait_loop, sub.wait_for_registration, 1)

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


def test_publish_first_routing():
    broker_address = "tcp://127.0.0.1:5512"
    sub_address = "tcp://127.0.0.1:5522"
    pub_address = "tcp://127.0.0.1:5532"
    topic = "numbers"
    num_msg = 100
    nl.clear()

    broker = RoutingBroker(broker_address)
    executor.submit(wait_loop, broker.process, num_msg)
    executor.submit(wait_loop, broker.process_registration, 2)

    logging.info("setting up publisher")
    pub = Publisher(pub_address, broker_address)
    pub.register(topic)

    logging.info("setting up subscriber")
    sub = Subscriber(sub_address, broker_address)
    future = executor.submit(wait_loop, sub.wait_for_msg, num_msg)

    sub.register_callback(add_number)
    sub.register(topic)
    sleep(.5)

    numbers = []
    for i in range(num_msg):
        pub.publish(topic, str(i))
        numbers.append(str(i))

    future.result(60)
    logging.info(f"nl: {nl}")
    logging.info(f"nu: {numbers}")
    assert nl == numbers


def test_publish_first_direct():
    broker_address = "tcp://127.0.0.1:5513"
    sub_address = "tcp://127.0.0.1:5523"
    pub_address = "tcp://127.0.0.1:5533"
    topic = "numbers"
    num_msg = 100
    nl.clear()

    broker = DirectBroker(broker_address)
    sleep(.5)
    executor.submit(wait_loop, broker.process_registration, 2)

    logging.info("setting up publisher")
    pub = Publisher(pub_address, broker_address)
    pub.register(topic)

    logging.info("setting up subscriber")
    sub = Subscriber(sub_address, broker_address)
    future = executor.submit(wait_loop, sub.wait_for_msg, num_msg)

    sub.register_callback(add_number)
    sub.register(topic)

    sleep(.5)
    numbers = []
    for i in range(num_msg):
        pub.publish(topic, str(i))
        numbers.append(str(i))

    future.result(60)
    logging.info(f"nl: {nl}")
    logging.info(f"nu: {numbers}")
    assert nl == numbers


def test_two_publishers():
    broker_address = "tcp://127.0.0.1:5514"
    sub_address = "tcp://127.0.0.1:5524"
    pub_address = "tcp://127.0.0.1:5534"
    pub2_address = "tcp://127.0.0.1:5535"
    topic = "numbers"
    topic2 = "other numbers"
    num_msg = 10
    nl.clear()

    broker = RoutingBroker(broker_address)
    executor.submit(wait_loop, broker.process, num_msg * 2)
    executor.submit(wait_loop, broker.process_registration, 4)

    logging.info("setting up subscriber")
    sub = Subscriber(sub_address, broker_address)
    future = executor.submit(wait_loop, sub.wait_for_msg, num_msg * 2)

    sub.register_callback(add_number)
    sub.register(topic)
    sub.register(topic2)

    logging.info("setting up publisher")
    pub1 = Publisher(pub_address, broker_address)
    pub1.register(topic)

    pub2 = Publisher(pub2_address, broker_address)
    pub2.register(topic2)

    sleep(.5)
    numbers = []
    for i in range(num_msg):
        pub1.publish(topic, f"pub1 {i}")
        pub2.publish(topic2, f"pub2 {i}")
        numbers.append(f"pub1 {i}")
        numbers.append(f"pub2 {i}")

    future.result(60)
    logging.info(f"nl: {nl}")
    logging.info(f"nu: {numbers}")
    assert len(nl) == len(numbers)


def add_number(topic, message):
    nl.append(message)
