class Subscriber:
    socket = None

    def __init__(self, socket):
        self.socket = socket

    def notify(self, topic, message):
        """Receives message"""
        pass
