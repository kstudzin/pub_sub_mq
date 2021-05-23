from pubsub.broker import RoutingBroker

broker = RoutingBroker("tcp://localhost:5555")


def main():
    broker.is_server()
    while True:
        broker.process()


if __name__ == "__main__":
    main()
