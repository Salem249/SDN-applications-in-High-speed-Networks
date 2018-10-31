from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.ofproto import ofproto_v1_2
from ryu.lib.packet import ethernet
from ryu.ofproto import ether
import netaddr
import host
import logging


LOG = logging.getLogger(__name__)


class arp_handler:

    def __init__(self, networkMap):
        self.networkMap = networkMap

    def _find_protocol(self, pkt, name):
        for p in pkt.protocols:
            if hasattr(p, 'protocol_name'):
                if p.protocol_name == name:
                    return p

    def _send_packet(self, datapath, actions, pkt, in_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        data = pkt.data
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)

    def handle(self, msg, callback):
        pkt = packet.Packet(data=msg.data)
        p_arp = self._find_protocol(pkt, "arp")
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if p_arp.opcode == arp.ARP_REQUEST:
            src_ip = str(netaddr.IPAddress(p_arp.src_ip))
            dst_ip = str(netaddr.IPAddress(p_arp.dst_ip))
            src_mac = str(p_arp.src_mac)

            # try to add src mac to network
            if not self.networkMap.findActiveHostByIP(src_ip):
                self.networkMap.addActiveHost(
                    datapath, msg.match['in_port'], host.host(src_mac, src_ip))

            if self.networkMap.findActiveHostByIP(dst_ip):
                dst_mac = self.networkMap.findActiveHostByIP(dst_ip).mac
                e = ethernet.ethernet(src_mac, dst_mac, ether.ETH_TYPE_ARP)
                a = arp.arp(hwtype=1, proto=ether.ETH_TYPE_IP, hlen=6, plen=4,
                            opcode=arp.ARP_REPLY, src_mac=dst_mac,
                            src_ip=dst_ip, dst_mac=src_mac, dst_ip=src_ip)
                p = packet.Packet()
                p.add_protocol(e)
                p.add_protocol(a)
                actions = [parser.OFPActionOutput(port=msg.match['in_port'])]
                print "msg.match['in_port'])]"
                print msg.match['in_port']
                print "actions"
                print actions
                callback(datapath, actions, p, ofproto.OFPP_CONTROLLER)
            else:
                LOG.debug("an ARP rquest was flooded")
                actions = [parser.OFPActionOutput(ofproto_v1_2.OFPP_FLOOD)]
                callback(datapath, actions, pkt, msg.match['in_port'])

        elif p_arp.opcode == arp.ARP_REPLY:
            if not self.networkMap.findActiveHostByIP(p_arp.src_ip):
                self.networkMap.addActiveHost(
                    msg.datapath, msg.match['in_port'], host.host(p_arp.src_mac, p_arp.src_ip))
            port = self.networkMap.findPortByHostMac(p_arp.dst_mac)
            if port:
                actions = [parser.OFPActionOutput(port=port.port_no)]
                callback(datapath, actions, pkt, ofproto.OFPP_CONTROLLER)
            else:
                actions = [parser.OFPActionOutput(ofproto_v1_2.OFPP_FLOOD)]
                callback(datapath, actions, pkt, msg.match['in_port'])
