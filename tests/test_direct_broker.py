import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pytest
import zmq

from pubsub import REG_PUB, REG_SUB
from pubsub.broker import DirectBroker, BrokerType

ctx = zmq.Context()
BROKER_ADDRESS = "tcp://127.0.0.1:1559"
SUB_ADDRESS = "tcp://127.0.0.1:1560"
PUB_ADDRESS = "tcp://127.0.0.1:1561"
TOPIC = "topic here"
MESSAGE = "message here"
ENCODING = "utf-8"
executor = ThreadPoolExecutor(max_workers=2)


class TestDirectBroker:

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
        broker = DirectBroker(BROKER_ADDRESS)
        assert broker.registration is not None
        assert broker.connect_address == BROKER_ADDRESS
        assert broker.registry == defaultdict(list)
        assert broker.message_out is not None

    def wait_for_msg(self, socket):
        topic = socket.recv_string()
        message = socket.recv_string()
        return topic, message

    def wait_for_registration(self, socket):
        message = socket.recv_multipart()
        return message

    def test_process_pub_registration(self, publisher):
        logging.info("Simulate registering publisher with broker")

        broker = DirectBroker(BROKER_ADDRESS)
        executor.submit(broker.process_registration)

        req = ctx.socket(zmq.REQ)
        req.connect(BROKER_ADDRESS)

        req.send_string(REG_PUB, flags=zmq.SNDMORE)
        req.send_string(TOPIC, flags=zmq.SNDMORE)
        req.send_string(PUB_ADDRESS)

        broker_type = req.recv_string()
        assert broker_type == BrokerType.DIRECT
        assert PUB_ADDRESS.encode(ENCODING) in broker.registry[TOPIC]

    def test_process_sub_registration(self, subscriber):
        logging.info("Simulate registering subscriber with broker")

        broker = DirectBroker(BROKER_ADDRESS)
        executor.submit(broker.process_registration)

        req = ctx.socket(zmq.REQ)
        req.connect(BROKER_ADDRESS)

        req.send_string(REG_SUB, flags=zmq.SNDMORE)
        req.send_string(TOPIC, flags=zmq.SNDMORE)
        req.send_string(SUB_ADDRESS)

        message = req.recv_multipart()
        assert len(message) == 2
        broker_type = message[0].decode(ENCODING)
        assert broker_type == BrokerType.DIRECT

        subscriber.setsockopt_string(zmq.SUBSCRIBE, TOPIC)
        future = executor.submit(self.wait_for_registration, subscriber)

        sleep(0.5)

        message = [TOPIC.encode(ENCODING), PUB_ADDRESS.encode(ENCODING)]
        broker.message_out.send_multipart(message)

        result = future.result(60)
        assert len(result) == 2
        topic = result[0].decode(ENCODING)
        address = result[1].decode(ENCODING)
        assert topic == TOPIC
        assert address == PUB_ADDRESS

        subscriber.setsockopt_string(zmq.UNSUBSCRIBE, TOPIC)
