---
id: schc
title: Présentation SCHC
sidebar_label: SCHC
slug: /
---

Les objets connectés sont généralement très limités en terme de bande-passante.
Les en-têtes représentent alors une proportion non négligeable de la taille totale pouvant être envoyée.
La taille maximale des paquets pouvant être envoyés sur le réseau (la *MTU*) peut également être très limité.

**SCHC** pour *Static Context Header Compression* (prononcer "chic") est une technologie dont le but est de palier à ces problème.

Pour une présentation complète de SCHC, se référer à la [RFC 8724](liens) dont sont inspirés les schémas.


# Le principe de SCHC
SCHC possède 2 fonctions principales: la Compression et la Fragmentation

## Compression
SCHC est intéressant dans les situations où la taille des paquets pouvant être envoyés est limitée. 

Les en-têtes décrits par la suite concernent la concaténation d'en-têtes protocolaires de la couche Réseau à la couche Application.
Cette concaténation d'en-têtes pour le paquet devant être envoyé sera défini par "en-tête original". 

La compression par SCHC peut être présentée grossièrement de la manière suivante (les termes techniques utilisés seront décrits dans la suite): 
- Un en-tête ou un ensemble d'en-tête est décrit par une *Rule*.

- Une liste de toutes les Rules est construite. Cette liste est appelé un *Context*. L'émetteur et le récepteur connaissent tous deux le Context. 

- A chaque Rule est associé un numéro, le *RuleID*.

- Lorsqu'un émetteur veut envoyer un paquet IP, il envoie le RumlID de la Rule associée au paquet qu'il compte envoyer suivi de la charge utile.

- Le récepteur récupère le RuleID et la charge utile. Grâce au Context il peut reconstituer l'en-tête original: c'est l'étape de décompression. Dans le cas où la Rule décrit un ensemble d'en-têtes, des données supplémentaires sont envoyées par l'émetteur pour lever l'ambiguïté lors de la reconstitution de l'en-tête. Ces données supplémentaires forment le *Compression Residue*.

On obtient alors un paquet dont l'en-tête est bien plus léger.

                       +--------------------------------------------- ... --------+--------------+
	Avant compression  |                  En-tête original                        | Charge utile |
	                   +--------------------------------------------- ... --------+--------------+


	                   |------- En-tête compressé -------|
	                   +---------------------------------+--------------+
	Après compression  | RuleID |  Compression Residue   | Charge utile |
	                   +---------------------------------+--------------+    

    Schéma d'un paquet avant et après compression SCHC
  
  

La suite décrit les différents termes utilisés.

### Context
Il s'agit d'une liste de Rules partagée par l'émetteur et le récepteur.

### Rule
Une Rule est divisée en différentes lignes appelées *Field*, chacune divisée en sections que nous définissons plus bas.
Chaque Field étudie un champ de l'en-tête originale.


    /-----------------------------------------------------------------\
    | (FID)                   Rule 12                                 |
    |+-------+--+--+--+------------+-----------------+---------------+|
    ||Field 1|FL|FP|DI|Target Value|Matching Operator|Comp/Decomp Act||
    |+-------+--+--+--+------------+-----------------+---------------+|
    ||Field 2|FL|FP|DI|Target Value|Matching Operator|Comp/Decomp Act||
    |+-------+--+--+--+------------+-----------------+---------------+|
    ||...    |..|..|..|    ...     | ...             | ...           ||
    |+-------+--+--+--+------------+-----------------+---------------+|
    ||Field N|FL|FP|DI|Target Value|Matching Operator|Comp/Decomp Act||
    |+-------+--+--+--+------------+-----------------+---------------+|
    |                                                                 |
    \-----------------------------------------------------------------/

    Représentation schématique d'une Rule

### Field Identifier (*FID*)
Il s'agit de la première colonne d'un Field. Elle permet de connaître le champ de l'en-tête originale traité. Elle l'identifie par un protocole et un champ.

Ex: `UDP.Length`, `IPv6.version`, `CoAP.TKL`

Dans la suite "ce champ" fera référence au champ décrit dans cette section.

### Field Length (*FL*)
Désigne la longueur de ce champ dans l'en-tête original. Il peut s'agir d'un entier désignant la taille en bits ou d'un type de variable dont la taille désigne


### Field Position (*FP*)
Dans certains protocoles, il peut y avoir plusieurs champs avec le même nom (Ex: `Coap.Uri-Path`). Cette section permet d'éviter les ambiguïtés.

### Direction Indicator (*DI*)
Peut prendre 3 valeurs:
- `Up`: La Rule n'est à considérer que dans le cas d'un paquet dont l'émetteur est l'objet connecté

