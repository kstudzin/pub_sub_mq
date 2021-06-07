import argparse
import sys
import threading

from pubsub.subscriber import Subscriber
this = sys.modules[__name__]
this.subscriber = None

EXIT_TOPIC = "EXIT_MESSAGE"
EXIT_MESSAGE = "Exiting..."

exit_received = False


def exiting_callback(topic, message):
    if topic == EXIT_TOPIC and message == EXIT_MESSAGE:
        print("Received exit message...")
        global exit_received
        exit_received = True
    else:
        print(f"Topic: {topic}, Message: {message}")


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
    parser.add_argument('--receive_exit', '-e', action='store_true',
                        help='flag indicating that this program will exit when publisher'
                             'indicates it has sent its final message')
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
    print("Intializing...")
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    address = args.address
    broker_address = args.broker_address
    topics = args.topics

    if args.receive_exit:
        topics.append(EXIT_TOPIC)

    subscriber = register(address, broker_address, topics)
    subscriber.register_callback(exiting_callback)

    if args.start_listener:
        threading.Thread(target=listen_for_registration, args=[subscriber], daemon=True).start()

    print("Waiting for messages...")
    while not exit_received:
        subscriber.wait_for_msg()

    print("Exiting...")


if __name__ == "__main__":
    main()
