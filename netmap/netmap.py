import networkx as nx

from host import host
from ryu.topology.switches import Switch
from ryu.topology.switches import Port


class netmap:

    def __init__(self):
        self.dDummy = "Disconnected"
        self.networkMap = nx.Graph()
        self.networkMap.add_node(self.dDummy)

    def getAllSwitches(self):
        return [switch for switch in self.networkMap.nodes if isinstance(switch, Switch)]

    def getAllSwitchPorts(self, switch):
        for thing in self.networkMap.nodes:
            if isinstance(thing, Switch) and thing == switch:
                return [port for port in self.networkMap.neighbors(switch) if isinstance(port, Port)]

    def findPortbyPortMac(self, mac):
        for thing in self.networkMap.nodes:
            if isinstance(thing, Port) and thing.hw_addr == mac:
                return thing

    def findPortByHostMac(self, mac):
        for thing in self.networkMap.nodes:
            if isinstance(thing, host) and thing.mac == mac:
                for port in self.networkMap.neighbors(thing):
                    if isinstance(port, Port):
                        return port

    def findSwitchByHostMac(self, mac):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch):
                for port in self.networkMap.neighbors(switch):
                    if isinstance(port, Port):
                        for thing in self.networkMap.neighbors(port):
                            if isinstance(thing, host):
                                if thing.mac == mac:
                                    return switch

    def findSwitchByDatapathAndByHostMac(self, hostmac, dpid):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch):
                if switch.dp.id == dpid:
                    for port in self.networkMap.neighbors(switch):
                        if isinstance(port, Port):
                            for thing in self.networkMap.neighbors(port):
                                if isinstance(thing, host):
                                    if thing.mac == hostmac:
                                        return switch

    def findSwitchByDatapath(self, dp):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch):
                if switch.dp == dp:
                    return switch

    def findSwitchByDatapathID(self, dpid):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch):
                if switch.dp.id == dpid:
                    return switch

    def findActiveHostByIP(self, ip):
        for thing in self.networkMap.nodes:
            if isinstance(thing, host) and thing.ip == ip:
                for port in self.networkMap.neighbors(thing):
                    if isinstance(port, Port):
                        return thing

    def findActiveHostByMac(self, mac):
        for thing in self.networkMap.nodes:
            if isinstance(thing, host) and thing.mac == mac:
                for port in self.networkMap.neighbors(thing):
                    if isinstance(port, Port):
                        return thing

    def isInactiveHost(self, mac):
        for thing in self.networkMap.neighbors(self.dDummy):
            if isinstance(thing, host):
                if thing.mac == mac:
                    return True

    def findInactiveHostByMac(self, mac):
        for thing in self.networkMap.neighbors(self.dDummy):
            if isinstance(thing, host):
                if thing.mac == mac:
                    return thing
        return None

    def delSwitch(self, todelete):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch):
                if switch.dp.id == todelete.dp.id:
                    self.networkMap.remove_node(switch)
                    return

    def activateHost(self, host, datapath, port_no):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch) and switch.dp == datapath:
                for port in self.networkMap.neighbors(switch):
                    if isinstance(port, Port) and port.port_no == port_no:
                        self.networkMap.add_edge(port, host)
                        self.networkMap.remove_edge(
                            self.dDummy, self.findInactiveHostByMac(host.mac))
                        return

    def findPortByPath(self, dpid, port_no):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch) and (switch.dp.id == dpid):
                for port in self.networkMap.neighbors(switch):
                    if isinstance(port, Port) and port.port_no == port_no:
                        return port

    def addSwitch(self, switch):
        self.networkMap.add_node(switch)
        for port in switch.ports:
            self.networkMap.add_edge(switch, port)

    def addActiveHost(self, datapath, port, host):
        if not self.isInactiveHost(host.mac):
            self.networkMap.add_edge(
                self.findPortByPath(datapath.id, port), host)
        else:
            self.activateHost(host, datapath, port)

    def flushInactiveHosts(self):
        todelete = []
        for node in self.networkMap.neighbors(self.dDummy):
            if isinstance(node, host):
                todelete.append(node)

        self.networkMap.remove_nodes_from(todelete)

    def report(self):
        for switch in self.networkMap.nodes:
            if isinstance(switch, Switch):
                print("+++ Switch ", str(switch))
                for port in self.networkMap.neighbors(switch):
                    if isinstance(port, Port):
                        print("--- Port ", port.port_no,
                              "with addr ", port.hw_addr)
                        for p in self.networkMap.neighbors(port):
                            if isinstance(p, Port) and not isinstance(p, Switch):
                                print("--- Connected to ", str(p))
                            if not isinstance(p, Switch) and not isinstance(p, Port):
                                print("--- Connected to ", str(p),
                                      "with MAC address", str(p.mac), "and IP address", str(p.ip))
                print "#########################"
        print("--- INACTIVE:---")
        for thing in self.networkMap.neighbors(self.dDummy):
            print "--- MAC ", thing.mac, " IP ", thing.ip, "----"
