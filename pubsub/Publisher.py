

class Publisher:
    socket = None

    def __init__(self, socket):
        self.socket = socket

    def publish(self, topic, message):
        """Publishes a message to socket(s)"""
        pass
