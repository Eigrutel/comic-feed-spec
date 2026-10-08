# Comic Feed 1.0

Spécification technique du protocole et de sa sortie RSS

Version du protocole : **1.0**. Édition : **5 octobre 2026**. Langue normative de cette édition : français.

Ce document définit les données nécessaires pour publier et consommer un catalogue Comic Feed sans utiliser les applications Eigrutel. Il applique le cahier des charges de référence du 24 septembre 2026 et les précisions P1 à P7 validées le 5 octobre 2026. Il constitue le livrable technique de l’étape 1 ; il ne certifie pas encore les applications ni le parcours de conformité final multi-Publishers.

Le contenu est autonome : les règles utiles à l’implémentation figurent ici. Les exemples et schémas joints sont des aides, jamais une dépendance à un serveur. Aucune autorisation d’Eigrutel n’est requise pour implémenter le protocole. Cette spécification ne confère aucun droit de réutilisation sur les œuvres référencées par les Feed.

## 1 Portée et conformité

**DOIT**, **NE DOIT PAS**, **OBLIGATOIRE** désignent une exigence. **DEVRAIT** désigne une recommandation dont une exception doit être justifiable. **PEUT** et **FACULTATIF** désignent une possibilité. Les tableaux de champs des sections 3 à 8 sont normatifs, même sans majuscules.

Un producteur émet les fichiers Feed. Un consommateur les interprète ; il peut être un Reader, un Collector, un outil d’import ou un validateur. Le protocole décrit les contenus et leurs relations, sans imposer l’interface du consommateur. Les réglages de Reader, projets privés d’Admin et sauvegardes personnelles de Collector ne sont pas des Feed.

Les sections 1 à 14 sont normatives. Les annexes sont informatives. En cas d’écart entre un schéma, un exemple et ces sections, les sections normatives prévalent et l’écart doit être corrigé. Les codes de diagnostic de la section 13 sont des identifiants documentaires stables de cette édition, pas des champs à ajouter aux Feed.

On distingue : la conformité des données, l’accessibilité de leur hébergement et la capacité d’un consommateur à lire un type. Un JSON conforme peut être inaccessible depuis un navigateur distant faute de CORS ; un lecteur peut ignorer un type futur sans rejeter les autres Canaux. Le validateur ne certifie ni identité réelle, ni légalité, ni moralité, ni droits sur les œuvres.

## 2 Modèle de données et identité

Un **Publisher** est la racine technique d’un catalogue. Une **Série** rassemble les métadonnées communes à une œuvre. Un **Canal** constitue une forme de diffusion de cette Série. Une **Publication** constitue une unité de lecture dans ce Canal. La hiérarchie est Publisher → Série → Canal → Publication.

Le Feed Publisher est un index léger. Chaque Série possède un Feed distinct contenant ses Canaux et Publications. Une Série PEUT comporter plusieurs Canaux de même type. Une Publication appartient à un seul Canal ; les références aux mêmes objets dans un index ou dans des versions successives ne sont pas de nouvelles entités.

Les IDs identifient, les noms décrivent et les URLs localisent. Un ID DOIT rester permanent lors d’un renommage, d’une correction, d’une sauvegarde, d’une restauration de sauvegarde ou d’un déplacement des fichiers. Une duplication créative DOIT recevoir de nouveaux IDs. Le type d’un Canal DOIT rester permanent. Déplacer une Publication déjà disponible vers un autre Canal impose de retirer l’ancienne et de créer une Publication d’un nouvel ID dans le Canal de destination.

Une définition d’objet ne peut apparaître deux fois avec le même ID dans un même état de catalogue. Les index et références parent sont des références, pas des définitions concurrentes. Un itm_ ne peut être défini dans deux Canaux ou deux Séries. Les variantes d’exemples du dossier scenarios représentent des états alternatifs, jamais un catalogue à fusionner.

Le Feed Série est la source de vérité éditoriale pour la Série. L’index Publisher transporte son ID, son adresse et sa date de modification, ainsi que des métadonnées de repérage. Une différence de nom n’autorise pas une fusion ou une substitution d’ID.

Suivre un Publisher ou une Série n’autorise pas l’abonnement automatique aux nouveaux Canaux. Les choix de suivi et de lecture appartiennent au lecteur et ne sont pas des champs du Feed. Le consommateur peut mémoriser localement ces choix et ses informations de lecture sans compte central.

## 3 Représentation commune

### 3.1 Sérialisation

Un Feed DOIT être un objet JSON conforme à RFC 8259, encodé en UTF-8 sans BOM. Les commentaires, virgules finales, NaN et Infinity ne sont pas du JSON autorisé. Les noms de membres dupliqués sont refusés à tous les niveaux, avant toute règle choisissant arbitrairement une des valeurs. Les chaînes DOIVENT représenter des caractères Unicode valides, sans surrogate isolé.

Dans un Feed Publisher, series est un tableau. Dans un Feed Série, series est un objet et channels est un tableau. Aucun champ feed_type n’est nécessaire. Un document ne DOIT PAS combiner les deux structures.

O signifie obligatoire. F signifie facultatif. C signifie obligatoire sous la condition indiquée. Un champ F, s’il est présent, doit respecter son type et ses contraintes.

Les chemins utilisent la notation pointée ; [] désigne chaque élément d’un tableau. Les noms de champs et valeurs fermées sont sensibles à la casse. PUBLIC, RESTRICTED et MIXED sont les libellés de documentation ; les valeurs JSON sont public, restricted et mixed.

| Type utilisé | Définition normative |
| --- | --- |
| Objet | Objet JSON ; ni tableau ni null. |
| Tableau de X | Tableau JSON composé uniquement d’éléments du type indiqué. |
| Texte | Chaîne Unicode rendue comme texte, jamais comme HTML actif. Une chaîne obligatoire identifiant un nom ou un titre doit contenir au moins un caractère non blanc. |
| Date | Date RFC 3339 de forme AAAA-MM-JJTHH:mm:ss[.fraction]Z ou avec décalage ±HH:mm. T et Z majuscules ; secondes 00 à 59 ; date civile valide ; fuseau explicite ; -00:00 exclu car décalage inconnu. Les comparaisons portent sur l’instant, pas sur la chaîne. |
| Langue | Étiquette BCP 47, par exemple fr ou en-GB. Absence : langue non déclarée, sans déduction obligatoire. |
| ID Publisher | pub_ suivi d’un UUID v4 canonique en minuscules. |
| ID Série | ser_ suivi d’un UUID v4 canonique en minuscules. |
| ID Canal | chn_ suivi d’un UUID v4 canonique en minuscules. |
| ID Publication | itm_ suivi d’un UUID v4 canonique en minuscules. |
| Référence URL | Chaîne non vide contenant une URL absolue ou une référence relative Web, résolue par rapport au document Feed qui la contient. Ce n’est ni un chemin système ni un identifiant. |
| Référence image | Référence URL dont la ressource est effectivement une image JPEG, PNG ou WebP. L’extension seule ne prouve pas le format. |

