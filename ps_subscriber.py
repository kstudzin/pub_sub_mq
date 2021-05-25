import argparse
import sys
import threading
import time

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


def listen_for_messages() -> None:
    print("Listening....")
    while True:
        # this.subscriber getMessages
        sample = "2021-05-25 13:19:42.504443 : FB : 202.11"
        sent_time, topic, message = sample.split(" : ")
        print(f"\nTime= {sent_time} Topic= {topic} Message= {message}")
        time.sleep(3)


def main():
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    this.subscriber = register(args)
    threading.Thread(target=listen_for_messages, daemon=True).start()

    while True:
        option = input("\nEnter 't' to add topic, 'q' to quit: ")
        if option.casefold() == "t":
            topic = input("Enter topic: ")
            print(topic)
            if len(topic) > 0:
                this.subscriber.register(topic)
        elif option.casefold() == "q":
            sys.exit(-1)
        else:
            print("Please enter valid option")


if __name__ == "__main__":
    main()
