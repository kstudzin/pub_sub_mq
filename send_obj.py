from time import sleep

from pubsub.publisher import Publisher
from pubsub.subscriber import Subscriber
from pubsub.util import MessageType

topic1 = "topic1"


class MyClass:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"


mine = MyClass("Kate")

pub1 = Publisher("tcp://localhost:5556", "tcp://localhost:5555")
sub1 = Subscriber("tcp://localhost:5557", "tcp://localhost:5555")

sleep(5)
pub1.register(topic1)
sub1.register(topic1)

sleep(5)
pub1.publish(topic1, mine, message_type=MessageType.PYOBJ)
sub1.wait_for_msg()