Les champs connus n’acceptent pas null. Une donnée facultative inconnue est omise. Les tableaux explicitement autorisés à être vides utilisent []. Les chaînes facultatives peuvent être vides sauf contrainte particulière, mais un producteur DEVRAIT omettre une donnée sans valeur utile. Les clés dupliquées dans un même objet sont refusées ; aucune réparation silencieuse n’est autorisée.

Un ID ne dépend jamais du titre, du nom de fichier, de l’URL, de l’ordre du catalogue ou de l’heure de publication. Il reste opaque pour le consommateur. Les préfixes sont vérifiés selon le type d’objet. Les ID ne prouvent pas l’identité réelle d’un Publisher.

### 3.2 Identifiants et dates

Après le préfixe pub_, ser_, chn_ ou itm_, l’UUID DOIT suivre ce motif, ancré sur toute la chaîne : `[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}`. Les producteurs utilisent un générateur aléatoire UUID v4 approprié, sans registre central. L’égalité des IDs est une égalité exacte de chaînes ; le consommateur ne normalise pas silencieusement un ID non conforme.

Le profil des dates est strictement celui de la table : année 0001 à 9999, calendrier grégorien valide, heure 00 à 23, minutes et secondes 00 à 59, fractions décimales facultatives, décalage horaire numérique de 00:00 à 23:59 ou Z. Les secondes intercalaires et le décalage inconnu -00:00 ne sont pas admis dans ce profil. Toutes les comparaisons DOIVENT convertir en instants UTC, y compris lorsque les fractions ou décalages diffèrent. L’affichage local est libre.

Les codes de langue respectent BCP 47. Ils ne pilotent pas l’accès. L’absence d’une langue ne rend pas le Feed invalide ; une éventuelle préférence d’affichage ne modifie pas les données.

### 3.3 Ordre

L’ordre des membres d’un objet JSON n’a aucune signification. L’ordre des ressources d’une Publication webtoon est normatif. L’ordre des autres tableaux ne définit ni identité, ni nouveauté, ni accès. Un Reader choisit sa présentation ; pour une chronologie, il utilise publish_at et non l’ordre des fichiers ou updated_at. Il PEUT utiliser l’ID comme départage stable d’horodatages égaux.

## 4 Feed Publisher

### 4.1 Enveloppe

| Champ | Type | Présence | Règle |
| --- | --- | --- | --- |
| protocol | Texte | O | Valeur exacte comic-feed. |
| version | Texte | O | Valeur exacte 1.0 pour un producteur V1.0 ; jamais un nombre JSON. |
| publisher | Objet Publisher | O | Identité du propriétaire technique du catalogue. |
| updated_at | Date | O | Dernière modification sémantique de ce Feed ; ce n’est pas l’heure de téléchargement. |
| series | Tableau d’entrées de Série | O | Index léger ; [] autorisé. Aucune liste de Publications à ce niveau. |
| generated_by | Objet logiciel | F | Diagnostic uniquement. |
| extensions | Objet d’extensions | F | Voir section 12. |

### 4.2 Objet Publisher

| Champ relatif à publisher | Type | Présence | Règle |
| --- | --- | --- | --- |
| id | ID Publisher | O | Permanent. |
| name | Texte | O | Nom public libre et modifiable. |
| type | Texte | F | Libre, purement informatif ; ne pilote aucun comportement. |
| description | Texte | F | Présentation du Publisher. |
| language | Langue | F | Langue principale des informations Publisher. |
| url | Référence URL | F | Page publique du Publisher ; ne remplace pas une adresse de Feed. |
| images | Objet | F | Contient les références d’images ci-dessous. |
| images.avatar | Référence image | F | Avatar. |
| images.banner | Référence image | F | Bandeau ; aucune dimension ni mise en page imposée au Reader. |
| status | Texte fermé | F | active, inactive ou moved ; active par défaut. |
| moved_to | Référence URL | C | Obligatoire et autorisé seulement pour status = moved ; cible un Feed Publisher. |
| extensions | Objet d’extensions | F | Voir section 12. |

Un ancien Feed moved conserve protocol, version, publisher.id, publisher.name, updated_at et series, avec un tableau series éventuellement vide. Il est interprété comme un avis de déplacement ; un tableau vide dans cet avis ne signifie pas le retrait de l’ancien catalogue.

### 4.3 Entrée de Série dans series

| Champ relatif à series[] | Type | Présence | Règle |
| --- | --- | --- | --- |
| id | ID Série | O | Identique à series.id du Feed Série ciblé. |
| title | Texte | O | Titre de repérage dans l’index ; le Feed Série reste la source de vérité éditoriale. |
| feed | Référence URL | O | Adresse du Feed Série, jamais sa page de lecture. |
| updated_at | Date | O | Copie exacte du updated_at racine de la version du Feed Série indexée. |
| thumbnail | Référence image | F | Miniature dupliquée volontairement pour l’index. |
| status | Texte fermé | F | active ou withdrawn ; active par défaut. Copie de l’état de la Série. |
| extensions | Objet d’extensions | F | Voir section 12. |

Ces champs obligatoires sont conservés pour une entrée withdrawn. Chaque id apparaît une seule fois dans l’index. Une indisponibilité du Feed ciblé n’autorise jamais à transformer une Série en withdrawn.

Le statut inactive n’est ni un retrait, ni une instruction de désabonnement : le catalogue existant reste interprétable et lisible selon ses accès. Un consommateur NE DOIT PAS supprimer les favoris ou positions à cause de cette seule valeur.

## 5 Feed Série

### 5.1 Enveloppe

