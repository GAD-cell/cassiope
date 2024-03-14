# Méta-analyse de papiers de recherche

Projet Cassiopée 2023-2024

Axel Benadiba, Sinoué Gad, Paul Guilloux

## Objectif

Lorsque des scientifiques veulent présenter un résultat, ils écrivent un article scientifique. Ces articles sont très codifiés : ils suivent souvent la même structure, ils doivent être bien présentés, sans faute, avec la bonne longueur, ...

Réussir à respecter ces standards est important car les articles sont évalués par la communauté pour savoir s’ils doivent être présentés dans une conférence, ce qui est le but ultime. Outre les critères scientifiques, les aspects liés à la présentation peuvent avoir un fort effet. Il est toujours dommage d’échouer à cause d’un problème qui pourrait être facilement rectifié.

Dans ce projet, nous proposons de construire un outil capable d’évaluer un papier scientifique pour corriger les erreurs les plus évidentes et proposer des idées d’amélioration. L’interface utilisateur passera par une interface web, mais le serveur pourra être codé dans un langage quelconque.

Les étapes du projet seront les suivantes:

- Transformation de papiers au format PDF en un format plus structuré. Les articles sont souvent écrits en LaTeX, mais seul le PDF est communiqué. Il faudra être capable de restructurer le PDF.
- Analyse de données sur les papiers existants. Nous consulterons une base de données de papiers déjà écrits pour en extraire des règles communes aux articles les plus populaires. Ces règles seront ensuite ajoutées au système final.
- Implémentation du système de vérification. Etant donné un article, nous voulons pouvoir écrire la liste de améliorations et corrections possible.
- Création d’une interface. Un utilisateur devra pouvoir interagir avec notre outil à travers une interface Web.