- `Down`: La Rule n'est à considérer que dans le cas d'un paquet dont le récepteur est l'objet connecté

- `Bi`: Est sexuellement attiré par les deux sexes

### Target Value (*TV*)
Les 3 dernières sections sont très liées. Les descriptions de chacune font référence aux autres.

Il y a 3 situations possibles pour cette section:
- __Cette section est vide__: le contenu de ce champ dans l'en-tête original n'entre pas en jeu dans le choix de la Rule. Il sera intégralement renvoyé et éventuellement recalculé selon les cas. La section *MO* doit contenir `Ignore`.

- __Cette section contient une valeur__: le contenu de ce champ dans l'en-tête original sera comparé à cette valeur selon la fonction de comparaison indiquée dans la section *MO* (`Equal` ou `MSB(x)`). La section *TV* contient alors un entier ou une chaîne de caractère.

- __Cette section contient un tableau__: si le contenu de ce champ dans l'en-tête original correspond à l'une des valeurs du tableau, alors l'indice du tableau associé à cette valeur sera renvoyé. La section *MO* doit contenir `Match-mapping`.


### Matching Operator (*MO*)
Il s'agit de la fonction de comparaison. Il y a 5 valeurs possibles:
- `Ignore`: Renvoie toujours `True`. Cela signifie que ce champ n'est pas pris en compte dans le choix de la Rule. La section *CDA* contiendra `Value-sent` ou `Compute-*`, sauf exception.

- `Equal` : Renvoie `True` si la valeur dans la section *TV* et la valeur de ce champ dans l'en-tête original sont égales et `False` sinon. La section *CDA* doit contenir la valeur `Not-sent`.

- `Most Significant Bits(x)` ou `MSB(x)`: Renvoie `True` si les `x` premiers bits de la valeur dans la section *TV* et de la valeur de ce champ dans l'en-tête original sont égales et `False` sinon. La section *CDA* doit contenir `LSB`.

- `Match-mapping`: Renvoie `True` si la valeur de ce champ dans l'en-tête original appartient au tableau présent dans la section *TV* et `False` sinon. La section *CDA* doit contenir `Mapping-sent.`

Pour qu'une Rule soit retenue, pour chaque Field, le test réalisé doit renvoyer `True`.

### Compression/Decompression Action (*CDA*)
Cette section détermine le contenu du Compression Residue associé au Field. Ces actions ne sont réalisées que si la Rule a été retenue au préalable. Il y a 5 valeurs possibles:
- `Not-sent` : Aucun Compression Residue associé à ce Field ne sera envoyé. La seule connaissance de la Rule doit permettre de retrouver cette valeur. La section *MO* contient alors `Equal`, sauf exceptions.

- `Value-sent` : La valeur de ce champ dans l'en-tête original est entièrement envoyée.

- `Least Significant Bits` ou `LSB` : La section *MO* contient `MSB(x)`. On note `n` le nombre de bits de la valeur de ce champ dans l'en-tête original. Dans ce cas, on envoie les `n-x` derniers bits de la valeur de ce champ dans l'en-tête original. On peut reconstituer cette valeur lors de la décompression en concaténant les `x` premiers bits de la valeur dans la section *TV* avec le contenu du Compression Residu

- `Mapping-sent` : On renvoie l'indice du tableau présent dans la section *TV* associé à la valeur de ce champ dans l'en-tête original.

- `Compute-*` : La valeur de ce champ dans l'en-tête original sera recalculée lors de la décompression. Il s'agit par exemple de longueurs (`Compute-length`) ou de sommes de contrôle (`Compute-checksum`).
---

## Fragmentation
Malgré la compression décrite précédemment, il peut arriver que la MTU soit si faible que cela ne suffisse pas.
SCHC permet d'envoyer la charge utile en plusieurs paquets: c'est la *fragmentation*.

### Le découpage
On considère un paquet SCHC (donc après compression) que l'on découpe.

#### Tile
Chacune des partie obtenue constitue une *Tile*.

Les Tiles forment une partition du paquet SCHC: elles sont non-vides, deux à deux disjointes et on retrouve le paquet SCHC initial en les concaténant dans le bon ordre.

Les conditions sur la taille des Tiles dépendent du mode d'acquittement.

Leur numérotation sera décrit dans la sous-section suivante

                          Paquet SCHC
          +---+-------+---------+----+ ... ---+------+
    Tiles |   |       |         |    |        |      |
          +---+-------+---------+----+ ... ---+------+

          Schéma de fragmentation en Tiles


