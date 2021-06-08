#!/usr/bin/python
import argparse
import os
import shutil
from time import sleep

from mininet.cli import CLI
from mininet.node import OVSController
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

address_format = "tcp://{0}:{1}"
default_port = "5555"
broker_cmd_fmt = "python psserver.py --address {0} --port {1} --type {2} &"
publisher_cmd_fmt = "python ps_publisher.py {0} {1} --topics lorem -r 1000"
subscriber_cmd_fmt = "python ps_subscriber.py {0} {1} --topics lorem -e {2}"
output_dir = "latency"
perf_logs = "pubsub_perf.log"
banner = "\n" \
         "+-------------------------------------------------\n" \
         "| Running test with {0} subscribers and {1} broker\n" \
         "+-------------------------------------------------\n"


class SingleSwitchTopo(Topo):
    """Single switch connected to n hosts."""

    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)


def config_parser():
    parser = argparse.ArgumentParser(prog="Single Switch Tests")

    parser.add_argument('subscribers', type=int,
                        help='max number of subscribers to test')

    return parser


def run_iteration(num_subs, broker_type):
    # If using direct flag, we need the the start listener flag,
    # otherwise we can just use an empty string
    start_listener = "--start_listener" if broker_type == 'd' else ""

    # Need one host for each subscriber, one for a publisher, and one for a broker
    n_hosts = num_subs + 2

    """Create and test a simple network"""
    topo = SingleSwitchTopo(n=n_hosts)
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    hosts = net.hosts
    broker = hosts[0]
    publisher = hosts[1]
    subscribers = hosts[2:]

    broker_address = address_format.format(broker.IP(), default_port)

    # Run the broker process
    broker_cmd = broker_cmd_fmt.format(broker.IP(), default_port, broker_type)
    print(f"Running {broker_cmd}")
    broker.cmd(broker_cmd)

    # Run the subscriber processes
    for subscriber in subscribers:
        subscriber_cmd = subscriber_cmd_fmt.format(
            address_format.format(subscriber.IP(), default_port),
            broker_address,
            start_listener
        )
        print(f"Running {subscriber_cmd}")
        subscriber.sendCmd(subscriber_cmd)
    sleep(.5)

    # Run the publisher process
    publisher_cmd = publisher_cmd_fmt.format(
        address_format.format(publisher.IP(), default_port),
        broker_address
    )
    print(f"Running {publisher_cmd}")
    publisher_out = publisher.cmd(publisher_cmd)
    print(f"Publisher output: {publisher_out}")

    # Wait for the subscriber to finish processing before exiting
    for subscriber in subscribers:
        print(f"Subscriber output length: {len(subscriber.waitOutput())}")

    # Kill the broker process before exiting
    broker.cmd(f"kill %1")

    net.stop()


def main():
    arg_parser = config_parser()
    args = arg_parser.parse_args()
    max_subs = args.subscribers

    shutil.rmtree(output_dir, ignore_errors=True)
    os.mkdir(output_dir)
    filename_fmt = "sub-{0}_broker-{1}.log"

    curr_sub = 1
    while curr_sub <= max_subs:
        for broker_type in ['r', 'd']:
            print(banner.format(curr_sub, broker_type))
            run_iteration(curr_sub, broker_type)

            filename = filename_fmt.format(curr_sub, broker_type)
            shutil.move(perf_logs, os.path.join(output_dir, filename))
        curr_sub *= 2


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    main()
