#!/usr/bin/python
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
subscriber_cmd_fmt = "python ps_subscriber.py {0} {1} --topics lorem -e"


class SingleSwitchTopo(Topo):
    """Single switch connected to n hosts."""

    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)


def main():
    """Create and test a simple network"""
    topo = SingleSwitchTopo(n=3)
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    hosts = net.hosts
    broker = hosts[0]
    publisher = hosts[1]
    subscriber = hosts[2]

    broker_address = address_format.format(broker.IP(), default_port)

    # Run the broker process
    broker_cmd = broker_cmd_fmt.format(broker.IP(), default_port, 'r')
    print(f"Running {broker_cmd}")
    broker.cmd(broker_cmd)

    # Run the subscriber processes
    subscriber_cmd = subscriber_cmd_fmt.format(
        address_format.format(subscriber.IP(), default_port),
        broker_address
    )
    print(f"Running {subscriber_cmd}")
    subscriber.sendCmd(subscriber_cmd)
    sleep(0.5)

    # Run the publisher process
    publisher_cmd = publisher_cmd_fmt.format(
        address_format.format(publisher.IP(), default_port),
        broker_address
        )
    print(f"Running {publisher_cmd}")
    publisher.cmd(publisher_cmd)

    # Wait for the subscriber to finish processing before exiting
    print(f"Subscriber output length: {len(subscriber.waitOutput())}")

    # Kill the broker process before exiting
    broker.cmd(f"kill %1")

    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    main()
