import argparse
import sys
import sample_data

from pubsub.publisher import Publisher


def config_parser() -> argparse.ArgumentParser:
    """
    Configures the arguments accepted by the argparse module.
    :return: A (argparse.ArgumentParser)
    """
    parser = argparse.ArgumentParser(prog='Publisher', usage='%(prog)s [options]',
                                     description='Start publishing topics.')
    parser.add_argument('--port', metavar='Port', type=int, nargs='?',
                        help='port numbers')
    parser.add_argument('--topics', metavar='Topics', type=str, nargs='+',
                        help='topics to publish')
    return parser


def register(args) -> Publisher:
    """
    Register a publisher based upon user arguments.
    :param args: A port number and a list of topics provided in arguments
    :return: A Publisher object
    """
    if args.port is not None:
        publisher = Publisher(f"tcp://localhost:{args.port}")
    else:
        return None

    if args.topics is not None:
        for topic in args.topics:
            publisher.register(topic)
    return publisher


def main():
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    publisher = register(args)
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
                else:
                    print("Please enter valid option")
                    continue
            else:
                print("Please enter valid option")
                continue
        elif option.casefold() == "q":
            sys.exit(-1)
        else:
            print("Please enter valid option")


if __name__ == "__main__":
    main()
