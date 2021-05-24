import pubsub


class Subscriber:
    topics = []
    address = None
    broker = pubsub.broker

    def __init__(self, address):
        self.address = address

    def register(self, topic):
        self.topics.append(topic)
        self.broker.register_sub(topic, self.address)

    def notify(self, topic, message):
        """Receives message"""
        pass

    def wait_for_msg(self):
        pass
