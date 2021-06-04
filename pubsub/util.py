
class MessageType:
    STRING = "STRING"
    PYOBJ = "PYOBJ"
    JSON = "JSON"


class TopicNotRegisteredError(Exception):

    def __init__(self, topic, address, message):
        self.topic = topic
        self.address = address
        self.message = message
        super(Exception, self).__init__(self.message)

    def __str__(self):
        return f"{self.message} Topic: {self.topic} Address: {self.address}"
