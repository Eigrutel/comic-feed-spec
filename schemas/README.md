# Schémas Comic Feed 1.1

Ces deux schémas JSON Schema 2020-12 sont des aides structurelles à la spécification. Chaque $ref est interne ; le $id documentaire ne demande aucun téléchargement.

- Pour un document déclarant 1.1, utiliser publisher.schema.json ou series.schema.json selon sa forme.
- Pour un document déclarant 1.0, utiliser les schémas inchangés de ../reference-1.0/schemas/.
- Ne pas appliquer un schéma 1.0 à tout un document 1.1 pour décider si un lecteur peut en conserver les Canaux connus. Cette consommation partielle relève de la section 12.

Le schéma Série 1.1 contrôle les quatre types, exactement une image pour Strip/Square, au moins une pour Webtoon/Pages lorsque resources est présent sur une Publication non retirée, l’obligation des ressources publiques, l’héritage d’accès et reading_direction uniquement pour Pages.

default: ltr documente la valeur implicite ; un validateur n’est pas tenu de modifier le JSON. Une valeur invalide présente ne doit jamais être remplacée silencieusement par ce défaut.

Les champs facultatifs inconnus restent tolérés. Les contrôles des URLs, dates civiles, langues, IDs dupliqués, relations, transitions, médias et transports complètent les schémas. Le rapport de vérification précise la portée réelle des outils exécutés.
