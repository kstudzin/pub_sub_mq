""" Tests the publisher and subscriber register functionality

To run this test start the psserver.py broker server. When the server
receives a registration, it will print the message it received.
Then run this script which should print 'received' for each registration.

"""
from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

pub1 = Publisher("tcp://localhost:5556")
pub1.register("topic1")
sub1 = Subscriber("tcp://localhost:5556")
sub1.register("topic1")