| Champ | Type | Présence | Règle |
| --- | --- | --- | --- |
| protocol | Texte | O | Valeur exacte comic-feed. |
| version | Texte | O | Chaîne 1.0 pour un producteur V1.0. |
| series | Objet Série | O | Objet, et non tableau : un Feed Série décrit une seule Série. |
| publisher | Objet référence parent | O | Contient id et feed obligatoires. |
| publisher.id | ID Publisher | O | Doit correspondre au publisher.id du Feed parent. |
| publisher.feed | Référence URL | O | Adresse du Feed Publisher parent. |
| updated_at | Date | O | Dernière modification sémantique de l’ensemble du Feed Série. |
| channels | Tableau de Canaux | O | [] autorisé. Un même type peut apparaître dans plusieurs Canaux d’IDs distincts. |
| generated_by | Objet logiciel | F | Même objet de diagnostic que dans le Feed Publisher. |
| extensions | Objet d’extensions | F | Voir section 12. |

Les informations du Publisher ne sont pas recopiées dans cette référence parent. Il n’est pas nécessaire de répéter publisher.id et series.id dans les Canaux et Publications imbriqués : leur appartenance provient de la structure du document.

### 5.2 Objet Série

| Champ relatif à series | Type | Présence | Règle |
| --- | --- | --- | --- |
| id | ID Série | O | Permanent. |
| title | Texte | O | Titre public libre et modifiable. |
| description | Texte | F | Présentation de l’œuvre. |
| language | Langue | F | Langue principale déclarée pour la Série. |
| images | Objet | F | Contient les références ci-dessous. |
| images.cover | Référence image | F | Couverture. |
| images.banner | Référence image | F | Bandeau. |
| credits | Tableau de crédits | F | [] autorisé ; les créateurs sont distincts du Publisher technique. |
| content_rating | Texte | F | Classification libre de la Série. |
| content_warning | Texte | F | Avertissement éditorial libre de la Série. |
| status | Texte fermé | F | active ou withdrawn ; active par défaut. |
| extensions | Objet d’extensions | F | Voir section 12. |

Il n’existe pas de series.updated_at imbriqué : le updated_at racine du Feed Série remplit cette fonction. Une Série withdrawn cesse de proposer ses Publications à la lecture, même si leurs anciennes descriptions sont conservées dans le document.

### 5.3 Crédit

| Champ relatif à credits[] | Type | Présence | Règle |
| --- | --- | --- | --- |
| name | Texte | O | Nom affiché du créateur. |
| role | Texte | F | Rôle libre : aucune liste fermée ni compte requis. |
| id | Texte non vide | F | Identifiant opaque facultatif dans le contexte du Publisher ; ni préfixe imposé ni identité mondiale déduite. |
| url | Référence URL | F | Page associée à ce crédit. |

## 6 Canal

| Champ relatif à channels[] | Type | Présence | Règle |
| --- | --- | --- | --- |
| id | ID Canal | O | Permanent. Un Canal appartient à une seule Série. |
| type | Texte fermé | O | strip ou webtoon en V1 ; permanent pour cet ID. |
| title | Texte | O | Nom public libre du Canal ; ne détermine pas son type. |
| language | Langue | F | Langue du Canal, recommandée par le cahier. |
| updated_at | Date | O | Change lorsque le Canal ou une de ses Publications change. |
| access | Objet accès | O | Contient mode obligatoire. |
| access.mode | Texte fermé | O | public, restricted ou mixed. Voir section 8. |
| publications | Tableau de Publications | O | [] autorisé. |
| status | Texte fermé | F | active ou withdrawn ; active par défaut. |
| url | Référence URL | C | Facultative en général ; obligatoire si rss est présent. Page publique de lecture du Canal. |
| rss | Référence URL | F | Adresse du RSS de ce Canal ; autorisée seulement si access.mode = public. |
| extensions | Objet d’extensions | F | Voir section 12. |

Un Canal withdrawn conserve ses champs obligatoires, y compris type et access, mais ses Publications ne sont plus proposées à la lecture. Il peut avoir publications: [].

Le Canal est l’unité de suivi des Publications. Un type inconnu est traité selon la section 12, sans interpréter son nom comme du code, un module ou une URL de moteur.

## 7 Publication et ressources

### 7.1 Champs de Publication

| Champ relatif à publications[] | Type | Présence | Règle |
| --- | --- | --- | --- |
| id | ID Publication | O | Permanent ; une seule appartenance à un Canal. |
| status | Texte fermé | O | scheduled, published ou withdrawn. draft interdit dans les Feed diffusés. |
| publish_at | Date | C | Obligatoire pour scheduled et published ; facultatif pour withdrawn. Date normative de disponibilité. |
| updated_at | Date | O | Dernière modification ; ne crée pas une nouveauté. |
| title | Texte | F | Titre éditorial ; son affichage reste libre. |
| thumbnail | Référence image | F | Miniature ; ne remplace jamais une ressource de lecture manquante. |
| resources | Tableau de ressources | C | Obligatoire pour un contenu non retiré d’accès effectif public ; facultatif si restricted ou withdrawn. Voir 7.2. |
| access | Objet accès | C | Facultatif avec héritage d’un Canal public/restricted ; obligatoire pour un contenu non retiré sous Canal mixed. |
| access.mode | Texte fermé | C | Obligatoire si access existe ; public ou restricted exclusivement. |
| update_notice | Objet avis de correction | F | Signale une correction avec le même ID. |
| update_notice.at | Date | C | Obligatoire si update_notice existe ; instant du signalement, au plus tard updated_at. |
| update_notice.message | Texte non vide | C | Obligatoire si update_notice existe ; explication libre et courte. |
| content_rating | Texte | F | Classification libre de cette Publication. |
| content_warning | Texte | F | Avertissement éditorial libre de cette Publication. |
| url | Référence URL | C | Facultative en général ; obligatoire pour une Publication incluse dans la sortie RSS. Page donnant accès à cette Publication. |
| extensions | Objet d’extensions | F | Voir section 12. |

Une Publication withdrawn peut se limiter à id, status et updated_at. Les autres champs, s’ils sont conservés, respectent leurs types, mais les ressources ne sont pas utilisées pour proposer sa lecture.

La date de disponibilité reste obligatoire dans les données même si un Reader choisit de ne pas l’afficher. Après première disponibilité, une correction conserve publish_at et id, et modifie updated_at. Il n’existe pas d’état corrected : une correction est une modification de la même Publication.

### 7.2 Ressource de lecture

| Champ relatif à resources[] | Type | Présence | Règle |
| --- | --- | --- | --- |
| type | Texte fermé | O | image en V1. |
| src | Référence image | O | Référence externe au JSON ; jamais des octets encodés dans une chaîne. |

Pour une Publication non retirée dont resources est fourni, strip exige exactement une ressource ; webtoon exige au moins une ressource. L’ordre du tableau est l’ordre de lecture des segments webtoon. Aucun découpage automatique n’est décrit par le Feed.

