import pubsub


def main():
    broker = pubsub.broker
    broker.is_server()
    while True:
        broker.process()


if __name__ == "__main__":
    main()
