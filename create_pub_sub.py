""" Tests the publisher and subscriber register functionality

To run this test start the psserver.py broker server. When the server
receives a registration, it will print the message it received.
Then run this script which should print 'received' for each registration.

"""
import threading
from time import sleep

from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber

topic1 = "topic1"
topic2 = "topic 2"

sub1 = Subscriber("tcp://127.0.0.1:5557", "tcp://127.0.0.1:5555")
pub1 = Publisher("tcp://127.0.0.1:5556", "tcp://127.0.0.1:5555")


def msg_proc_loop(subscriber):
    while True:
        subscriber.wait_for_registration()


process_publisher_thread = threading.Thread(target=msg_proc_loop,
                                            args=[sub1],
                                            daemon=True)
process_publisher_thread.start()

sleep(5)
sub1.register(topic1)
sub1.register(topic2)

sleep(5)
pub1.register(topic1)
pub1.register(topic2)

sleep(5)
pub1.publish(topic1, "some message")
sub1.wait_for_msg()

pub1.publish(topic2, "other message")
sub1.wait_for_msg()

sub1.unregister(topic1)

pub1.publish(topic1, "SHOULD NOT RECEIVE")
pub1.publish(topic2, "should receive")
sub1.wait_for_msg()