Une Publication restricted peut omettre resources : le Feed ne révèle alors pas l’adresse des œuvres protégées. Pour éviter deux représentations du même cas, resources: [] est réservé aux retraits ; pour une annonce restreinte sans médias exposés, le champ est omis. Si des ressources restreintes sont annoncées, elles respectent les mêmes formats et cardinalités et la protection réelle reste à la charge de l’hébergement.

JPG et JPEG désignent le même format. Les médias reconnus sont JPEG, PNG et WebP. GIF n’est pas pris en charge en V1 ; SVG, HTML, JavaScript, iframe et autres contenus actifs ne sont pas des ressources de lecture autorisées. Ces contraintes d’images valent aussi pour les miniatures et visuels déclarés par le Feed. Aucun champ de poids ou de dimensions n’est imposé par cette version.

### 7.3 Formats et chargement

Le type image désigne des octets d’image réellement décodables comme JPEG, PNG ou WebP. Le validateur NE DOIT PAS se contenter d’une extension de fichier ou d’un Content-Type pour accepter une ressource. Les paramètres de décodage et limites locales de mémoire restent du ressort de l’application ; aucune limite universelle de pixels ou d’octets n’est fixée.

Une ressource manquante, interdite ou corrompue NE DOIT PAS être remplacée par une miniature présentée comme l’œuvre complète. Un lien facultatif vers une page HTML n’est pas une ressource de lecture image : cette page peut être ouverte séparément, mais le Feed ne la fait pas exécuter dans le moteur de lecture.

## 8 Accès et classification

### 8.1 Accès effectif

| Valeur du Canal | Valeur de la Publication | Résultat |
| --- | --- | --- |
| public | access absent | public |
| restricted | access absent | restricted |
| public ou restricted | public explicite | public |
| public ou restricted | restricted explicite | restricted |
| mixed | public explicite | public |
| mixed | restricted explicite | restricted |
| mixed | access absent sur une Publication non retirée | Publication invalide ; jamais publique par défaut. |
| Toute valeur | mixed dans la Publication | Publication invalide. |

Un avis de retrait minimal n’a pas besoin d’annoncer un accès. Un mode inconnu sur un contenu actif ne devient ni public ni une règle implicite : l’objet concerné est isolé.

PUBLIC signifie sans autorisation Comic Feed. Il ne vaut ni licence de réutilisation ni mise dans le domaine public. RESTRICTED décrit un besoin d’autorisation, sans définir une API d’authentification, un prestataire ou un paiement. Aucun code, mot de passe ou jeton n’est ajouté aux champs standards proposés.

Le champ access.mode du Canal représente sa valeur par défaut, pas une garantie sur tous ses descendants. Une Série ou un Canal dont les contenus mêlent les deux accès peut être présenté comme mixte par le consommateur, indépendamment du choix de valeur par défaut. Une Série ne possède pas de champ standard access concurrent.

Le consommateur calcule l’accès effectif avant de sélectionner une ressource, un export ou une Publication pour le RSS. Il n’émet pas une requête protégée pour découvrir si un mode inconnu voulait dire public. Une URL connue ne constitue pas une autorisation.

### 8.2 Classification

content_rating et content_warning sont des textes libres admis sur la Série et la Publication. Les déclarations de Série décrivent le contexte de l’œuvre ; celles d’une Publication apportent une information propre. Elles restent attachées à leur niveau et une valeur de Publication n’efface pas automatiquement celle de la Série. Aucun vocabulaire mondial, calcul d’âge, filtre ou correspondance avec PUBLIC/RESTRICTED n’est imposé.

### 8.3 Protection réelle

Un Feed public PEUT annoncer des métadonnées de contenu restreint sans ressources. Les fichiers protégés peuvent nécessiter une couche serveur choisie par le Publisher. La V1 ne définit ni paiement, ni API d’autorisation, ni transfert de secrets. Un mot de passe, jeton ou code d’accès ne DOIT PAS être placé dans un champ standard du Feed. Une éventuelle extension ne doit pas exposer un secret dans un document public.

## 9 Cycle de vie et dates

### 9.1 Disponibilité

Pour une Publication connue, le consommateur applique dans cet ordre :

1. Vérifier que la structure, les IDs, le type et les valeurs nécessaires sont compris.
2. Écarter un Publisher moved jusqu’à traitement de sa migration. inactive n’interdit pas la lecture.
3. Écarter une Série, un Canal ou une Publication withdrawn, même si des médias restent référencés.
4. Pour scheduled ou published, attendre que l’instant courant soit supérieur ou égal à publish_at.
5. Appliquer l’accès effectif. Une Publication RESTRICTED arrivée à échéance reste soumise à son autorisation.

Un contenu scheduled arrivé à échéance est temporellement disponible sans réécriture du Feed. published avec une date future n’est pas disponible avant cette date. Un producteur DEVRAIT écrire scheduled avant l’échéance ; la règle temporelle reste identique pour les deux valeurs.

Le temps est évalué localement par le consommateur. Le protocole ne fournit pas de service d’horloge. Une horloge incorrecte peut donc modifier cette évaluation. La programmation statique n’est pas un mécanisme de confidentialité : métadonnées et médias déjà déposés peuvent être accessibles directement.

### 9.2 Changements éditoriaux

| Situation | Règle |
| --- | --- |
| Brouillon | Privé au projet de l’auteur ; jamais dans un Feed diffusé. |
| Programmé, jamais disponible | Modifiable et reprogrammable avec le même ID ; tout changement modifie updated_at. |
| Programmé annoncé puis annulé | S’il a été diffusé, un avis withdrawn permet aux consommateurs qui le connaissent d’éviter une activation future. Une simple absence ne constitue pas cet avis. |
| Première disponibilité | Pas de nouvel ID ; le seul passage du temps ne change pas updated_at. |
| Correction après disponibilité | Même ID et même publish_at ; updated_at augmente. |
| Correction signalée | Même règle, avec update_notice.at et message. |
| Retrait | status = withdrawn et updated_at augmente ; les ressources peuvent disparaître. |
| Renommage ou changement d’adresse média | Même ID ; updated_at augmente pour le changement sémantique. |

Un retrait valide reçu prime sur la présence d’anciens médias. La V1 n’ajoute pas de procédure de restauration éditoriale d’un retrait : une réactivation contradictoire ne rétablit pas silencieusement la lecture et doit être signalée. Restaurer une sauvegarde privée ne justifie pas la réémission d’un ancien catalogue en tant que mise à jour récente.

### 9.3 Propagation de updated_at

