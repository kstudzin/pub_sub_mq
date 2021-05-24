import argparse
import sys

from pubsub.subscriber import Subscriber


def config_parser() -> argparse.ArgumentParser:
    """
    Configures the arguments accepted by the argparse module.
    :return: A (argparse.ArgumentParser)
    """
    parser = argparse.ArgumentParser(prog='Subscriber', usage='%(prog)s [options]'
                                     , description='Start subscribing to topics.')
    parser.add_argument('--port', metavar='Port', type=int, nargs='?',
                        help='port numbers')
    parser.add_argument('--topics', metavar='Topics', type=str, nargs='+',
                        help='topics to subscribe to')
    return parser


def register(args) -> Subscriber:
    """
    Register a subscriber based upon user arguments.
    :param args: A port number and a list of topics provided in arguments
    :return: A Subscriber object
    """
    if args.port is not None:
        subscriber = Subscriber(f"tcp://localhost:{args.port}")
    else:
        return None

    if args.topics is not None:
        for topic in args.topics:
            subscriber.register(topic)
    return subscriber


def main():
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    subscriber = register(args)
    while True:
        option = input("Enter 't' to add topic, 'q' to quit: ")
        if option.casefold() == "t":
            topic = input("Enter topic: ")
            print(topic)
            if len(topic) > 0:
                subscriber.register(topic)
        elif option.casefold() == "q":
            sys.exit(-1)
        else:
            print("Please enter valid option")


if __name__ == "__main__":
    main()
