# Comic Feed 1.0

Livrables de l’étape 1, édition du 5 octobre 2026.

Ouvrir **SPECIFICATION.html** dans un navigateur pour lire le document avec son sommaire. Tout le texte et la mise en forme sont intégrés ; aucune connexion n’est requise. SPECIFICATION.md contient le même texte normatif dans un format simple à versionner.

## Contenu

| Chemin | Usage |
| --- | --- |
| SPECIFICATION.md et SPECIFICATION.html | Spécification complète en 14 sections et annexes. |
| schemas/ | Deux schémas JSON Schema 2020-12 autonomes, de portée structurelle. |
| demo/aube/feed.json | Publisher Atelier Aube ; trois Séries, dont une retirée. |
| demo/brume/feed.json | Publisher Éditions Brume ; une Série et deux Canaux webtoon. |
| demo/rivage/feed.json | Publisher Studio Rivage ; inactivité, accès et Canal retiré. |
| demo/rivage-ancien/feed.json | Déplacement vers Rivage avec le même publisher.id. |
| scenarios/ | Documents complets avant/après de correction et retrait, plus évaluations de programmation. |
| invalid/ | 41 exemples volontairement non conformes avec diagnostics attendus. |
| compatibility/ | Trois exemples de versions ou formats futurs ; comportement prudent attendu. |
| mapping.json | Correspondance entre URLs fictives et dossiers locaux, hors protocole. |
| reference.json et ids.json | Inventaire des références et des IDs des exemples, hors protocole. |
| VERIFICATION.md et VERIFICATION.json | Résultats et limites des contrôles effectués. |

## Lire les exemples

Le catalogue de référence utilise trois Publishers indépendants, cinq Feed Série et cinq RSS. Les noms et œuvres sont fictifs. Les petites images PNG, JPEG et WebP sont des fichiers de test ; leurs dimensions ne constituent pas des recommandations de publication. Les pages HTML des Canaux et Publications sont des destinations factices pour les liens RSS, sans application Reader.

L’instant de référence est **2026-10-05T10:00:00Z**. Le RSS livré a été généré pour cet instant. Le strip programmé pour le 10 octobre n’y figure pas. Il devient disponible dans Comic Feed à l’échéance sans réécriture de son Feed ; il faut régénérer le RSS pour l’y ajouter.

Les documents de scenarios représentent des versions alternatives des mêmes IDs, à charger dans le contexte indiqué dans leur manifest. Ils ne doivent pas être fusionnés. Les avis de correction et de retrait conservent l’identité. Les documents invalid sont intentionnellement incorrects et ne doivent pas être utilisés comme catalogue.

## Hébergement de démonstration

Les domaines aube.example, brume.example, rivage.example et archives-rivage.example sont des adresses de documentation, sans site effectivement déployé. mapping.json permet les vérifications hors ligne sans les contacter.

Pour une simple inspection locale, on peut servir le dossier demo avec la commande suivante depuis la racine de ce dossier livré :

    python3 -m http.server 8000 --bind 127.0.0.1 --directory demo

Cela ne remplace pas les URLs absolues fictives dans les Feed ni dans les RSS et ne configure pas CORS. Pour tester un déploiement réel, associer chaque dossier Publisher à sa propre base HTTP(S), remplacer les URLs absolues fictives, régénérer les RSS et vérifier les en-têtes CORS. Les chemins relatifs restent résolus depuis le Feed qui les contient.

## Statut du livrable

La structure et les précisions P1 à P7 ont été validées avant rédaction. Cette livraison couvre la spécification et ses exemples de référence. Elle n’inclut pas les applications Reader, Admin ou Collector, ni le validateur futur. Les schémas ne remplacent pas les contrôles sémantiques du texte.

La conformité technique d’un Feed n’atteste pas les droits sur les œuvres. Le protocole est réimplémentable indépendamment d’Eigrutel ; la licence éditoriale de diffusion de la spécification reste à formaliser conformément au cahier de référence.