Une modification sémantique d’un objet DOIT produire une valeur updated_at strictement plus récente que la précédente. Une mise en forme JSON différente ou un téléchargement ne suffit pas à créer une modification sémantique. Le producteur utilise une précision suffisante lorsque plusieurs modifications surviennent dans une seconde.

La propagation d’une correction de Publication est : Publication → Canal → updated_at racine du Feed Série → series[].updated_at dans le Feed Publisher → updated_at racine du Feed Publisher. Un changement de métadonnées de Série commence au Feed Série. Les dates parent DOIVENT être au moins aussi récentes que celles de leurs descendants. publish_at est exclu de ce calcul : updated_at peut lui être antérieur.

L’index DOIT recopier exactement la valeur updated_at du Feed Série indexé. Le consommateur peut alors ne recharger que les Séries dont cette valeur a changé. Un changement de l’adresse feed déclenche également une résolution de la nouvelle adresse. Des snapshots d’horodatage plus ancien ou contradictoires ne doivent pas écraser sans diagnostic les données plus récentes connues.

Lorsqu’un média change sous la même URL, le producteur DOIT rendre sa nouvelle version récupérable par les mécanismes HTTP ordinaires. Il DEVRAIT changer l’URL du média si une revalidation fiable des caches n’est pas assurée ; cette opération ne change jamais l’ID de Publication. Les clients ne déduisent pas d’un seul updated_at qu’un cache d’image s’est nécessairement vidé.

### 9.4 Nouveautés et corrections

Une nouvelle œuvre est détectée par un nouvel ID de Publication dans une appartenance vérifiée. Une Publication déjà connue mais future entre dans les contenus disponibles à son échéance. Une correction, même signalée, ne devient pas une nouvelle œuvre et ne réinitialise pas automatiquement l’état de lecture personnel.

update_notice.at désigne l’avis et DOIT être inférieur ou égal à updated_at. Son message est du texte. Le consommateur PEUT mémoriser id + update_notice.at pour ne montrer un avis qu’une fois. Une nouvelle correction signalée utilise une nouvelle date d’avis ; une correction silencieuse peut omettre l’objet. La V1 ne fournit pas un historique de toutes les corrections.

### 9.5 Conservation des retraits

Le producteur DEVRAIT conserver durablement les avis de retrait minimaux pour les Publications déjà annoncées. Le cahier autorise leur présence temporaire : aucun délai universel n’est imposé. S’ils sont supprimés, un consommateur resté longtemps hors ligne peut ne jamais recevoir l’avis. L’absence seule ne permet toujours pas de conclure au retrait.

Un consommateur garde localement les informations nécessaires à ses favoris, positions et décisions. Une impossibilité de lecture n’est pas une instruction d’effacer la bibliothèque. Le protocole n’impose pas de stockage durable des œuvres.

## 10 Relations et déplacements

### 10.1 Références et base

Chaque référence relative est résolue contre l’adresse du document Feed qui la contient, après les redirections HTTP. Elle n’est jamais résolue contre le nom de Série, le dossier supposé du Canal, publisher.url ou l’adresse du Collector. Les ../ sont autorisés et nécessaires au lien parent.

Les références suivent la syntaxe URI de RFC 3986 : les espaces, contrôles, antislashs et caractères nécessitant un encodage ne sont pas des raccourcis de chemins de fichiers. Ils doivent être représentés correctement, notamment par encodage pour cent. L’URL résultante utilise HTTP(S), possède un hôte et ne contient pas de nom d’utilisateur ni de mot de passe. Une adresse de Feed ou moved_to désigne le document JSON entier, sans fragment. Une page de lecture PEUT avoir un fragment.

Sur Internet, les règles HTTPS de la section 11 s’appliquent. Une importation de fichiers locaux doit recevoir explicitement sa base de résolution dans le contexte de l’import. Cette base n’est pas un nouveau champ de Feed. Faute de base, les références relatives restent non résolues et le consommateur le signale ; il n’invente pas d’adresse. Les chemins de fichiers locaux ne sont pas autorisés comme valeurs d’URL dans les Feed.

Exemple : dans https://aube.example/bd/series/les-lucioles/feed.json, ../../feed.json désigne https://aube.example/bd/feed.json et channels/strips/media/001.png désigne https://aube.example/bd/series/les-lucioles/channels/strips/media/001.png.

### 10.2 Concordance

| Frontière | Vérification obligatoire |
| --- | --- |
| Index Publisher → Feed Série | publisher.id parent = publisher.id enfant, et series[].id index = series.id enfant. |
| Feed Série → Feed Publisher | publisher.id référence = publisher.id parent ; l’index actif doit référencer la même series.id. |
| Source moved → destination | Même publisher.id, protocol compatible et cible de type Feed Publisher. |
| Série → Canal → Publication imbriqués | Appartenance structurelle ; aucune répétition des IDs parent exigée. |

Une adresse de retour peut employer une autre écriture relative ou suivre une redirection ; l’égalité textuelle de ces URLs n’est pas l’identité. Une relation active cohérente doit finalement retrouver les mêmes objets. Si le parent est momentanément inaccessible, la relation reste non vérifiée ; le client ne fabrique pas un parent et peut conserver ses informations antérieures.

Une discordance d’ID provoque le refus ou l’isolation de la relation, sans remplacement de l’entité connue. Un écart de titre ou de date peut provenir d’un déploiement non atomique ou d’un cache : il est signalé et une nouvelle actualisation est possible. Il ne devient ni une migration ni un retrait implicite.

L’index peut porter un avis withdrawn valide pour une Série déjà identifiée même si le Feed Série n’est plus disponible. L’index et le Feed Série DOIVENT déclarer des états cohérents ; une contradiction ne réactive pas automatiquement un retrait reçu.

### 10.3 Migration du Publisher

1. Recevoir publisher.status = moved et publisher.moved_to depuis la source du Publisher déjà suivie.
2. Résoudre et contrôler cette URL comme toute URL de Feed.
3. Charger la cible sans transmettre d’autorisation d’une autre origine ; vérifier protocol, version, forme Publisher et le même publisher.id.
4. Si la cible est elle-même moved, poursuivre en détectant les boucles. Les limites locales de redirections sont explicites et ne constituent pas une migration réussie.
5. Après vérification d’une cible finale cohérente, mémoriser la nouvelle adresse ; préserver les IDs et les états personnels qui s’y rattachent.

Une panne, une boucle, une version incompatible ou un ID différent interrompt la migration en conservant les données précédentes. Un simple HTTP 301 ne remplace pas les vérifications d’identité. Un ancien avis moved avec series: [] n’annonce pas le retrait de tout le catalogue.

