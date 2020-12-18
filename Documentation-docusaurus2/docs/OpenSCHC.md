---
id: openschc
title: OpenSCHC
---

Il s'agit d'une implémentation Python de [SCHC](.). 

# Description du projet
Ce projet vient répondre au besoin de mise à jour régulière, de la gestion des autorisations et des authentifications pour la sécurisation des objets connectés.

Pour ce faire, nous avons réalisé notre objet connecté constitué des éléments suivants : 
- Un Pycom LoPy4 pour tester notre capteur sur différents réseaux (LoRa, SigFox, Wifi, Bluetooth)
- Un capteur BME280 pour recueillir la température, la pression et l'humidité de l'air
- Une Antenne LoRa 868 MHz pour l'émission et la réception LoRa

L'émission et la réception des données :  
- Un serveur réseau LoRa pour communiquer avec les serveurs applicatifs
- Un serveur d'application (Serveur CoAP) qui contient les ressources et les données transmises par l'objet connecté

# Description du code
Les différents programmes (python) utilisés:
- `BME280.py`,  pour lire les données que renvoie le capteur notamment la température, la pression et l'humidité de l'air

- `join.py`,  pour tester la connexion au serveur réseau LoRa (LNS, LoRa Network Server)
```python
from network import LoRa
import time
import pycom
import binascii


lora = LoRa(mode=LoRa.LORAWAN)


# create an OTAA authentication parameters
app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))


pycom.heartbeat(False)
pycom.rgbled(0x111111)

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

pycom.rgbled(0x000000)

```

- `SendAndReceive.py`, pour tester l'émission des données depuis le pycom et la réception des réponses du serveur de ressource

- `CBOR.py`,   pour la sérialisation des données en [CBOR](cbor), du binaire voire des données transmises en hexadécimal

- `CoAP.py`,   pour la définition des standards [CoAP](coap) et des classes en vue de la communication client-serveur

- `send-coap-TPH.py`,  pour l'émission des données vers le serveur CoAP avec l'URI le chemin menant à la ressource TPH (Température-Pression-Humidité)

- `icmp.json`, pour la description des Rules. En voici un exemple

```js
"RuleID": 6,
	    "RuleIDLength": 3,
	    "Compression": [
		{"FID": "IPV6.VER",                   "TV": 6,                        "MO": "equal",  "CDA": "not-sent"},
		{"FID": "IPV6.TC",                    "TV": 0,                        "MO": "equal",  "CDA": "not-sent"},
		{"FID": "IPV6.FL",                    "TV": 0,                        "MO": "ignore", "CDA": "not-sent"},
		{"FID": "IPV6.LEN",                                                   "MO": "ignore", "CDA": "compute-length"},
		{"FID": "IPV6.NXT",                   "TV": 58,                       "MO": "equal",  "CDA": "not-sent"},
		{"FID": "IPV6.HOP_LMT",               "TV": 255,                      "MO": "ignore", "CDA": "not-sent"},
		{"FID": "IPV6.DEV_PREFIX",            "TV": "2001:470:1F21:1D2::/64", "MO": "equal",  "CDA": "not-sent"},
		{"FID": "IPV6.DEV_IID",               "TV": "::1",                    "MO": "equal",  "CDA": "not-sent"},
		{"FID": "IPV6.APP_PREFIX",                                            "MO": "ignore", "CDA": "value-sent"},
		{"FID": "IPV6.APP_IID",                                               "MO": "ignore", "CDA": "value-sent"},
		{"FID": "ICMPV6.TYPE",    "DI": "DW", "TV": 128,                      "MO": "equal",  "CDA": "not-sent"},
		{"FID": "ICMPV6.TYPE",    "DI": "UP", "TV": 129,                      "MO": "equal",  "CDA": "not-sent"},
		{"FID": "ICMPV6.CODE",                "TV": 0,                        "MO": "equal",  "CDA": "not-sent"},
		{"FID": "ICMPV6.CKSUM",               "TV": 0,                        "MO": "ignore", "CDA": "compute-checksum"},
		{"FID": "ICMPV6.IDENT",               "TV": 0,                        "MO": "ignore", "CDA": "value-sent"},
		{"FID": "ICMPV6.SEQNO",               "TV": 0,                        "MO": "ignore", "CDA": "value-sent"}
	    ]
```

Ces programmes permettent en quelque sorte au Pycom (le client) d'envoyer les données sérialisées en CBOR du capteur BME280 vers 
le serveur de ressource en utilisant le protocole d'application CoAP et le reseau LoRa.

- 

```python
from network import LoRa
import pycom
#
lora = LoRa(mode=LoRa.LORAWAN)
mac = lora.mac()
#
print ('devEUI: ',  end='')
#
for i in range (0,  8):
        print(hex(mac[i]), end='-')
#
print ()
```

