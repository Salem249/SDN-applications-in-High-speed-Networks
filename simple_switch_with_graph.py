import networkx.algorithms as nx
# Python Standard
import logging
import thread
import netaddr


# Ryu
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.topology import event
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


from protocol_handler import lldp_handler
from protocol_handler import arp_handler
from protocol_handler import ipv4_handler
from netmap import netmap


LOG = logging.getLogger(__name__)


class SimpleSwitch(app_manager.RyuApp):
  OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

  ZERO_IP = int(netaddr.IPAddress('0.0.0.0'))

  def add_flow_based_on_mac(self, datapath, priority, match, actions, buffer_id=None):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser

    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)]
    if buffer_id:
      mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                              priority=priority, match=match,
                              instructions=inst)
    else:
      mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                              match=match, instructions=inst)
    datapath.send_msg(mod)

  def add_flow(self, datapath, out_port, actions, match):
    LOG.debug("--- Add FLow matching based on IPAddress")
    ofproto = datapath.ofproto

    instructions = [datapath.ofproto_parser.OFPInstructionActions(
        ofproto_v1_3.OFPIT_APPLY_ACTIONS, actions=actions)]

    mod = datapath.ofproto_parser.OFPFlowMod(
        datapath=datapath, match=match, cookie=0, cookie_mask=0,
        command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
        out_port=out_port, flags=ofproto.OFPFF_SEND_FLOW_REM,
        instructions=instructions, priority=3)
    datapath.send_msg(mod)

  @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
  def _switch_features_handler(self, ev):
    msg = ev.msg
    datapath = msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    actions = [parser.OFPActionOutput(port=ofproto.OFPP_CONTROLLER,
                                      max_len=ofproto.OFPCML_NO_BUFFER)]
    inst = [parser.OFPInstructionActions(type_=ofproto.OFPIT_APPLY_ACTIONS,
                                         actions=actions)]
    mod = parser.OFPFlowMod(datapath=datapath,
                            priority=1,
                            match=parser.OFPMatch(),
                            instructions=inst)
    datapath.send_msg(mod)

  def __init__(self, *args, **kwargs):
    super(SimpleSwitch, self).__init__(*args, **kwargs)

    self.movedHosts = {}
    # Instance of the NetworkMap
    self.networkMap = netmap.netmap()
    # Instance of ipv4_handler
    self.ipv4 = ipv4_handler.icmp_handler(self.networkMap)
    # Instance of Arp Handler
    self.arph = arp_handler.arp_handler(self.networkMap)
    # Instance of LLDP Handler
    self.lldph = lldp_handler.lldp_handler(self.networkMap)
    # LLDP Deamon

    try:
      thread.start_new_thread(
          self.lldph._execute_lldp, (10, self._send_data))
    except:
      LOG.debug("--- LLDP Doesn't start")

  def _find_protocol(self, pkt, name):
    for p in pkt.protocols:
      if hasattr(p, 'protocol_name'):
        if p.protocol_name == name:
          return p

  @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
  def _packet_in_handler(self, ev):
    msg = ev.msg
    in_port = msg.match['in_port']
    pkt = packet.Packet(data=msg.data)
    eth = pkt.get_protocol(ethernet.ethernet)
    p_ipv4 = self._find_protocol(pkt, "ipv4")
    datapath = msg.datapath

    self.logger.info("packet in switch %s src %s dst %s in_port%s", datapath.id,
                     eth.src, eth.dst, in_port)

    # The flow rules with test of icmp
    if p_ipv4:
      self.ipv4.handle(p_ipv4, msg, in_port, eth, self.add_flow)
    elif self._find_protocol(pkt, "arp"):
      self.arph.handle(msg, self._send_packet)
    elif self._find_protocol(pkt, "lldp"):
      self.lldph.handle(msg, self._send_packet)
    else:
      LOG.debug(" --- No Supported Protocol")
      for p in pkt.protocols:
        if hasattr(p, 'protocol_name'):
          LOG.debug(p.protocol_name)

  @set_ev_cls(event.EventSwitchEnter)
  def get_topology_data(self, ev):
    if ev.switch is not None:
      switch = ev.switch
      self.networkMap.addSwitch(switch)

  @set_ev_cls(event.EventSwitchLeave)
  def remove_topology_data(self, ev):
    if ev.switch is not None:
      switch = ev.switch
      self.networkMap.delSwitch(switch)
      if len(self.networkMap.getAllSwitches()) == 0:
        self.networkMap.flushInactiveHosts()

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

  def _send_data(self, datapath, actions, data, in_port):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    out = parser.OFPPacketOut(datapath=datapath,
                              buffer_id=ofproto.OFP_NO_BUFFER,
                              in_port=in_port,
                              actions=actions,
                              data=data)
    datapath.send_msg(out)