Les IDs ne sont pas des signatures. Deux sources indépendantes revendiquant un même ID ne sont pas fusionnées arbitrairement : la relation, la provenance et le chemin de migration doivent être vérifiés. La V1 ne fournit pas d’authentification cryptographique.

## 11 Transport Web

Un hébergement statique suffit pour les contenus PUBLIC. Les noms des dossiers sont libres et ne sont pas des identifiants. Aucun nom de domaine, serveur, proxy, API ou compte Eigrutel n’est nécessaire.

| Document ou ressource | Exigence de publication |
| --- | --- |
| Feed JSON Internet | HTTPS et Content-Type application/json. |
| Feed public destiné aux Collectors Web externes | CORS permettant sa lecture sans identité du lecteur. |
| Médias et miniatures pour une lecture Web HTTPS | Ressources chargeables en HTTPS ; CORS recommandé. |
| Image JPEG, PNG, WebP | Content-Type cohérent : image/jpeg, image/png, image/webp ; les octets doivent correspondre. |
| RSS Internet | HTTPS ; Content-Type application/rss+xml ; URLs internes absolues. |
| Développement local | HTTP permis sur localhost et adresses de boucle locale ; aucun autre HTTP de Feed Internet conforme. |

Pour un Feed public lu sans identifiants, Access-Control-Allow-Origin: * permet l’agrégation depuis des origines externes. Une réponse réservée à l’origine du site source ne satisfait pas cet objectif général. Les réponses utiles, y compris les réponses revalidées, doivent permettre l’accès du navigateur. CORS ne constitue pas une autorisation de lecture d’un contenu protégé.

Un Reader installé sur le même site peut fonctionner alors que l’agrégation externe échoue. Un diagnostic DOIT distinguer l’erreur CORS, l’erreur HTTP, une URL non HTTPS et une structure JSON invalide. Aucun proxy central obligatoire n’est prévu pour contourner la configuration de l’hébergeur.

Le serveur PEUT utiliser ETag, Last-Modified, compression et cache HTTP. Ces mécanismes ne remplacent ni les IDs ni updated_at. Les producteurs DEVRAIENT déployer un ensemble cohérent et conserver les anciennes ressources le temps nécessaire à leurs mises à jour ; le consommateur doit supporter une incohérence temporaire sans supprimer sa bibliothèque.

## 12 Versions et extensions

### 12.1 Version de protocole

protocol vaut exactement comic-feed. version est une chaîne majeur.mineur, sans zéro initial superflu : 1.0 pour cette édition. generated_by décrit un logiciel et ne détermine jamais la compatibilité.

Un producteur 1.0 DOIT respecter les valeurs de cette édition. Les versions 1.x ajoutent des possibilités compatibles sans rendre obligatoires de nouveaux champs pour les documents existants. Une version majeure inconnue est signalée et son contenu n’est pas interprété comme 1.0. Une version mineure ultérieure est examinée avec les règles connues ; le client ne prétend pas certifier toute une version qu’il ne connaît pas.

| Situation | Comportement du consommateur 1.0 |
| --- | --- |
| Champ facultatif inconnu | Ignorer, éventuellement diagnostiquer ; ne pas l’exécuter. |
| Champ obligatoire connu absent | Objet invalide. |
| Champ connu de mauvais type | Objet invalide, même s’il est facultatif. |
| Type de Canal inconnu | Isoler ce Canal ; garder les métadonnées sûres et les Canaux pris en charge. |
| Statut ou accès inconnu | Isoler l’objet affecté ; ne jamais supposer active, published ou public. |
| Version majeure incompatible | Refuser l’interprétation du Feed en conservant les données locales précédentes. |

Un type futur déclaré dans un document 1.0 ne respecte pas les valeurs de cette édition ; la tolérance du lecteur ne le rend pas conforme. Dans un document 1.x ultérieur, il est non pris en charge par ce lecteur, sans supposer que le producteur a violé cette version future.

### 12.2 Logiciel générateur

| Champ relatif à generated_by | Type | Présence | Règle |
| --- | --- | --- | --- |
| name | Texte non vide | O dans cet objet | Nom du logiciel, quel qu’il soit. |
| version | Texte non vide | F | Version du logiciel, indépendante de la version Comic Feed. |

L’objet generated_by lui-même est facultatif. Son absence n’est jamais une erreur de conformité. Il n’accorde aucune confiance particulière à Eigrutel ou à un autre logiciel.

### 12.3 Extensions

extensions est facultatif sur tout objet standard défini dans ce dictionnaire, même lorsque la ligne n’est pas répétée dans son petit tableau. Il ne s’applique pas récursivement aux structures privées internes d’une extension.

Sa valeur est un objet dont les clés sont des noms d’espace non vides, par exemple org.example.mafonction. La notation en domaine inversé est recommandée pour limiter les collisions ; elle ne déclenche ni résolution DNS ni requête. La valeur de chaque entrée est un objet JSON appartenant à cette extension.

Une extension inconnue est ignorée. Une extension ne peut pas remplacer un champ obligatoire, changer l’accès effectif, rendre exécutable une donnée ni redéfinir le sens d’un champ standard. Un consommateur doit pouvoir interpréter le socle standard sans installer de code indiqué par le Feed.

Les champs facultatifs standards ajoutés dans une future version compatible sont ignorés par les anciens consommateurs. Un champ obligatoire connu absent reste une erreur ; un champ facultatif connu présent avec un type incorrect reste une erreur. Un producteur 1.0 place ses ajouts expérimentaux dans extensions.

## 13 Validation et sécurité

### 13.1 Ordre des contrôles

Le contrôle se fait en couches : JSON et encodage ; enveloppe et version ; types et champs ; IDs, dates et cardinalités ; règles entre objets ; concordance entre documents ; transitions connues ; transport et fichiers réellement servis. Un validateur hors ligne doit annoncer les couches qu’il a effectivement vérifiées.

Les schémas JSON joints expriment la structure et plusieurs contraintes conditionnelles. Ils ne prouvent pas à eux seuls la validité du calendrier, BCP 47, l’absence de clés dupliquées avant décodage, la cohérence interdocuments, l’historique, le contenu réel des images ou CORS. Une option de validation format non activée ne vaut pas contrôle des dates.

### 13.2 Diagnostics

