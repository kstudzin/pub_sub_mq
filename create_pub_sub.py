""" Tests the publisher and subscriber register functionality

To run this test start the psserver.py broker server. When the server
receives a registration, it will print the message it received.
Then run this script which should print 'received' for each registration.

"""
from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

pub1 = Publisher("topic1", "tcp://localhost:5556")
sub1 = Subscriber("topic1", "tcp://localhost:5556")
