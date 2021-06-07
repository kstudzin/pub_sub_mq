import argparse
import sys
import threading

from pubsub.subscriber import Subscriber
this = sys.modules[__name__]
this.subscriber = None


def config_parser() -> argparse.ArgumentParser:
    """
    Configures the arguments accepted by the argparse module.
    :return: A (argparse.ArgumentParser)
    """
    parser = argparse.ArgumentParser(prog='Subscriber', usage='%(prog)s [options]',
                                     description='Start subscribing to topics.')
    parser.add_argument('address', metavar='Address', type=str,
                        help='<transport>://<ip_address>:<port>')
    parser.add_argument('broker_address', metavar='Broker Address', type=str,
                        help='<transport>://<ip_address>:<port>')
    parser.add_argument('--topics', metavar='Topics', type=str, nargs='+', required=True,
                        help='topics to subscribe to')
    parser.add_argument('--start_listener', action='store_true',
                        help='flag to start thread to listen for publisher registration')
    return parser


def register(address, broker_address, topics) -> Subscriber:
    """
    Register a subscriber based upon user arguments.
    :param address: Address to bind this publisher to
    :param broker_address: Address of the broker to connect to
    :param topics: A list of topics to subscribe to
    :return: A Subscriber object
    """
    subscriber = Subscriber(address, broker_address)

    if topics is not None:
        for topic in topics:
            subscriber.register(topic)

    return subscriber


def listen_for_registration(subscriber):
    while True:
        subscriber.wait_for_registration()


def main():
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    address = args.address
    broker_address = args.broker_address
    topics = args.topics
    subscriber = register(address, broker_address, topics)

    if args.start_listener:
        threading.Thread(target=listen_for_registration, args=[subscriber], daemon=True).start()

    while True:
        subscriber.wait_for_msg()


if __name__ == "__main__":
    main()
