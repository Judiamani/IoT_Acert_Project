import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../src/')

from scapy.all import *
import scapy.contrib.coap as scapy_coap


import gen_rulemanager as RM
import compr_parser as parser
from compr_core import *

import pprint
import binascii

import socket
import ipaddress

coap_options = {'If-Match':1,
            'Uri-Host':3,
            'ETag':4,
            'If-None-Match':5,
            'Observe':6,
            'Uri-Port':7,
            'Location-Path':8,
            'Uri-Path':11,
            'Content-Format':12,
            'Max-Age':14,
            'Uri-Query':15,
            'Accept':17,
            'Location-Query':20,
            'Block2':23,
            'Block1':27,
            'Size2':28,
            'Proxy-Uri':35,
            'Proxy-Scheme':39,
            'Size1':60}

class debug_protocol:
    def _log(*arg):
        print (arg)

parse = parser.Parser(debug_protocol)
rm    = RM.RuleManager()
rm.Add(file="icmp.json")
rm.Print()


comp = Compressor(debug_protocol)
decomp = Decompressor(debug_protocol)

def send_scapy(fields, pkt_bb, rule=None):
    """" Create and send a packet, rule is needed if containing CoAP options to order them
    """ 

    pkt_data = bytearray()
    while (pkt_bb._wpos - pkt_bb._rpos) >= 8:
        octet = pkt_bb.get_bits(nb_bits=8)
        pkt_data.append(octet)

    c = {}
    for k in [T_IPV6_DEV_PREFIX, T_IPV6_DEV_IID, T_IPV6_APP_PREFIX, T_IPV6_APP_IID]:
        v = fields[(k, 1)][0]
        if type(v) == bytes:
            c[k] = int.from_bytes(v, "big")
        elif type(v) == int:
            c[k] = v
        else:
            raise ValueError ("Type not supported")
        
    
    IPv6Src = (c[T_IPV6_DEV_PREFIX] <<64) + c[T_IPV6_DEV_IID]
    IPv6Dst = (c[T_IPV6_APP_PREFIX] <<64) + c[T_IPV6_APP_IID]

    
    IPv6Sstr = ipaddress.IPv6Address(IPv6Src)
    IPv6Dstr = ipaddress.IPv6Address(IPv6Dst)
    
    IPv6Header = IPv6 (
        version= fields[(T_IPV6_VER, 1)][0],
        tc     = fields[(T_IPV6_TC, 1)][0],
        fl     = fields[(T_IPV6_FL, 1)][0],
        nh     = fields[(T_IPV6_NXT, 1)][0],
        hlim   = fields[(T_IPV6_HOP_LMT, 1)][0],
        src    =IPv6Sstr.compressed, 
        dst    =IPv6Dstr.compressed
    ) 

    if fields[(T_IPV6_NXT, 1)][0] == 58: #IPv6 /  ICMPv6
        ICMPv6Header = ICMPv6EchoReply(
            id = fields[(T_ICMPV6_IDENT, 1)][0],
            seq =  fields[(T_ICMPV6_SEQNO, 1)][0],
            data = pkt_data
        )

        full_header = IPv6Header/ICMPv6Header
    elif fields[(T_IPV6_NXT, 1)][0] == 17: # IPv6 / UDP
        UDPHeader = UDP (
            sport = fields[(T_UDP_DEV_PORT, 1)][0],
            dport = fields[(T_UDP_APP_PORT, 1)][0]
            )
        if (T_COAP_VERSION, 1) in fields: # IPv6 / UDP / COAP
            print ("CoAP Inside")

            b1 = (fields[(T_COAP_VERSION, 1)][0] << 6)|(fields[(T_COAP_TYPE, 1)][0]<<4)|(fields[(T_COAP_TKL, 1)][0])
            coap_h = struct.pack("!BBH", b1, fields[(T_COAP_CODE, 1)][0], fields[(T_COAP_MID, 1)][0])

            tkl = fields[(T_COAP_TKL, 1)][0]
            if tkl != 0:
                token = fields[(T_COAP_TOKEN, 1)][0]
                for i in range(tkl-1, -1, -1):
                    bt = (token & (0xFF << 8*i)) >> 8*i
                    coap_h += struct.pack("!B", bt)

            delta_t = 0
            comp_rule = rule[T_COMP] # look into the rule to find options 
            for idx in range(0, len(comp_rule)):
                if comp_rule[idx][T_FID] == T_COAP_MID:
                    break

            idx += 1 # after MID is there TOKEN
            if idx < len(comp_rule) and comp_rule[idx][T_FID] == T_COAP_TOKEN:
                print ("skip token")
                idx += 1

            for idx2 in range (idx, len(comp_rule)):
                print (comp_rule[idx2])
                opt_name = comp_rule[idx2][T_FID].replace("COAP.", "")
                
                delta_t = coap_options[opt_name] - delta_t
                print (delta_t)

                if delta_t < 13:
                    dt = delta_t
                else:
                    dt = 13
                    
                opt_len = fields[(comp_rule[idx2][T_FID], comp_rule[idx2][T_FP])][1] // 8
                opt_val = fields[(comp_rule[idx2][T_FID], comp_rule[idx2][T_FP])][0]
                print (opt_len, opt_val)

                if opt_len < 13:
                    ol = opt_len
                else:
                    ol = 13
                    
                coap_h += struct.pack("!B", (dt <<4) | ol)

                if dt == 13:
                    coap_h += struct.pack("!B", delta_t - 13)

                if ol == 13:
                    coap_h += struct.pack("!B", opt_len - 13)


                for i in range (0, opt_len):
                    print (i)
                    if type(opt_val) == str:
                        coap_h += struct.pack("!B", ord(opt_val[i]))
                    elif type(opt_val) == int:
                        v = (opt_val & (0xFF << (opt_len - i - 1))) >> (opt_len - i - 1)
                        coap_h += struct.pack("!B", v)

            if len(pkt_data) > 0:
                coap_h += b'\xff'
                coap_h += pkt_data

                    
            print (binascii.hexlify(coap_h))

            full_header = IPv6Header / UDPHeader / Raw(load=coap_h)
            pass
        else: # IPv6/UDP
            full_header = IPv6Header / UDPHeader / Raw(load=pkt_data)
    else: # IPv6 only
        full_header= IPv6Header / Raw(load=pkt_data)
        

    full_header.show()
