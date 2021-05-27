""" Tests the publisher and subscriber register functionality

To run this test start the psserver.py broker server. When the server
receives a registration, it will print the message it received.
Then run this script which should print 'received' for each registration.

"""
from time import sleep

from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

topic1 = "topic1"
topic2 = "topic 2"

pub1 = Publisher("tcp://localhost:5556", "tcp://localhost:5555")
sub1 = Subscriber("tcp://localhost:5557", "tcp://localhost:5555")

sleep(5)
pub1.register(topic1)
pub1.register(topic2)
sub1.register(topic1)
sub1.register(topic2)

sleep(5)
pub1.publish(topic1, "some message")
sub1.wait_for_msg()

pub1.publish(topic2, "other message")
sub1.wait_for_msg()
