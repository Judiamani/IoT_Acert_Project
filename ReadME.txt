*****************************Maquette technologique en vue de la sécurisation d'un objet médical connecté - SCHC*****************************

Ce projet vient répondre au besoin de mise à jour régulière, de la gestion des autorisations et des authentifications pour la sécurisation des objets connectés.

Pour ce faire, nous avons réalisé notre objet connecté constitué des éléments suivants : 
- Un Pycom LoPy4 pour tester notre capteur sur différents réseaux (LoRa, SigFox, Wifi, Bluetooth)
- Un capteur BME280 pour recueillir la température, la pression et l'humidité de l'air
- Une Antenne LoRa 868 MHz pour l'émission et la réception LoRa

L'émission et la réception des données :  
- Un serveur réseau LoRa pour communiquer avec les serveurs applicatifs
- Un serveur d'application (Serveur CoAP) qui contient les ressources et les données transmises par l'objet connecté

Les différents programmes (python) utilisés:
- BME280.py,                     pour lire les données que renvoie le capteur notamment la température, la pression et l'humidité de l'air
- join.py,                             pour tester la connexion au serveur réseau LoRa (LNS, LoRa Network Server)
- SendAndReceive.py,         pour tester l'émission des données depuis le pycom et la réception des réponses du serveur de ressource
- CBOR.py,                        pour la sérialisation des données en CBOR, du binaire voire des données transmises en hexadécimal
- CoAP.py,                         pour la définition des standards CoAP et des classes en vue de la communication client-serveur
- send-coap-TPH.py,          pour l'émission des données vers le serveur CoAP avec l'URI le chemin menant à la ressource TPH (Température-Pression-Humidité)

Ces programmes permettent en quelque sorte au Pycom (le client) d'envoyer les données sérialisées en CBOR du capteur BME280 vers 
le serveur de ressource en utilisant le protocole d'application CoAP et le reseau LoRa.
