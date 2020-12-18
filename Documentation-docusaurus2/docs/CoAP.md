---
id: coap
sidebar_label: CoAP
title: Constrained Application Protocol (CoAP)
---

Le protocole CoAP est un protocole de transfert Web spécialisé destiné à être utilisé avec des nœuds contraints et des réseaux contraints (par exemple, à faible puissance ou avec perte). 
Les nœuds ont souvent des microcontrôleurs 8 bits avec de petites quantités de ROM et de RAM, tandis que les réseaux contraints tels que IPv6 sur les réseaux personnels sans fil à faible puissance (6LoWPAN) ont souvent des taux d'erreur de transmission de paquets élevés et un débit typique de 10 kbit / s. 
Le protocole est conçu pour les applications de machine à machine (M2M) telles que l'énergie intelligente et l'automatisation des bâtiments.

CoAP fournit un modèle d'interaction demande / réponse entre les points de terminaison d'application, prend en charge la découverte intégrée des services et des ressources et inclut des concepts clés du Web tels que les URI et les types de médias
Internet. CoAP est conçu pour s'interfacer facilement avec HTTP pour une
intégration avec le Web tout en répondant à des exigences spécifiques telles que laprise en charge de la multidiffusion, une surcharge très faible et la simplicité pour les
environnements contraints.

## CoAP/HTTP
Une requête CoAP est équivalente à celle de HTTP et est envoyée par un client pour demander une action (à l'aide d'un code de méthode) sur une ressource (identifiée par un URI) sur un serveur. 
Le serveur envoie ensuite une réponse avec un code de réponse. Cette réponse peut inclure une représentation de ressource.

Contrairement à HTTP, CoAP traite ces échanges de manière asynchrone sur un
transport orienté datagramme tel que UDP. Cela se fait de manière logique en
utilisant une couche de messages qui prend en charge la fiabilité facultative (avec recul exponentiel). 
CoAP définit quatre types de messages:

- Confirmable
- Non confirmable
- Acquittement
- Reset
    
Les codes de méthode et les codes de réponse inclus dans certains de ces messages les obligent à véhiculer des demandes ou des réponses.

### Confirmable Message
Certains messages nécessitent un accusé de réception. Ces messages sont appelés «confirmables».
Lorsqu'aucun paquet n'est perdu, chaque message Confirmable
suscite exactement un message de retour de type Accusé de réception ou de type Reset.

### Non-confirmable Message
Certains autres messages ne nécessitent pas d'acquittement. 
Cela est particulièrement vrai pour les messages qui sont répétés régulièrement pour les besoins de l'application, tels que les lectures répétées d'un capteur.

### Acknowledgement Message
Un message d'accusé de réception reconnaît qu'un message confirmable spécifique est arrivé. 
En lui-même, un message d'accusé de réception n'indique pas le succès ou l'échec d'une demande encapsulée dans le message de confirmation, mais le message d'accusé de réception peut également porter une réponse piggybacked .

### Reset Message
Un message de réinitialisation indique qu'un message spécifique (confirmable ou non confirmable) a été reçu, mais il manque du contexte pour le traiter correctement.
Cette condition se produit généralement lorsque le nœud de réception a redémarré et a oublié un état qui serait nécessaire pour interpréter le message. 
Provoquer un message de réinitialisation (par exemple, en envoyant un message vide confirmable) est également utile comme vérification peu coûteuse de la vivacité d'un point
d'extrémité ("CoAP ping").

