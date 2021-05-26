import pubsub.broker


def main():
    broker = pubsub.broker.RoutingBroker("tcp://localhost:5555")

    while True:
        broker.process()


if __name__ == "__main__":
    main()
