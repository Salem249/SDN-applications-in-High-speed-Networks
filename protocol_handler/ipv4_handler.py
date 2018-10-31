import networkx.algorithms as nx
# Python Standard
import logging
import host


# Ryu
from ryu.topology.switches import Switch
from ryu.topology.switches import Port

LOG = logging.getLogger(__name__)


class icmp_handler:
    def __init__(self, networkMap):
        self.networkMap = networkMap

    def _find_protocol(self, pkt, name):
        for p in pkt.protocols:
            if hasattr(p, 'protocol_name'):
                if p.protocol_name == name:
                    return p

    def handle(self, p_ipv4, msg, in_port, eth, callback):
        datapath = msg.datapath
        ofproto = datapath.ofproto

        LOG.debug("--- ICMP Packet!: \nIP Address src:%s\nIP Address Dest:%s\n",
                  p_ipv4.src, p_ipv4.dst)

        if not self.networkMap.findActiveHostByIP(p_ipv4.src):
            self.networkMap.addActiveHost(
                datapath, msg.match['in_port'], host.host(eth.src, p_ipv4.src))

        if self.networkMap.findActiveHostByMac(eth.dst):
            LOG.debug("This adress has been found!")
            if self.networkMap.isInactiveHost(eth.src):
                LOG.debug("Activate Host...")
                self.networkMap.addActiveHost(
                    datapath, msg.match['in_port'], host.host(eth.src, p_ipv4.src))
            out_port = self.networkMap.findPortByHostMac(eth.dst).port_no
        # else:
        #     out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            if (self.networkMap.findSwitchByDatapath(datapath) != self.networkMap.findSwitchByHostMac(eth.dst)):

                LOG.debug("###More than one Switch detected###")
                path = nx.shortest_path(self.networkMap.networkMap, self.networkMap.findSwitchByDatapath(
                    datapath), self.networkMap.findSwitchByHostMac(eth.dst))
                print("---- Way to go ", str(path))

                print("--- IP Packet from ", str(p_ipv4.src), 
                    "to", str(p_ipv4.dst),"--from Switch", str(msg.datapath.id))
                for item in range(1, (len(path))):
                    if isinstance(path[item], Port) and isinstance(path[item - 1], Switch):
                        datapath = path[item - 1].dp
                        port_no = path[item].port_no
                        match = datapath.ofproto_parser.OFPMatch(
                            in_port=in_port, eth_src=eth.src,
                            eth_dst=eth.dst)
                        actions = [
                            datapath.ofproto_parser.OFPActionOutput(port_no)]

                        callback(datapath, port_no, actions, match)

                    else:
                        LOG.debug("---- Error in establishing multiflow.")
            else:
                match = datapath.ofproto_parser.OFPMatch(
                    in_port=in_port, eth_src=eth.src,
                    eth_dst=eth.dst)

                callback(datapath, out_port, actions, match)

        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
        datapath.send_msg(out)
