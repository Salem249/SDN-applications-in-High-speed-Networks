#!/usr/bin/python

"""
Setting the position of Nodes (only for Stations and Access Points) and providing mobility.

"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def configure_network(network):
    h1 = network.get('h1')
    h1.setIP('10.0.0.10', intf='h1-eth0')
    h1.setMAC('00:00:00:00:00:10', intf='h1-eth0')
    h1.setIP('192.168.0.11', intf='h1-eth1')
    h1.setMAC('00:00:00:00:00:11', intf='h1-eth1')

    h2 = network.get('h2')
    h2.setIP('10.0.0.20', intf='h2-eth0')
    h2.setMAC('00:00:00:00:00:20', intf='h2-eth0')
    h2.setIP('192.168.0.21', intf='h2-eth1')
    h2.setMAC('00:00:00:00:00:21', intf='h2-eth1')

    h3 = network.get('h3')
    h3.setIP('10.0.0.30', intf='h3-eth0')
    h3.setMAC('00:00:00:00:00:30', intf='h3-eth0')
    h3.setIP('192.168.0.31', intf='h3-eth1')
    h3.setMAC('00:00:00:00:00:31', intf='h3-eth1')

def topology():
    "Create a network."
    net = Mininet(controller=Controller, link=TCLink, switch=OVSSwitch)

    print "*** Creating nodes"
    h1 = net.addHost('h1')

    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    c1 = net.addController(
        'c1', controller=RemoteController, ip='127.0.0.1', port=6633)

    print "*** Associating and Creating links"
    net.addLink(s1, h1)
    net.addLink(s3, h1)

    net.addLink(s2, h2)
    net.addLink(s1, h2)

    net.addLink(s3, h3)
    net.addLink(s2, h3)


    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s1)

    print "*** Starting network"
    net.build()
    c1.start()
    s1.start([c1])
    s2.start([c1])
    s3.start([c1])

    """uncomment to plot graph"""

    print "*** Running CLI"
    configure_network(net)
    CLI(net)

    print "*** Stopping network"
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
    
