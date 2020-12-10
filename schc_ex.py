import sys, getopt
sys.path.append('/home/silhack/Documents/ProjetS3/openschc/src')

import os 

from net_udp_core import  *
from gen_base_import import b2hex
from compr_core import * #module d'implementation des actions dans les regles chosies au niveau du core du reseau
from compr_parser import * #module permettant de faire correspondre les entetes du paquet à leur valeur
from gen_rulemanager import * #le gestionnaire des regles de copression et de fragmentation

class debug_protocol:
    def _log(*arg):
        print(*arg)
#paquet ip brut
coap_ip_packet = bytearray(b"""`\
\x12\x34\x56\x00\x1e\x11\x1e\xfe\x80\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\xfe\x80\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x02\x16\
2\x163\x00\x1e\x00\x00A\x02\x00\x01\n\xb3\
foo\x03bar\x06ABCD==Fk=eth0\xff\x84\x01\
\x82  &Ehello""")

#parse the packet 
p = Parser(debug_protocol)
v= p.parse(coap_ip_packet , T_DIR_UP) #on parse en spécifiant la direction de la transmission
C = Compressor(debug_protocol)#instanciation de l'objet compression

RM = RuleManager(debug_protocol)
RM.Add(file="../configs/comp-rule-100.json") #ajout d'un fichier contenant des règles de fragmentations et de compessions
r1 = RM.FindRuleFromPacket(v[0],direction="UP") #recherche automatique de la regle de compression convenable au paquet

if r1 != None:
    schc_packet = C.compress(r1, v[0], v[1], T_DIR_UP) #compression
    print('entete compressé',schc_packet)
    print('taille de header compressé',schc_packet.get_length())
    