| Code | Cause | Portée habituelle |
| --- | --- | --- |
| CF_JSON | JSON invalide, encodage ou caractères invalides. | Feed. |
| CF_DUPLICATE_KEY | Deux membres de même nom dans un objet. | Feed. |
| CF_REQUIRED | Champ obligatoire absent. | Objet concerné ; Feed si enveloppe. |
| CF_TYPE | Mauvais type ou null non autorisé. | Objet concerné. |
| CF_ENUM | Valeur fermée non conforme à la version déclarée. | Objet concerné. |
| CF_ID | Préfixe ou UUID v4 incorrect. | Objet concerné. |
| CF_DUPLICATE_ID | Définition multiple du même ID dans un état cohérent. | Définitions et relations concernées. |
| CF_DATE | Date syntaxiquement ou civilement invalide. | Objet concerné. |
| CF_TIME_ORDER | Horodatages de modification incohérents. | Objets concernés. |
| CF_MIXED_ACCESS | Publication active sans accès explicite sous Canal mixed. | Publication. |
| CF_RESOURCE_COUNT | Ressources absentes pour PUBLIC ou cardinalité incorrecte. | Publication. |
| CF_RESOURCE_FORMAT | Octets non conformes aux formats d’image permis. | Ressource et lecture affectée. |
| CF_URL | Référence d’URL mal formée, schéma interdit, identifiants intégrés. | Lien ou objet concerné. |
| CF_PARENT_ID | publisher.id discordant entre documents. | Relation. |
| CF_SERIES_ID | series.id discordant entre index et Feed Série. | Relation. |
| CF_INDEX_DATE | Date d’index différente de la version Série chargée. | Ensemble de versions ; actualisation à réessayer. |
| CF_MOVE_ID | Migration vers un autre publisher.id. | Migration. |
| CF_MOVE_LOOP | Boucle de déplacement. | Migration. |
| CF_IMMUTABLE | Changement interdit d’ID, type, appartenance ou publish_at après disponibilité. | Transition. |
| CF_REACTIVATION | Contradiction avec un retrait explicite reçu. | Transition à isoler. |
| CF_RSS_POLICY | rss sur Canal non public, URL requise absente ou élément inéligible. | Sortie RSS. |
| CF_RSS_XML | XML/RSS mal formé ou correspondance invalide. | Sortie RSS. |
| NET_HTTPS | Transport Internet ne satisfaisant pas HTTPS. | Déploiement. |
| NET_CORS | Feed inaccessible à l’origine Web externe. | Déploiement. |
| NET_HTTP | Ressource absente, non autorisée ou erreur réseau. | Chargement ; jamais retrait implicite. |
| UNSUPPORTED | Type ou version non pris en charge. | Capacité du consommateur. |

Un résultat doit fournir le code, le document et le chemin de l’objet concerné lorsque disponibles. Un outil PEUT émettre plusieurs diagnostics pour une même erreur ; un exemple invalide peut donc spécifier un diagnostic principal sans interdire les diagnostics secondaires.

**VALIDE** signifie que les contrôles annoncés ont réussi. **VALIDE AVEC AVERTISSEMENTS** conserve cette conformité dans le périmètre vérifié, avec des éléments non bloquants. **REFUSÉ** signifie qu’un Feed, objet, lien ou changement est rejeté dans la portée précisée. Isoler une Publication défectueuse peut laisser d’autres Canaux lisibles, mais ne rend pas cette Publication conforme. Un contrôle réseau non réalisé est indiqué comme non vérifié, pas comme réussi.

### 13.3 Sécurité et confidentialité

Les Feed sont des données non fiables. Un consommateur NE DOIT PAS exécuter de script, iframe, plugin, modèle de code ou moteur indiqué par un Feed. Il affiche descriptions, titres, crédits, avertissements et messages comme du texte ; aucune interprétation HTML active n’est permise pour ces champs.

javascript:, file:, data:, blob: et autres schémas hors HTTP(S) ne sont pas des références autorisées. Une extension ne crée pas d’exception. Un fichier annoncé comme image ne devient pas sûr par son seul suffixe. Les extensions de noms ou valeurs spéciales ne doivent pas altérer les objets internes d’une application lors de l’import.

Les consommateurs contrôlent les redirections et les origines, cloisonnent les éventuelles autorisations et ne transmettent pas de secrets d’un Publisher à l’autre. Une implémentation serveur doit protéger ses accès réseau internes ; le droit d’utiliser localhost en développement n’autorise pas un Feed Internet à faire sonder arbitrairement un réseau privé.

Les limites contre les abus de taille, de profondeur, de nombre de redirections ou de temps sont propres aux applications et doivent produire un diagnostic explicite. Elles ne sont pas annoncées comme limites universelles du protocole. Aucun bouton d’exécution forcée de contenu interdit n’est prévu.

Un Feed PUBLIC ne requiert aucune identité du lecteur. Le protocole ne transmet pas sa bibliothèque globale ni une télémétrie individuelle. Les abonnements, favoris, positions et préférences restent sous le contrôle local du lecteur. Des services ajoutés dans un site Reader indépendant ne deviennent pas des fonctions de Comic Feed.

## 14 Sortie RSS

### 14.1 Portée

La sortie standard est RSS 2.0, XML 1.0 en UTF-8, sans DTD ni entités externes. Elle est facultative et parallèle au Feed complet. Sa présence n’est pas une condition de validité de Comic Feed. Le générateur doit pouvoir la produire pour chaque Canal déclarant access.mode = public. Aucun RSS de Canal restricted ou mixed n’est défini par ce profil.

channels[].rss localise le document XML ; channels[].url localise sa page de lecture. Toute Publication sélectionnée possède une url de lecture spécifique. Ces références sont résolues depuis le Feed Série, puis écrites en absolu dans le RSS. Ni l’ID ni l’adresse JSON ne sont utilisés à la place d’une page de lecture.

### 14.2 Sélection

À l’instant de génération T, une Publication est éligible si ses données sont valides, ses ancêtres ne sont pas retirés, son Publisher n’est pas moved, son status est scheduled ou published, publish_at ≤ T et son accès effectif est public. Une Publication future ou restreinte est exclue, même sous un Canal public. Un Canal retiré peut conserver un RSS vide. Les éléments éligibles ne sont pas dupliqués et un générateur DEVRAIT les écrire du plus récent au plus ancien, avec l’ID comme départage stable.

La sélection de référence conserve tous les éléments éligibles. Un hébergeur PEUT limiter l’historique RSS pour ses besoins, en documentant cette limite hors Feed ; cette coupe n’est jamais un retrait Comic Feed.

### 14.3 Correspondance normative du profil

