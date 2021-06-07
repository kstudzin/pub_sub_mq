import argparse
import sys
from time import sleep

from faker import Faker
from pubsub.publisher import Publisher


faker = Faker()
Faker.seed(0)

EXIT_TOPIC = "EXIT_MESSAGE"
EXIT_MESSAGE = "Exiting..."


def config_parser() -> argparse.ArgumentParser:
    """
    Configures the arguments accepted by the argparse module.
    :return: A (argparse.ArgumentParser)
    """
    parser = argparse.ArgumentParser(prog='Publisher', usage='%(prog)s [options]'
                                     , description='Start publishing topics.')
    parser.add_argument('address', metavar='Address', type=str,
                        help='<transport>://<ip_address>:<port>')
    parser.add_argument('broker_address', metavar='Broker Address', type=str,
                        help='<transport>://<ip_address>:<port>')
    parser.add_argument('--topics', metavar='Topics', type=str, nargs='+', required=True,
                        help='topics to publish')
    parser.add_argument('--random', '-r', metavar='<number of messages>', type=int,
                        help='send random messages')
    parser.add_argument('--delay', metavar='Delay', type=float, default=.5,
                        help='amount of time to wait for connections before sending messages')
    return parser


def register(address, broker_address, topics) -> Publisher:
    """
    Register a publisher based upon user arguments.
    :param address: Address to bind this publisher to
    :param broker_address: Address of broker to connect to
    :param topics: A list of topics to subscribe to
    :return: A Publisher object
    """
    publisher = Publisher(address, broker_address)

    if topics is not None:
        for topic in topics:
            publisher.register(topic)

    return publisher


def handle_cli(publisher):
    while True:
        option = input("Enter 't' to add topic, 'q' to quit: ")
        if option.casefold() == "t":
            topic = input("Enter topic: ")
            print(topic)
            if len(topic) > 0:
                publisher.register(topic)
                message = input("Enter message: ")
                if len(message) > 0:
                    publisher.publish(topic, message)
        elif option.casefold() == "q":
            sys.exit(-1)
        else:
            print("Please enter valid option")


def handle_random(publisher, topics, num_messages):
    num_sent = 0
    topic = topics[0]
    while num_sent < num_messages:
        publisher.publish(topic, get_message())
        num_sent += 1
        if num_sent % 100 == 0:
            print(f"Sent {num_sent} messages")

    publisher.publish(EXIT_TOPIC, EXIT_MESSAGE)


def get_message():
    return faker.sentence()


def main():
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    address = args.address
    broker_address = args.broker_address
    topics = args.topics
    delay = args.delay

    if args.random:
        topics.append(EXIT_TOPIC)

    publisher = register(address, broker_address, topics)

    sleep(delay)
    if args.random:
        handle_random(publisher, topics, args.random)
    else:
        handle_cli(publisher)


if __name__ == "__main__":
    main()
