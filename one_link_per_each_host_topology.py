#!/usr/bin/python

"""
Setting the position of Nodes (only for Stations and Access Points) and providing mobility.

"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch,OVSSwitch, UserSwitch, OVSController
from mininet.nodelib import LinuxBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def topology():

    "Create a network."
    net = Mininet( controller=Controller, link=TCLink, switch=OVSSwitch)

    print "*** Creating nodes"
    h1 = net.addHost( 'h1', mac='00:00:00:00:00:01', ip='10.0.0.1/24' )
    h2 = net.addHost( 'h2', mac='00:00:00:00:00:11', ip='10.0.0.2/24' )
    h3 = net.addHost( 'h3', mac='00:00:00:00:01:11', ip='10.0.0.3/24' )
 #   h4 = net.addHost( 'h4', mac='00:00:00:00:11:11', ip='10.0.0.4/24' )

    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2')
    s3 = net.addSwitch( 's3')
    
    c1 = net.addController( 'c1', controller=RemoteController, ip='127.0.0.1', port=6633 )

    #net.runAlternativeModule('../module/mac80211_hwsim.ko')


    print "*** Associating and Creating links"
    net.addLink(s1, h1)
    net.addLink(s2, h2)
    net.addLink(s3, h3)
    
    net.addLink(s1,s2)
    net.addLink(s2,s3)
    net.addLink(s3,s1)
    #net.addLink(ap1, ap2)


    print "*** Starting network"
    net.build()
    c1.start()
    s1.start( [c1] )
    s2.start( [c1] )
    s3.start( [c1] )

    """uncomment to plot graph"""

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()