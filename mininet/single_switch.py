#!/usr/bin/python
from mininet.cli import CLI
from mininet.node import OVSController
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


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

    CLI(net)

    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simple_test()
