import pubsub


class Publisher:
    topics = []
    address = None
    broker = pubsub.broker

    def __init__(self, address):
        self.address = address

    def register(self, topic):
        self.topics.append(topic)
        self.broker.register_pub(topic, self.address)

    def publish(self, topic, message):
        """Publishes a message to socket(s)"""
        pass
