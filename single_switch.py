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
broker_cmd = "python psserver.py --address {0} --port {1} --type {2}"
publisher_cmd = "python ps_publisher.py {0} {1} --topics lorem -r 1000"
subscriber_cmd = "python ps_publisher.py {0} {1} --topics lorem "


class SingleSwitchTopo(Topo):
    """Single switch connected to n hosts."""

    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)


def simple_test():
    """Create and test a simple network"""
    topo = SingleSwitchTopo(n=3)
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    print("Dumping host connections")
    dumpNodeConnections(net.hosts)

    print("Testing network connectivity")
    net.pingAll()

    hosts = net.hosts
    broker = hosts[0]
    publisher = hosts[1]
    subscriber = hosts[2]

    broker.sendCmd('echo hello > broker.log')
    subscriber.sendCmd('echo hello > sub.log')
    publisher.cmd('date > pub.log; sleep 5; date >> pub.log')

    print(f"Subscriber output: {subscriber.waitOutput()}")
    print(f"Broker output: {broker.waitOutput()}")

    # broker_address = address_format.format(broker.IP, default_port)
    # broker.cmd(broker_cmd.format(broker.IP, default_port, 'r'))
    # publisher.cmd(publisher_cmd.format(
    #     address_format.format(publisher.IP, default_port),
    #     broker_address
    #     ))
    # sleep(.05)
    # subscriber.cmd(subscriber_cmd.format(
    #     address_format.format(subscriber.IP, default_port),
    #     broker_address
    # ))
    # CLI(net)

    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simple_test()
