""" Tests the publisher and subscriber register functionality

To run this test start the psserver.py broker server. When the server
receives a registration, it will print the message it received.
Then run this script which should print 'received' for each registration.

"""
from time import sleep

from pubsub.publisher import DirectPublisher
from pubsub.subscriber import DirectSubscriber

topic1 = "topic 1"
topic2 = "topic 2"

pub1 = DirectPublisher(topic1, "127.0.0.1", 5555)
sleep(1)
sub1 = DirectSubscriber(topic1, "127.0.0.1", 5556)
sleep(1)
sub1.register(topic2)
# sleep(1)
# pub1.register(topic2)

# sleep(3)
# pub1.publish(topic1, "some message")
# pub1.publish(topic2, "other message")
#
# sub1.unregister(topic1)
#
# pub1.publish(topic1, "SHOULD NOT RECEIVE")
# pub1.publish(topic2, "should receive")
