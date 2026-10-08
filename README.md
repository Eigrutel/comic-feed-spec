# Comic Feed 1.1 — spécification

Édition du 8 octobre 2026. Étape A3 : formalisation des décisions Square/Pages validées.

Ouvrir **SPECIFICATION.html** pour lire le document hors ligne avec son sommaire. Le même texte est disponible dans **SPECIFICATION.md**.

| Fichier ou dossier | Contenu |
| --- | --- |
| SPECIFICATION.md / SPECIFICATION.html | Spécification normative consolidée 1.1. |
| CHANGES.md / CHANGES.diff | Résumé et différences exactes avec 1.0. |
| schemas/ | Deux schémas structurels pour les documents déclarant 1.1. |
| examples/ | Publisher 1.0, deux Séries 1.1 et deux RSS ; données fictives, médias non déployés. |
| cases/ | Cas valides, invalides et de consommation partielle. |
| READER_DECISIONS.md | Comportements validés du Reader/Collector, hors norme du protocole. |
| reference-1.0/ | Référence précédente conservée sans modification, avec trois Publishers indépendants. |
| checks/ | Vérifications internes reproductibles, sans application Reader ni validateur général. |
| VERIFICATION.md / VERIFICATION.json | Contrôles exécutés et limites. |
| SHA256.json | Empreintes des fichiers du dossier, hors ce manifeste lui-même. |

## Utilisation des exemples

Les domaines .example ne sont pas des sites disponibles. Les nouveaux Feed sont complets en tant que données ; leurs adresses d’images et de lecture sont des emplacements prévus. La vérification de leur hébergement n’est pas réalisée. Le corpus SPOON/CUVIER sera préparé séparément à l’étape A4.

Les variantes sous cases représentent des états alternatifs : ne pas les fusionner. Choisir le schéma correspondant à la version de chaque document. Les Feed 1.0 de référence restent valides selon l’édition 1.0, y compris lorsque leur index pointe vers une Série 1.1.

Les résultats historiques sous reference-1.0 sont conservés pour provenance. Le rapport situé à la racine décrit les contrôles de cette livraison. Les décisions Reader ne prouvent pas leur implémentation ; le Reader 0.8.7 n’a pas été modifié.

## Reproduire les contrôles

Depuis ce dossier :

```sh
python3 checks/check_reference_1_0.py
python3 checks/check_1_1.py
```

Python 3 et Pillow sont nécessaires pour le décodage des médias de référence 1.0. L’évaluateur structurel interne ne prend en charge que les mots-clés des schémas livrés ; il ne remplace pas un moteur JSON Schema général. Les scripts ne font aucun accès réseau. Ils écrivent leurs résultats sous checks ; aucun Feed ni fichier de référence n’est modifié.