#### Window
Une *Window* est une groupe de Tiles consécutives vérifiant les propriétés suivantes:
- Chaque Window,à l'exception de la dernière, doit contenir le même nombre de Tiles. Dans la suite, on note `WINDOW_SIZE` ce nombre.
- La dernière Window doit contenir `WINDOW_SIZE` Tiles ou moins.
- Les Windows sont numéroté dans l'ordre croissant à partir de 0 en partant du début du paquet.
- Dans chaque Window, les Tiles sont numérotées dans l'ordre décroissant à partir de `WINDOW_SIZE - 1` en partant du début de la Window.

```
                                            Paquet SCHC
            +-+---+-+---+---+---+-----+---+-+---+---+---+---+---+ ... ----+-+---+---+---+-+---+
            | |   | |   |   |   |     |   | |   |   |   |   |   |         | |   |   |   | |   |
            +-+---+-+---+---+---+-----+---+-+---+---+---+---+---+ ... ----+-+---+---+---+-+---+

    Tile#   |4| 3 |2| 1 | 0 | 4 |  3  | 2 |1| 0 | 4 | 3 | 2 | 1 |  ...    |2| 1 | 0 | 4 |3| 2 |
    Window# |------ 0 ------|-------- 1 --------|------- 2 ------- ... -- 8 --------|--- 9 ---|  

    Schéma de fragmentation en Windows
```


### Fragment SCHC

```
|-- En-tête de Fragment SCHC -|
          |-- T --|-M-|-- N --|
+-- ... --+- ... -+---+- ... -+------- ... ------+-------------------------
| RuleID  | DTag  | W |  FCN  |   Charge utile   | padding (si nécessaire) 
+-- ... --+- ... -+---+- ... -+------- ... ------+-------------------------

Schéma d'un Fragment SCHC standard
```
```
|-- En-tête de Fragment SCHC -|
          |-- T --|-M-|-- N --|-- U --|
+-- ... --+- ... -+---+- ... -+- ... -+------- ... ------+-------------------------
| RuleID  | DTag  | W | 11..1 |  RCS  |   Charge utile   | padding (si nécessaire) 
+-- ... --+- ... -+---+- ... -+- ... -+------- ... ------+-------------------------

Schéma d'un Fragment SCHC All-1
```


#### RuleID
#### Datagram Tag (*DTag*)
#### W
#### Fragment Compressed Number (*FCN*)
#### Reassembly Check Sequence (*RCS*)


### Acquittement SCHC
```
|--- SCHC ACK Header ----|--------     Bitmap     --------|
         |-- T --|-M-| 1 |
+-- ... -+- ... -+---+---+---------------------------------+
| RuleID |  DTag | W |C=0|1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1|
+-- ... -+- ... -+---+---+---------------------------------+

Schéma d'un Acquittement (ACK) SCHC
```
#### Compressed Bitmap
On associe à chaque Window une suite de bits dont la taille correspond à son nombre de Tiles. Cette suite de bits est appelée *Bitmap*. Chaque bit est associé à une Tile. Le bit le plus à gauche est associé à la Tile de numéro `WINDOW_SIZE - 1`. Le deuxième bit en partant de la gauche est associé à la Tile de numéro `WINDOW_SIZE - 2`. Et ainsi de suite.

Il s'agit d'un message pouvant être envoyé par la récepteur pour savoir si les Tiles ont été correctement reçues. Pour chaque Tile, la Bitmap associe `1` si la Tile a été correctement reçue et `0` sinon.

Par exemple, pour une Window n'étant pas la dernière, `11101` signifie que sur les 5 Tiles que contient cette Window, seule celle de numéro 1 n'a pas été reçue correctement.



### Les modes d'acquittement
#### No-Ack
- Chaque Fragment contient 1 Tile dans sa charge utile.

- Les Fragments sont envoyés mais aucun acquittement n'est envoyé.

- Les Windows ne sont pas utilisées

- Les Tiles n'ont pas nécéssairement la même taille.

- A l'exception de la dernière, les Tiles doivent avoir une taille telle qu'il n'y ait pas besoin de padding

- Les Fragment sont envoyés de dans l'ordre, celui portant le début du paquet original est envoyé en premier.

#### Ack-Always

- Chaque Fragment contient 1 Window dans sa charge utile.

- Un ACK positif ou négatif est émis par le récepteur après l'envoi de chaque Window.

- Les Windows sont utilisées.

- Les Tiles n'ont pas nécessairement la même taille.

- A l'exception de la dernière, les Tiles doivent avoir une taille telle qu'il n'y ait pas besoin de padding

#### Ack-on-Error

- Chaque Fragment contient 1 Window dans sa charge utile.

- Les Windows sont utilisées

- A l'exception des 2 dernières, les Tiles doivent avoir la même taille.

-
---