#    full_header.hexdump()

    send(full_header, iface="he-ipv6")
compr_rule={"RuleID": 5,
    "RuleIDLength": 3,
    "Compression": [ 
      {"FID": "IPV6.VER", "TV": 6, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.TC",  "TV": 1, "MO": "equal", "CDA": "not-sent"},
      {"FID": "IPV6.FL",  "TV": 144470, "MO": "ignore","CDA": "not-sent"},
      {"FID": "IPV6.LEN",          "MO": "ignore","CDA": "compute-length"},
      {"FID": "IPV6.NXT", "TV": 17, "MO": "ignore", "CDA": "value-sent"},
      {"FID": "IPV6.HOP_LMT", "TV" : 255,"MO": "ignore","CDA": "not-sent"},
      {"FID": "IPV6.DEV_PREFIX","TV": ["2001:db8::/64",
                                       "fe80::/64",
                                       "2001:0420:c0dc:1002::/64" ],
                                         "MO": "match-mapping","CDA": "mapping-sent","SB": 1},
      {"FID": "IPV6.DEV_IID", "TV": "::1","MO": "equal","CDA": "DEVIID"}, 
      {"FID": "IPV6.APP_PREFIX","TV": [ "2001:db8:1::/64",
                                        "fe80::/64",
                                        "2404:6800:4004:818::/64" ],
                                         "MO": "match-mapping","CDA": "mapping-sent", "SB": 2},
      {"FID": "IPV6.APP_IID", "TV": 2,"MO": "equal","CDA": "not-sent"},
      {"FID": "UDP.DEV_PORT",  "TV": 5680,"MO": "MSB", "MO.VAL": 12, "CDA": "LSB"},
      {"FID": "UDP.APP_PORT",  "TV": 5680,"MO": "MSB", "MO.VAL": 12, "CDA" : "LSB"},
      {"FID": "UDP.LEN",       "TV": 0,   "MO": "ignore","CDA": "compute-length"},
      {"FID": "UDP.CKSUM",     "TV": 0,  "MO": "ignore","CDA": "compute-checksum"},
      {"FID": "COAP.VER", "TV": 1,    "MO": "equal","CDA": "not-sent"},
      {"FID": "COAP.TYPE",                "MO": "ignore","CDA": "value-sent"},
      {"FID": "COAP.TKL",                 "MO": "ignore","CDA": "value-sent"},
      {"FID": "COAP.CODE",                "MO": "ignore","CDA": "value-sent"},
      {"FID": "COAP.MID",                 "MO": "ignore","CDA": "value-sent"},
      {"FID": "COAP.TOKEN",                 "MO": "ignore","CDA": "value-sent"},
      {"FID": "COAP.Uri-Path", "FL": "var", "FP": 1, "DI": "UP", "TV": "foo","MO": "equal","CDA": "not-sent"},
      {"FID": "COAP.Uri-Path", "FL": "var", "FP": 2, "DI": "UP", "TV": ["bar", "toto"] ,"MO": "match-mapping","CDA": "mapping-sent"},
      {"FID": "COAP.Uri-Path", "FL": "var", "FP": 3, "DI": "UP",             "MO": "ignore","CDA": "value-sent"},
      {"FID": "COAP.Uri-Path", "FL": "var", "FP": 4, "DI": "UP",             "MO": "ignore","CDA": "value-sent"},
      
      {"FID": "COAP.Content-Format",                  "DI": "DW", "TV": 30, "MO": "equal", "CDA": "not-sent"}
    ]
}

rm.Print()    
def processPkt(pkt):
    global parser
    global rm
    
    # look for a tunneled SCHC pkt

    if pkt.getlayer(Ether) != None: #HE tunnel do not have Ethernet
        e_type = pkt.getlayer(Ether).type
        if e_type == 0x0800:
            ip_proto = pkt.getlayer(IP).proto
            if ip_proto == 17:
                udp_dport = pkt.getlayer(UDP).dport
                if udp_dport == socket_port: # tunnel SCHC msg to be decompressed
                    print ("tunneled SCHC msg")

                    pkt.show()
                    
                    schc_pkt, addr = tunnel.recvfrom(2000)
                    device_id = "udp:"+addr[0]+":"+str(addr[1])
                    print ("donnee recupere",binascii.hexlify(schc_pkt), addr, device_id)
                    print("packet schc recupere",schc_pkt)
                    
                   

                    schc_bb = BitBuffer(schc_pkt)
                    #print("bitbuffer",schc_bb)
                    #print("bytes",bytes(schc_pkt))
                    #print("bytearray",bytearray(schc_pkt))
                    #schc=bytearray(schc_pkt)
                    #print("bytearray2",bytearray(schc_bb))
                    rule = rm.FindRuleFromSCHCpacket(schc_bb)
                    print("--------------REGLE DE DECOMPRESSION RETROUVE-------------- ")

                    print (rule,"\n\n")
                    if rule != None:
                        print("----------LA DECOMPRESSION------------")
                        phd = decomp.decompress(schc_bb, rule, recv_dir)
                        print ("le paquet décompressé \n",phd)
                     
                        print("Taille de l'en-tête du paquet: ",len(phd)+1)
                        #send_scapy(phd, schc_bb, rule)
                    else:
                        print ("unknown rule")
        
    elif pkt.getlayer(IP).version == 6 : # regular IPv6trafic to be compression

        pkt_fields, data, err = parse.parse( bytes(pkt), T_DIR_DW, layers=["IP", "ICMP"], start="IPv6")
        print (pkt_fields)

        if pkt_fields != None:
            rule, device = rm.FindRuleFromPacket(pkt_fields, direction=T_DIR_DW, failed_field=True)
            if rule != None:
                schc_pkt = comp.compress(rule, pkt_fields, data, T_DIR_DW)
                if device.find("udp") == 0:
                    destination = (device.split(":")[1], int(device.split(":")[2]))
                    print (destination)
                    schc_pkt.display()
                    tunnel.sendto(schc_pkt._content, destination)
                else:
                    print ("unknown connector" + device)
    else:
     print (".", end="", flush=True)           
                    
        
# look at the IP address to define sniff behavior

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]


print ("core role")
send_dir = T_DIR_DW
recv_dir = T_DIR_UP

socket_port = 0x5C4C

tunnel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tunnel.bind(("0.0.0.0", 0x5C4C))

sniff(prn=processPkt, iface=["he-ipv6", "ens3"])
