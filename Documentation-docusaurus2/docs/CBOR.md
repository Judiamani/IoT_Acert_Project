---
id: cbor
sidebar_label: CBOR
title: Concise Binary Object Representation (CBOR)
---

L’octet initial de chaque data item contient des informations sur :
- le Major Type : 3 bits de point fort
- des informations supplémentaires:5 bits de poids faible 

## Major Type 0 : Unsigned integer
Les informations supplémentaires sont soit l’entier lui-même ( pour des valeurs entre 0 et 23) soit la longueur des données; 
une information supplémentaire de 24 signifie que la valeur est représentée dans 1 `uint8_t` (1 octet),  25 signifie que la valeur est représentée dans 2 octets ainsi de suite...

<u> Exemple </u> :

`10` est désigné par `0b000_01010`

`500` serait `0b000_11001` suivi des deux octets `0x01f4` qui vaut `500` en décimal.


## Major Type 1 : Negative integer
Même règles que celles du Major Type 0, sauf que la valeur est -1 moins l’entier non signé codé.

<u> Exemple </u> :

`500` serait `0b000_11001` suivi des deux octets `0x01f3` qui vaut `499` en décimal.


## Major Type 2 : Byte String
L’information supplémentaire correspond à la longueur des données.

<u> Exemple </u> :

Un byte string de longueur 5 serait désignée par `0b010_00101` suivi des 5 octets du contenu binaire.


## Major Type 3: Text string , une chaîne de caractères Unicode codé en UTF-8
Même chose que String byte. 
Ce type est fourni pour les systèmes qui doivent interpréter ou afficher des octets non structurés et du texte ayant un répertoire et un codage spécifiés.

