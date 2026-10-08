# Passage de Comic Feed 1.0 à 1.1

Édition du 8 octobre 2026. Extension des formats validée point par point.

## Changements normatifs

| Section | Changement |
| --- | --- |
| 1 | Séparation explicite du protocole et des décisions d’interface du Reader. |
| 3.3 | L’ordre de resources devient également normatif pour Pages. |
| 4.1 et 5.1 | Version 1.1 des nouveaux documents ; conservation des documents 1.0 selon leur édition. |
| 6, 6.1 | Ajout de square et pages ; deux familles utilisant la même Publication. |
| 6.2 | reading_direction facultatif, uniquement sur pages : ltr ou rtl ; absence = ltr. |
| 7.2 | Exactement une image pour Strip/Square ; au moins une pour Webtoon/Pages lorsque resources est fourni sur une Publication non retirée. Aucun plafond universel ni ratio Square imposé. |
| 12.1 | Compatibilité document par document : Publisher 1.0 / Série 1.1 admis ; isolation des types inconnus. |
| 13 | Contrôles des nouveaux types et du périmètre du champ ; diagnostic documentaire CF_FIELD_SCOPE. |
| 14 | RSS Square avec gag complet ; RSS Pages avec annonce, miniature facultative et lien, sans export automatique des pages. |

Le seul nouveau champ standard est `channels[].reading_direction`. Aucun `pages[]`, `page_count`, ID de page, objet Chapitre ou réglage de Reader n’est ajouté.

## Socle conservé

La hiérarchie Publisher → Série → Canal → Publication, les UUID préfixés, la permanence du type de Canal, les champs de Publication, les formats JPEG/PNG/WebP, l’accès effectif, les états, les dates, les corrections, retraits, déplacements, références relatives, HTTPS/CORS et les principes de sécurité sont conservés.

La liste de plusieurs images Webtoon existait déjà en 1.0. Les Feeds à une seule longue image ne nécessitent aucun changement. La version du protocole ne modifie pas automatiquement celle du Reader.

`CHANGES.diff` expose les modifications exactes du texte. Les fichiers de `reference-1.0` restent identiques aux sources de l’édition précédente.

## Portée de cette livraison

L’étape A3 comprend la spécification consolidée, ses schémas, des exemples documentaires complets, les cas de test et la note séparée des comportements Reader validés. Les médias des nouveaux exemples sont des emplacements documentaires ; le ZIP n’est pas un déploiement du corpus SPOON/CUVIER.

L’étape suivante A4 préparera le corpus réel en préservant le catalogue Eigrutel courant. Le développement Square puis Pages aura lieu dans le fil Reader.
