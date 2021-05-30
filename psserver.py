import threading
import pubsub.broker


def msg_proc_loop(broker):
    while True:
        broker.process()


def main():
    broker = pubsub.broker.RoutingBroker("tcp://127.0.0.1:5555")
    process_msg_thread = threading.Thread(target=msg_proc_loop,
                                          args=[broker],
                                          daemon=True)
    process_msg_thread.start()

    while True:
        broker.process_registration()


if __name__ == "__main__":
    main()
