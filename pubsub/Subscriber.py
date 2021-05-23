import argparse


class Subscriber:
    def __init__(self):
        self.sockets = {}

    def add_port(self, port_num):
        self.sockets[port_num] = []

    def add_topic(self, topic):
        for value in self.sockets.values():
            value.append(topic)

    def notify(self, topic, message):
        """Receives message"""
        pass


subscriber = None
parser = argparse.ArgumentParser(prog='Subscriber', usage='%(prog)s [options]'
                                 , description='Start subscribing to topics.')
parser.add_argument('--ports', metavar='Ports', type=int, nargs='+',
                    help='port numbers')
parser.add_argument('--topics', metavar='Topics', type=str, nargs='+',
                    help='topics to subscribe to')

args = parser.parse_args()

if args.ports is not None and args.topics is not None:
    subscriber = Subscriber()
    for port in args.ports:
        subscriber.add_port(port)
    for topic in args.topics:
        subscriber.add_topic(topic)

print(subscriber.sockets)


