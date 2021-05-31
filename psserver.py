import threading
import pubsub.broker as br
import argparse as ap


def config_parser() -> ap.ArgumentParser:
    """
    Configures the arguments accepted by the argparse module.
    :return: A (argparse.ArgumentParser)
    """
    parser = ap.ArgumentParser(prog='Server', usage='%(prog)s [options]',
                               description='Start broker service.')
    parser.add_argument('--type', metavar='Type', type=str, nargs='?',
                        help="Type of broker: 'd' direct 'r' router")
    parser.add_argument('--address', metavar='Address', type=str, nargs='?',
                        help='IP address EX: 127.0.0.1')
    parser.add_argument('--port', metavar='Port', type=int, nargs='?',
                        help='Port number EX: 5556')
    return parser


def msg_proc_loop(broker):
    while True:
        broker.process()


def routing_broker(address="127.0.0.1", port=5555):
    broker = br.RoutingBroker(address, port)
    process_msg_thread = threading.Thread(target=msg_proc_loop,
                                          args=[broker],
                                          daemon=True)
    process_msg_thread.start()

    while True:
        broker.process_registration()


def direct_broker(address="127.0.0.1", port=5555):
    broker = br.DirectBroker(address, port)
    process_msg_thread = threading.Thread(target=msg_proc_loop,
                                          args=[broker],
                                          daemon=True)
    process_msg_thread.start()

    while True:
        broker.process_registration()


def main():
    arg_parser = config_parser()
    ps_args = arg_parser.parse_args()
    if ps_args.type == "r":
        routing_broker(ps_args.address, ps_args.port)
    elif ps_args.type == "d":
        direct_broker(ps_args.address, ps_args.port)
    else:
        print("Invalid option")


if __name__ == "__main__":
    main()
