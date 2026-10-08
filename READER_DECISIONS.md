# Décisions pour le Reader et le Collector de référence

Validées le 8 octobre 2026 lors de la préparation de Comic Feed 1.1.

**Statut : document d’application, distinct de la spécification normative du protocole.** Ces décisions orientent le futur Reader Eigrutel et les fonctions personnelles du Collector. Elles ne sont pas des conditions de conformité pour un logiciel tiers. Aucune application ni aucun moteur n’est développé ou modifié par ce livrable.

## 1 Périmètre

Le Reader de référence de départ est la version 0.8.7. Les moteurs Strip et Webtoon existants doivent être préservés. Square doit réutiliser les fonctions communes du lecteur Strip ; Pages doit utiliser les données éditoriales communes à Webtoon avec un mode de lecture paginé. L’ajout des formats ne justifie pas la réécriture des deux moteurs existants.

Les quatre formats doivent pouvoir être présentés dans l’accueil, la fiche Série, la bibliothèque, les archives ou listes d’épisodes. La configuration `channel_type` doit reconnaître les quatre valeurs, en plus des scopes Publisher, Série et Canal existants. Ces scopes sont propres au Reader : ils n’entrent pas dans le Feed.

La sélection des Publications éligibles réutilise les règles du protocole et le périmètre du Reader. Les textes d’interface sont disponibles en FR/EN et les fonctions restent utilisables sur ordinateur, tablette et téléphone, en portrait et en paysage, avec accès clavier.

## 2 Square

- Une image complète, intégralement visible dans sa présentation normale, sans déformation ni recadrage destructeur.
- Navigation précédente/suivante, aléatoire, archives et accès direct depuis une miniature ; réutiliser les fonctions existantes du Strip.
- Fiche Série et archives : miniature cliquable et date uniquement. L’accès doit fonctionner au clavier et posséder un nom accessible, sans ajouter un titre technique visible.
- Aucun titre de Publication, nom de fichier ou bouton répétitif « Lire le gag » affiché. Le titre éditorial facultatif reste conservé dans les données.
- Le nom de la Série reste disponible lorsqu’il aide la navigation.

## 3 Ordre des Publications et passage entre chapitres

Pour les nouveaux formats, précédente/suivante désignent les Publications voisines du même Canal, dans le scope du Reader, triées par instant `publish_at` croissant puis par ID dans un ordre lexicographique stable. L’accueil peut afficher l’ordre inverse. L’aléatoire Square est limité au même ensemble de Publications éligibles. Une correction ne change pas la position chronologique en utilisant `updated_at` à la place de `publish_at`.

Les pages internes suivent strictement l’ordre de `resources`. « Page suivante » et « Page précédente » restent dans le chapitre. À une extrémité, un balayage ou une commande de page ne franchit pas automatiquement la frontière du chapitre. Une action explicitement nommée « Chapitre suivant » ou « Chapitre précédent » permet le franchissement lorsqu’une destination éligible existe. L’emplacement exact des commandes sera décidé dans le fil Reader.

Le chapitre rejoint suit la règle de reprise ci-dessous : position mémorisée, sinon première page. Une action permet toujours de recommencer à la première page. Pour une première lecture de CUVIER : chapitre 1, pages 1 à 8 ; action « Chapitre suivant » ; chapitre 2, pages 1 à 2.

Les contenus futurs, retirés ou sans autorisation ne peuvent pas être ouverts par ces commandes. La lecture d’un contenu `scheduled` arrivé à échéance demeure possible selon les mêmes règles d’accès que les autres Publications.

## 4 Sens de lecture : conventions du Reader

Le champ de Canal `reading_direction` est défini par le protocole. Les conventions ci-dessous concernent le Reader de référence :

| Action | ltr | rtl |
| --- | --- | --- |
| Page suivante au clavier | Flèche droite. | Flèche gauche. |
| Page précédente au clavier | Flèche gauche. | Flèche droite. |
| Geste vers la page suivante | Balayage vers la gauche. | Balayage vers la droite. |
| Geste vers la page précédente | Balayage vers la droite. | Balayage vers la gauche. |
| Placement du bouton « Suivant » | À droite. | À gauche. |

Précédent et Suivant gardent leur signification narrative. L’ordre des images et la progression 1 / N, 2 / N, etc. ne sont jamais inversés. Les raccourcis doivent être intégrés sans perturber la saisie dans les champs ni l’accessibilité des commandes.

## 5 Reprise Pages