Contrairement aux formats tels que JSON, les caractères Unicode de ce type ne sont jamais échappés. 
Ainsi, un caractère de nouvelle ligne (U + 000A) est toujours représenté dans une chaîne comme l'octet `0x0a`, et jamais comme les octets `0x5c6e` (les caractères `\` et `n`) ou comme
`0x5c7530303061` (les caractères `\`, `u `, `0`, `0`, `0` et `a`).


## Major Type 4: Array of data items
Les tableaux sont également appelés listes, séquences ou tuples. La longueur du tableau suit les
règles pour les chaînes d'octets (type majeur 2), sauf que la longueur indique le nombre d'éléments
de données, et non la longueur en octets que le tableau occupe. Les éléments d'un tableau n'ont pas
besoin d'être tous du même type.

<u> Exemple </u> :

Un tableau qui contient 10 éléments de tout type aurait un octet initial de `0b100_01010` (type
principal de 4, informations supplémentaires de 10 pour la longueur) suivi des 10 éléments
restants. 

```
[1, [2, 3], [4, 5]] → 0x8301820203820405
```


## Major Type 5 :Map of pairs of data items
Les maps sont également appelées tables, dictionnaires, hachages ou objets (en JSON). Une map
est composée de paires d'éléments de données, chaque paire étant constituée d'une clé
immédiatement suivie d'une valeur. La longueur de la carte suit les règles pour les chaînes d'octets
(type majeur 2), sauf que la longueur indique le nombre de paires, et non la longueur en octets que
la map occupe.

<u> Exemple </u> :

Une map qui contient 9 paires aurait un octet initial de 0b101_01001 (type principal de 5,
informations supplémentaires de 9 pour le nombre de paires) suivi des 18 éléments restants. Le
premier élément est la première clé, le deuxième élément est la première valeur, le troisième
élément est la deuxième clé, et ainsi de suite.

```
{"Fun": true, "Amt": -2} → 0xbf6346756ef563416d7421ff (map indéfinie)
```

Une carte qui a des clés en double peut être bien formée, mais elle n'est pas valide, et donc elle
provoque un décodage indéterminé; voir également


## Major Type 5: Optional semantic tagging for other major types
Il indique une étiquette (tag), qui sert à préciser la sémantique de l'élément qui suit. Un exemple
typique est pour indiquer qu'une chaîne de caractères est un fait une donnée structurée, par
exemple une date ou un numéro de téléphone. Un décodeur n'a pas besoin de comprendre les
étiquettes, il peut parfaitement les ignorer. Les valeurs possibles pour les étiquettes sont stockées
dans un [registre IANA](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml).

```
+--------------+------------------+---------------------------------+
|     Tag      |    Data Item     |            Semantics            |
+--------------+------------------+---------------------------------+
| 0            | UTF-8 string     | Standard date/time string; see  |
|              |                  | Section 2.4.1                   |
|              |                  |                                 |
| 1            | multiple         | Epoch-based date/time; see      |
|              |                  | Section 2.4.1                   |
|              |                  |                                 |
| 2            | byte string      | Positive bignum; see Section    |
|              |                  | 2.4.2                           |
|              |                  |                                 |
| 3            | byte string      | Negative bignum; see Section    |
|              |                  | 2.4.2                           |
|              |                  |                                 |
| 4            | array            | Decimal fraction; see Section   |
|              |                  | 2.4.3                           |
|              |                  |                                 |
| 5            | array            | Bigfloat; see Section 2.4.3     |
|              |                  |                                 |
| 6..20        | (Unassigned)     | (Unassigned)                    |
|              |                  |                                 |
| 21           | multiple         | Expected conversion to          |
|              |                  | base64url encoding; see         |
|              |                  | Section 2.4.4.2                 |
|              |                  |                                 |
| 22           | multiple         | Expected conversion to base64   |
|              |                  | encoding; see Section 2.4.4.2   |
|              |                  |                                 |
| 23           | multiple         | Expected conversion to base16   |
|              |                  | encoding; see Section 2.4.4.2   |
|              |                  |                                 |
| 24           | byte string      | Encoded CBOR data item; see     |
|              |                  | Section 2.4.4.1                 |
|              |                  |                                 |
| 25..31       | (Unassigned)     | (Unassigned)                    |
|              |                  |                                 |
| 32           | UTF-8 string     | URI; see Section 2.4.4.3        |
|              |                  |                                 |
| 33           | UTF-8 string     | base64url; see Section 2.4.4.3  |
|              |                  |                                 |
| 34           | UTF-8 string     | base64; see Section 2.4.4.3     |
|              |                  |                                 |
| 35           | UTF-8 string     | Regular expression; see         |
|              |                  | Section 2.4.4.3                 |
|              |                  |                                 |
| 36           | UTF-8 string     | MIME message; see Section       |
|              |                  | 2.4.4.                          |
|              |                  |                                 |
| 37..55798    | (Unassigned)     | (Unassigned)                    |
|              |                  |                                 |
| 55799        | multiple         | Self-describe CBOR; see         |
|              |                  | Section 2.4.5                   |
|              |                  |                                 |
|55800+        | (Unassigned)     | (Unassigned)                    |
+--------------+------------------+---------------------------------+
 

                 Values for Tags
```

```
+---------------------+-------------------------------------------------------+
|     5 Bit Value     |              Semantics                                |
+---------------------+-------------------------------------------------------+
|       0..23         |      Simple value (value 0..23)                       |
|         24          |      Simple value (value 32..255 in following byte)   |
|         25          |      IEEE 754 Half-Precision Float (16 bits follow)   |
|         26          |      IEEE 754 Single-Precision Float (32 bits follow) |
|         27          |      IEEE 754 Double-Precision Float (64 bits follow) |
|       28-30         |                 (Unassigned)                          |
|         31          |      "break" stop code for indefinite-length items    |
+---------------------+-------------------------------------------------------+

Table 1: Valeurs de Additional Information dans Major Type 7
```
<u> Exemple </u> : 
'''
false -> F4 : 0b111_10100
'''


```
+----------+------------------+
|  Value   |     Semantics    |
+----------+------------------+
|  0..19   |   (Unassigned)   |
|    20    |      False       |
|    21    |       True       |
|    22    |      NULL        |
|    23    |  Undefined value |
|  24..31  |   (Reserved)     |
| 32..255  |   (Unassigned)   |
+----------+------------------+

Table 2: Simple  Values
```

## Major type 6 : Floating-point numbers and simple data types that need no content
Chaque valeur des informations
supplémentaires de 5 bits dans
l'octet initial a sa propre
signification distincte, comme
défini dans le tableau :

Exemple :
``` 
false → F4 : 0b111_10100 
```
---

# Indefinite Lengths for Some Major Types
L’information supplémentaire de valeur 31 est utilisé pour les 4 CBOR Major Types (`array`, `map`, `text string`, `string byte`) 
si le codage de l’élément doit commencer avant que le le nombre d’éléments dans une liste ou une map, ou la longueur de la chaîne
soit connue ( referred to as ‘streaming’ within Indefinte-length a data item) 

## Indefinite-length map and array
La fin du tableau ou de la map est indiquée en codant un code d'arrêt "break" à un endroit où l'élément de données suivant aurait normalement été inclus. 
Le "break" est codé avec le type Majeur 7 et la valeur d'information supplémentaire 31
(`0b111_11111`) mais n'est pas lui-même une donnée: il ne s'agit que d'une fonction syntaxique pour
fermer le tableau ou la carte.

## Indefinte-length string byte and text string: 
Les chaînes de longueur indéfinie sont ouvertes avec le type principal et la valeur d'informations supplémentaires de 31, mais ce qui
suit est une série d'octets ou de chaînes de texte qui ont des longueurs définies (les morceaux :
chunks). 
La fin de la série de morceaux est indiquée en codant le code d'arrêt "break"
(`0b111_11111`) à un endroit où le morceau suivant de la série se produirait. Le contenu des
morceaux est concaténé et la longueur totale de la chaîne de longueur indéfinie sera la somme des
longueurs de tous les morceaux.

Par exemple, considérons la sequence:
```
0b010_11111 0b010_00100 0xaabbccdd 0b010_00011 0xeeff99 0b111_11111
```

- `0b010_11111 --> 0x5F` : Début d'une byte string de longueur indéfinie

- `0b010_00100 --> 0x44` : Byte string de longueur 4

- `0xaabbccdd` Bytes content

- `0b010_00011 --> 43` : Byte string de longueur 3

- `0xeeff99` : Bytes content

- `0b111_11111 --> 0xFF` : "break"

Après décodage, cela donne une byte string de 7 octets de long: `0xaabbccddeeff99`

Les chaînes de texte de longueurs indéfinies agissent de la même manière que les chaînes
d'octets de longueurs indéfinies, sauf que tous leurs morceaux DOIVENT être des chaînes de
texte de longueur définie, cela implique que les octets d'un seul caractère UTF-8 ne peuvent
pas être répartis entre les blocs: un nouveau bloc ne peut être démarré qu'à une limite de
caractère.
