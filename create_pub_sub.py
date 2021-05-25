""" Tests the publisher and subscriber register functionality

To run this test start the psserver.py broker server. When the server
receives a registration, it will print the message it received.
Then run this script which should print 'received' for each registration.

"""
from time import sleep

from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

topic = "topic1"
pub1 = Publisher("tcp://localhost:5556")
pub1.register(topic)
sub1 = Subscriber("tcp://localhost:5557")
sub1.register(topic)
sleep(5)

pub1.publish(topic, "some_message")
topic, message = sub1.wait_for_msg()
print(f"Received message: {message} On topic: {topic}")