| Élément RSS | Présence du profil | Valeur |
| --- | --- | --- |
| rss/@version | O | 2.0. |
| channel | O | Un seul élément channel. |
| channel/title | O | Nom lisible de Série et Canal ; libre composition. |
| channel/link | O | URL absolue de channels[].url. |
| channel/description | O | Présentation textuelle ; repli descriptif si la Série n’a pas de description. |
| channel/language | F | Langue déclarée du Canal, à défaut celle de la Série. |
| channel/lastBuildDate | F | Instant de modification du RSS ; peut être sa génération si son contenu change. |
| item/guid | O | itm_ complet et attribut isPermaLink="false". |
| item/title | O | Titre si non vide ; sinon libellé composé du titre du Canal et de la date publish_at. |
| item/link | O | URL absolue de publications[].url. |
| item/pubDate | O | publish_at, converti en date RSS UTC avec année à quatre chiffres. |
| item/description | F | Présentation sûre, éventuellement miniature et lien de lecture. |

Les dates sont rendues comme Mon, 05 Oct 2026 10:00:00 GMT, avec les noms de jour et mois anglais corrects ; les fractions de seconde sont omises. L’ordre peut utiliser la précision complète de Comic Feed, même si RSS n’affiche que la seconde. Le GUID ne change ni lors d’une correction ni lors d’un déplacement du site.

### 14.4 Texte et médias

Les titres et métadonnées sont échappés pour XML. Si le générateur compose une description HTML, il doit d’abord échapper les textes provenant du Feed pour HTML, puis sérialiser ce fragment comme texte XML ou CDATA. Une description du Feed n’est jamais copiée comme balisage de confiance. Le choix CDATA ne rend pas sûr un script ou un attribut actif.

Le profil de référence emploie une description textuelle simple et peut ajouter une miniature PNG/JPEG avec un lien absolu. Il n’exige ni Media RSS ni extension Comic Feed. La lecture ordinaire repose sur item/link : un agrégateur n’est pas tenu d’intégrer les images, WebP ou les longs épisodes. Un enclosure est facultatif et n’est utilisable que si son URL, son type MIME et sa longueur réelle en octets sont connus ; il ne représente pas à lui seul un épisode segmenté. L’élément channel/image facultatif reste soumis aux formats et dimensions du standard RSS, distincts des visuels Comic Feed.

### 14.5 Programmation et corrections

Le générateur n’inclut pas d’élément futur. Pour le faire apparaître plus tard, le RSS doit être régénéré et redéployé après son échéance. Un fichier statique ne se modifie pas avec le temps, et RSS n’oblige pas tous les agrégateurs à masquer les dates futures. Cette limite ne modifie pas l’activation locale de Comic Feed.

Une correction met à jour l’élément existant en conservant guid et pubDate. Une mention textuelle de correction PEUT être incluse ; le profil ne promet pas qu’un agrégateur la signalera. Un retrait supprime l’élément du RSS régénéré, mais ne peut forcer la suppression des copies déjà archivées par les agrégateurs. Aucun nouvel item de retrait n’est créé par ce profil. Comic Feed reste la source des états structurés.

## Annexe A Catalogue des exemples

Le dossier demo contient trois Publishers indépendants : Atelier Aube, Éditions Brume et Studio Rivage. Les domaines .example sont réservés à l’illustration et ne correspondent pas à des sites hébergés. mapping.json associe chaque URL canonique fictive à son dossier local ; ce fichier est un outil de démonstration, pas un champ ni une dépendance du protocole.

Aube illustre plusieurs Séries, un Canal strip et un Canal webtoon publics, une programmation, une correction signalée, un retrait minimal et une Série à accès mixte. Brume illustre deux Canaux webtoon de la même Série et des URLs absolues. Rivage illustre l’inactivité, les surcharges d’accès et un ancien Feed moved qui mène à son emplacement courant avec le même ID.

Les fichiers scenarios présentent des versions successives de documents existants, avec un contexte de résolution et des résultats attendus dans manifest.json. Les scénarios incluent programmation avant/après échéance, correction silencieuse, correction signalée et retrait. Les IDs conservés y sont intentionnels. Les dossiers invalid et compatibility sont distincts des références valides.

## Annexe B Exemples invalides

invalid/manifest.json décrit chaque exemple et le diagnostic principal attendu, ainsi que son contexte et, si nécessaire, le document parent ou l’état antérieur. Les cas syntaxiques sont stockés avec l’extension .invalid.json pour être inspectables sans être confondus avec des références valides. Les cas compatibility décrivent une capacité de lecture ; ils ne sont pas présentés comme des erreurs JSON.

## Annexe C Arborescence et utilisation

README.md décrit l’ouverture de SPECIFICATION.html, les dossiers de chaque Publisher et les emplacements de médias. Les images sont des fichiers de test sans œuvre réelle. Les pages HTML sont des cibles factices pour les URLs de lecture RSS, sans application Reader.

Les chemins sont relatifs à l’intérieur des packages quand cela est pertinent. Pour un hébergement réel, les URLs absolues fictives et le contenu absolu des RSS doivent être remplacés ou régénérés à partir des véritables bases. Les tests HTTPS/CORS sur plusieurs origines réelles relèvent de l’étape de déploiement et ne sont pas prouvés par l’ouverture des fichiers locaux.

## Annexe D Références et provenance

Le cahier des charges Comic Feed 1.0 du 24 septembre 2026, la décision RSS et les précisions P1 à P7 validées le 5 octobre constituent la provenance de cette édition. Le lecteur n’a pas besoin du cahier pour appliquer les règles ci-dessus.

- [RFC 8259 JSON](https://www.rfc-editor.org/rfc/rfc8259).
- [RFC 3339 Dates Internet](https://www.rfc-editor.org/rfc/rfc3339), selon le profil explicite de la section 3.
- [RFC 9562 UUID](https://www.rfc-editor.org/rfc/rfc9562.html).
- [RFC 5646 Langues BCP 47](https://www.rfc-editor.org/rfc/rfc5646.html).
- [RFC 3986 Références URI](https://www.rfc-editor.org/rfc/rfc3986).
- [Fetch Standard et CORS](https://fetch.spec.whatwg.org/#http-cors-protocol).
- [RSS 2.0](https://www.rssboard.org/rss-specification).
- [RSS Best Practices Profile](https://www.rssboard.org/rss-profile), complément informatif.
- [RSS Encoding Examples](https://www.rssboard.org/rss-encoding-examples), complément informatif.
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core), pour les schémas d’accompagnement.

