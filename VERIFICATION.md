# Vérification de Comic Feed 1.1

Édition du 8 octobre 2026. **141 contrôles internes réussis sur 141** : 79 contrôles de la référence 1.0 exécutés à nouveau et 62 contrôles liés à l’extension. Aucun échec restant dans ce périmètre.

## Contrôles effectués

| Ensemble | Vérification |
| --- | --- |
| Référence 1.0 | 79 contrôles : Feed, RSS, cas invalides, scénarios, identités, dates et décodage des médias factices. |
| Schémas 1.1 | JSON, références internes et contraintes employées ; schémas de producteur distincts selon l’édition. |
| Nouveaux exemples | Un Publisher 1.0 et deux Feed Série 1.1 ; concordance des IDs, index, dates et références relatives. |
| Ressources | Une image Strip/Square ; une ou plusieurs Webtoon/Pages ; exemples Pages de 1, 8, 2 et 33 images, retraits et annonces restreintes. |
| Sens de lecture | ltr, rtl et absence admis pour Pages ; valeurs invalides, null et présence sur les autres types refusées. |
| Accès | Héritage et surcharges public/restricted, accès explicite sous mixed et exclusions RSS. |
| Cas JSON | 8 cas valides, 19 cas invalides, 2 cas de compatibilité ; variantes non fusionnables. |
| RSS 1.1 | Deux RSS avec sélection à l’instant 2026-10-08T12:00:00Z, GUID, dates, URLs absolues et médias attendus. |
| RSS invalides | Quatre contre-exemples : contenu futur, contenu restreint, gag sans image et page de lecture exportée à la place d’une miniature. |
| Anciennes structures | Neuf Feed 1.0 projetés en mémoire en 1.1 : aucune nouvelle exigence imposée à leurs Canaux Strip/Webtoon. |
| Type permanent | Retypage Strip → Square avec le même chn_ refusé. |
| Consommation partielle | Simulation des règles de sélection des types connus, sans exécution d’un ancien Reader. |

Les 155 fichiers de reference-1.0 ont été comparés octet par octet aux sources précédentes au moyen de leurs empreintes SHA-256 : ils sont identiques. Les scripts de test écrivent leurs résultats sous checks et ne remplacent aucun Feed de référence.

La version HTML possède un sommaire de 18 entrées, des ancres uniques et résolues et des tables structurellement équilibrées. Le navigateur Chromium local n’étant pas disponible, son rendu visuel n’a pas été inspecté.

## Méthode et limites

Les tests sont internes et hors ligne. L’évaluateur de schéma est limité aux mots-clés effectivement employés dans les fichiers fournis ; aucun moteur JSON Schema tiers complet n’a été exécuté. Les contrôles de dates, relations, ressources, transitions et RSS complètent cette vérification structurelle. Ces scripts ne constituent pas le futur validateur général Comic Feed.

Les nouveaux médias 1.1 sont des emplacements documentaires : leurs octets, dimensions, disponibilité HTTP et netteté ne sont pas vérifiés. Le décodage réel effectué dans les tests concerne uniquement les médias factices déjà présents dans la référence 1.0. Un exemple de données structurellement valide n’est pas une preuve d’hébergement opérationnel.

Restent à effectuer : le corpus réel SPOON/CUVIER, les essais des applications Reader/Admin/Collector, la lecture dans des agrégateurs RSS réels et les tests HTTPS/CORS sur plusieurs hébergements indépendants. Aucune compatibilité effective du Reader 0.8.7 avec les nouveaux types n’est annoncée par cette livraison.

Le détail des 141 contrôles figure dans VERIFICATION.json. Les fixtures sont référencées par cases/manifest.json et checks/rss-invalid-cases.json. Les rapports historiques sous reference-1.0 restent clairement distincts du présent rapport.