La position personnelle est associée à l’ID permanent de la Publication, dans son appartenance vérifiée. Le stockage local conserve le numéro de la page, la référence de l’image comme aide de repositionnement et l’état connu de la liste des ressources. La référence d’image est un indice technique, jamais une identité permanente de page.

| Situation | Reprise |
| --- | --- |
| Chapitre jamais ouvert | Première page. |
| Liste de ressources inchangée | Page mémorisée. |
| Liste réorganisée ou augmentée, ressource mémorisée retrouvée sans ambiguïté | Même image à sa nouvelle position. |
| Liste modifiée, ressource impossible à retrouver sûrement | Première page et indication discrète que le chapitre a changé et que la reprise se fait au début. |
| Publication retirée ou devenue inaccessible | Conserver la position personnelle, sans ouvrir ses images. |

Une référence répétée ou un changement général d’adresses ne doit pas être présenté comme une identification certaine. La comparaison des références doit tenir compte de leur contexte de résolution et des migrations déjà vérifiées ; les détails techniques seront traités lors du développement. Si la correspondance reste incertaine, la règle de retour annoncé au début s’applique.

La position est distincte de l’état lu/non lu. Remettre un chapitre en non lu ne supprime pas sa position. Ce document ne fixe pas de nouvelle règle de marquage automatique « lu » à l’arrivée sur la dernière page.

Le Collector utilisera IndexedDB et inclura ces informations dans l’export/import des données personnelles. Aucune progression, identité de lecteur ni sauvegarde personnelle n’est ajoutée au Feed ; aucun compte ou service central n’est nécessaire.

## 6 Zoom et déplacement Pages

| Situation | Comportement |
| --- | --- |
| Ouverture ou changement de page | Page entière visible dans l’espace disponible, sans déformation ni recadrage. |
| Zoom tactile | Pincement à deux doigts. |
| Déplacement d’une image agrandie | Glissement dans l’image, sans changement de page. |
| Zoom sur ordinateur | Commandes accessibles à la souris et au clavier. |
| Déplacement sur ordinateur | Glisser avec la souris et moyen également accessible au clavier. |
| Retour à la vue entière | Action explicite « Page entière ». |

En vue entière, le balayage peut naviguer entre les pages. En vue agrandie, le glissement déplace uniquement l’image ; le pincement règle le zoom. Les commandes explicites de changement de page restent disponibles ; les flèches simples du clavier conservent leur fonction précédente/suivante. Les moyens de déplacement au clavier devront éviter ce conflit de raccourcis.

La reprise rétablit la page atteinte en vue entière ; elle ne restaure pas le grossissement ni le déplacement antérieur. L’apparence des commandes, les raccourcis complémentaires, les seuils de gestes et les paramètres de zoom seront définis lors du travail Reader.

## 7 Admin, miniatures et corpus à venir

L’Admin doit réutiliser les formulaires et mécanismes communs : import d’une image pour Square ; import et réorganisation d’images pour un chapitre Pages ; sens de lecture au niveau Canal ; métadonnées, Feed et RSS.

Les miniatures seront créées ou choisies à partir d’un visuel adapté. La qualité sera contrôlée pour éviter une image devenue illisible par réduction d’une longue planche entière. Le protocole ne prescrit pas de taille de miniature ni de technique de recadrage. Les visuels de lecture demeurent entiers.

Le corpus réel attendu est SPOON : trois Publications Square ; CUVIER : deux Publications Pages de huit et deux images. Les dates manquantes seront clairement marquées comme dates de démonstration, sans inventer une publication historique.

L’intégration dans le Publisher Eigrutel nécessite d’abord de lire son corpus courant : conserver ses IDs, enrichir une Série existante si elle correspond déjà à l’œuvre, ou créer une nouvelle Série dans le cas contraire. Un Canal existant n’est pas retypé. Toute modification suit les règles de propagation de `updated_at`. Aucune modification du catalogue existant n’est réalisée dans l’étape A3.

## 8 Vérifications ultérieures

Les tests du Reader devront couvrir les comportements ci-dessus, les deux sens de lecture, le zoom tactile, la reprise après réorganisation, les passages entre chapitres, les scopes, les accès, le cache, les liens de suivi, FR/EN et l’accessibilité. Les moteurs Strip et Webtoon devront être vérifiés sans régression. Les anciens lecteurs devront conserver les Canaux compris lorsqu’ils rencontrent des types nouveaux.

Les tests sur le Reader 0.8.7, les agrégateurs RSS et plusieurs Publishers réellement hébergés restent à exécuter. Les exemples de données et contrôles hors ligne de cette livraison ne prouvent pas ces comportements d’application.
