import pubsub


def main():
    broker = pubsub.broker
    while True:
        broker.process()


if __name__ == "__main__":
    main()