## Messaging Model
CoAP utilise un en-tête binaire court de longueur fixe (4 octets) qui peut être suivi d'options binaires compactes et d'une charge utile. 
Ce format de message est partagé par les demandes et les réponses. 
Le format de message CoAP est spécifié dans lasection 3. Chaque message contient un ID de message utilisé pour détecter les doublons et pour une fiabilité facultative.
(L'ID de message est compact; sa taille de 16 bits permet jusqu'à environ 250 messages par seconde d'un point de terminaison à un autre avec les paramètres de protocole par défaut.)

La fiabilité est fournie en marquant un message comme confirmable (CON). 
Un message confirmable est retransmis en utilisant un délai d'expiration par défaut et une interruption exponentielle entre les retransmissions, jusqu'à ce que le destinataire envoie un message d'accusé de réception (ACK) avec le même ID de message (dans cet exemple, 0x7d34) à partir du point d'extrémité correspondant; voir la figure 2.
Lorsqu'un destinataire n'est pas du tout capable de traiter un message confirmable (c'est-à-dire qu'il n'est même pas en mesure de fournir une réponse d'erreur appropriée), il répond par un message de réinitialisation (RST) au lieu d'un accusé de réception (ACK).

    Client              Serveur
       |                  |
       |   CON [0x7d34]   |
       +----------------->|
       |                  |
       |   ACK [0x7d34]   |
       |<-----------------+
       |                  |

    Figure 2: Reliable Message Transmission

Un message qui ne nécessite pas de transmission fiable (par exemple,
chaque mesure individuelle d'un flux de données de capteur) peut être envoyée sous
forme de message non confirmable (NON). Ceux-ci ne sont pas reconnus, mais ont
toujours un ID de message pour la détection des doublons (dans cet exemple,0x01a0); voir la figure 3. Lorsqu'un destinataire n'est pas en mesure de traiter un
message non confirmable, il peut répondre par un message de réinitialisation (RST).


    Client             Server
        |                  |
        |   NON [0x01a0]   |
        +----------------->|
        |                  |

    Figure 3: Unreliable Message Transmission

## Request/Response Mode
La sémantique de demande et de réponse CoAP est transportée dans les messages
CoAP, qui incluent respectivement un code de méthode ou un code de réponse. Les
informations de demande et de réponse facultatives (ou par défaut), telles que l'URI et
le type de support de charge utile, sont transmises en tant qu'options CoAP. Un jeton
est utilisé pour faire correspondre les réponses aux demandes indépendamment des
messages sous-jacents.

    Client            Server           Client               Server        
                                                                     
    |                  |                  |                  |             
    |   CON [0xbc90]   |                  |   CON [0xbc91]   |            
    | GET /temperature |                  | GET /temperature |                 
    |    (Token 0x71)  |                  |    (Token 0x72)  |           
    +----------------->|                  +----------------->|         
    |                  |                  |                  | 
    |   ACK [0xbc90]   |                  |   ACK [0xbc91]   |
    |   2.05 Content   |                  |   4.04 Not found |
    |   (Token 0x71)   |                  |   (Token 0x72)   |
    |     "22.5 C"     |                  |   "Not found"    |
    |<-----------------+                  |<-----------------+
    |                  |                  |                  | 
    Figure 4: Two GET Requests with Piggybacked Responses


→ Une demande est transportée dans un message confirmable (CON) ou non
confirmable (NON) et, si elle est immédiatement disponible, la réponse à une demandetransportée dans un message confirmable est transportée dans le message d'accusé de
réception (ACK) résultant. C'est ce qu'on appelle une réponse superposée.

```
Client             Server
   |                  |
   |  CON [0x7a10]    |
   | GET /temperature |
   |  (Token 0x73)    |
   +----------------->|
   |                  |
   |   ACK [0x7a10]   |
   |<-----------------+
   |                  |
   ... Time Passes  ...
   |                  |
   |   CON [0x23bb]   |
   |   2.05 Content   |
   |   (Token 0x73)   |
   |     "22.5 C"     |
   |<-----------------+
   |                  |
   |   ACK [0x23bb]   |
   +----------------->|
   |                  |
Figure 5: A GET Request with a Separate Response
```
→ Si le serveur n'est pas en mesure de répondre immédiatement à une demande portée
dans un message confirmable, il répond simplement avec un message d'accusé de
réception vide afin que le client puisse arrêter de retransmettre la demande. Lorsque la
réponse est prête, le serveur l'envoie dans un nouveau message Confirmable (qui à son
tour doit être acquitté par le client). C'est ce qu'on appelle une «réponse séparée»,
comme illustré à la figure 5.

```
Client             Server
   |                  |
   |   NON [0x7a11]   |
   | GET /temperature |
   |   (Token 0x74)   |
   +----------------->|
   |                  |
   |   NON [0x23bc]   |
   |   2.05 Content   |
   |   (Token 0x74)   |
   |     "22.5 C"     |
   |<-----------------+
   |                  |
Figure 6: A Request and a Response Carried in Non-confirmable Messages
```

Si une demande est envoyée dans un message non confirmable, la réponse est envoyé
à l'aide d'un nouveau message non confirmable, bien que le serveur puisse à la place,
envoyez un message confirmable. Ce type d'échange est illustré à la figure 6.


## Message Format
Les messages CoAP sont encodés dans un format binaire simple. Le format du message
commence par un en-tête de 4 octets de taille fixe :

```
0                  1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Ver| T | TKL |       Code     |          Message ID            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Token (if any, TKL bytes) ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Options (if any) ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|1 1 1 1 1 1 1 1|    Payload (if any) ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

                      Figure 7: Message Format
```
- Version (Ver): entier non signé 2 bits. 
Indique la version CoAP. 
Les implémentations de cette spécification DOIVENT mettre ce champ à 1 (01 binaire). 
Les autres valeurs sont réservées aux versions futures.
Les messages avec des numéros de version inconnus DOIVENT être ignorés en silence.

- Type (T): entier non signé 2 bits. Indique si ce message est de type:
    - Confirmable (0)
    - Non confirmable (1) 
    - Accusé de réception (2)
    - ou Réinitialiser (3)

- Token Length (TKL): entier non signé de 4 bits. 
Indique la longueur du champ Token:  0 à 8 octets. 
Les longueurs 9 à 15 sont réservées, NE DOIVENT PAS être envoyées
 et DOIVENT être traitées comme une erreur de format de message.

- Code: entier non signé de 8 bits, 
divisé en une classe de 3 bits (bits les plus significatifs) 
et un détail de 5 bits (bits les moins significatifs). 
Documenté comme "c.dd" où "c" est un chiffre de 0 à 7 pour le sous-champ à 3 bits 
et "dd" sont deux chiffres de 00 à 31 pour le sous-champ à 5 bits. 
La classe peut indiquer:
    - une demande (0)
    - une réponse de succès (2)
    - une réponse d'erreur client (4) 
    - ou une réponse d'erreur serveur (5) 
    - Toutes les autres valeurs de classe sont réservées.
Dans un cas particulier, le code 0.00 indique un message vide.
En cas de demande, le champ Code indique la méthode de demande; 
en cas de réponse, un code de réponse. 
Les valeurs possibles sont conservées dans les registres de codes CoAP. 

- ID de message: entier non signé 16 bits dans l'ordre des octets du réseau. 
Utilisé pour détecter la duplication des messages et pour faire correspondre les messages de type Accusé de réception / Réinitialisation aux messages de type Confirmable / Non
confirmable. 


L'en-tête est suivi de la valeur Token, qui peut être comprise entre 0 et 8 octets,
comme indiqué par le champ Token Length. La valeur Token est utilisée pour corréler
les demandes et les réponses.

L'en-tête et le jeton sont suivis de zéro ou plusieurs options. 
Une option peut être suivie de la fin du message, d'une autre option ou du marqueur de
charge utile et de la charge utile.

Après l'en-tête, le jeton et les options, le cas échéant, vient la charge utile facultative. S'il
est présent et de longueur non nulle, il est préfixé par un marqueur de charge utile fixe
d'un octet (`0xFF`), qui indique la fin des options et le début de la charge utile. 
Les données de charge utile s'étendent après le marqueur jusqu'à la fin du datagramme UDP,
c'est-à-dire que la longueur de la charge utile est calculée à partir de la taille du
datagramme. 
L'absence du marqueur de charge utile indique une charge utile de
longueur nulle. 
La présence d'un marqueur suivi d'une charge utile de longueur nulle
DOIT être traitée comme une erreur de format de message.

Un message vide a le champ Code défini sur 0,00. Le champ Token Length DOIT
être mis à 0 et les octets de données NE DOIVENT PAS être présents après le champ
Message ID. S'il y a des octets, ils DOIVENT être traités comme une erreur de format
de message.


## Message transmitted reliably
La transmission fiable d'un message est initiée en marquant le message comme
confirmable dans l'en-tête CoAP. Un message confirmable porte toujours une requête
ou une réponse, sauf si elle est utilisée uniquement pour obtenir un message de
réinitialisation, auquel cas il est vide. Un destinataire DOIT soit :

- (a) accuser réception d'un message confirmable avec un Message d'accusé de réception

- (b) rejeter le message si le destinataire manque de contexte pour traiter correctement le
message, y compris les situations où le message est vide, utilise un code avec une classe
réservée (1, 6,ou 7), ou présente une erreur de format de message. Rejeter une
confirmation message est effectué en envoyant un message de réinitialisation
correspondant → et autrement l'ignorer.

Le message d'accusé de réception DOIT faire écho à l'ID de message de le
message confirmable et DOIT porter une réponse ou être vide.Le message de
réinitialisation DOIT faire écho au message ID du message confirmable et DOIT être
vide.

Rejeter un Message d'accusé de réception ou de réinitialisation (y compris le cas où
l'accusé de réception porte une requête ou un code avec une classe réservée, ou le
message de réinitialisation n'est pas vide) est effectué en l'ignorant silencieusement.
Plus généralement, les destinataires des messages d'accusé de réception et de
réinitialisation DOIVENT NE répond PAS avec des messages d'acquittement ou de
réinitialisation.

L'expéditeur retransmet le message Confirmable à intervalles augmentant d façon
exponentielle , jusqu'à ce qu'il reçoive un acquittement (ou Reset message) ou manque
de tentatives.

La retransmission est contrôlée par deux choses qu'un point d'extrémité CoAP DOIT
garder une trace de chaque message confirmable qu'il envoie en attendant un accusé de
réception (ou une réinitialisation): un délai d'expiration et un compteur de
retransmission. Pour un nouveau message confirmable, le délai initial est défini sur
une durée aléatoire (souvent non un nombre entier de secondes) entre
`ACK_TIMEOUT` et (`ACK_TIMEOUT * ACK_RANDOM_FACTOR`), et le compteur de retransmission est mis à 0. 
Lorsque le délai d'expiration est
déclenché et le compteur de retransmission est inférieur à `MAX_RETRANSMIT`, le
message est retransmis, le compteur de retransmission est incrémenté et le délai est
doublé. Si le compteur de retransmission atteint `MAX_RETRANSMIT` lors d'un
dépassement de délai, ou si le point d'extrémité reçoit un message de réinitialisation,
alors la tentative de transmission du message est annulée et le processus d'application
informé de l'échec. En revanche, si l'extrémité reçoit un accusé de réception à temps, la
transmission est considérée comme réussie.

Un point d'extrémité CoAP qui a envoyé un message Confirmable PEUT renoncer à
tenter d'obtenir un ACK avant même que la valeur du compteur `MAX_RETRANSMIT` ne soit atteinte. 
Par exemple, l'application a annulé la demande car elle n'a plus besoin de réponse, ou il y a une autre indication que le message CON
est arrivé. 
En particulier, un message de demande CoAP peut avoir suscité une réponse
distincte, auquel cas il est clair pour le demandeur que seul l'ACK a été perdu et qu'une
retransmission de la demande ne servirait à rien. Cependant, un répondeur NE DOIT
PAS à son tour s'appuyer sur ce comportement intercouche d'un demandeur, c'est-à-dire
qu'il DOIT conserver l'état pour créer l'ACK pour la demande, si nécessaire, même si
une réponse Confirmable a déjà été acquittée par le demandeur. Une autre raison
d'abandonner la retransmission PEUT être la réception d'erreurs ICMP.

"*" signifie que la combinaison n'est pas utilisée en temps normal mais seulement pour provoquer un message Reset
("CoAP ping").

```
+----------+-----+-----+-----+-----+
|          | CON | NON | ACK | RST |
+----------+-----+-----+-----+-----+
| Request  | X   | X   | -   | -   |
| Response | X   | X   | X   | -   |
| Empty    | *   | -   | X   | X   |
+----------+-----+-----+-----+-----+
Table 1: Usage of Message Types
```

