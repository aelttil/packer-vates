# GitHub Actions Runner

Ce document explique où est stocké le runner GitHub Actions auto-hébergé et comment il fonctionne.

## Emplacement du runner

Le runner GitHub Actions auto-hébergé est installé sur une machine que vous contrôlez. Lorsque vous configurez un runner auto-hébergé, vous téléchargez et exécutez un script d'installation qui:

1. Crée un répertoire pour le runner (généralement `actions-runner` dans le répertoire où vous exécutez le script)
2. Télécharge les binaires du runner
3. Configure le runner pour qu'il se connecte à votre dépôt GitHub

Par défaut, les fichiers du runner sont stockés dans le répertoire `actions-runner` sur la machine où vous l'avez installé. Ce répertoire contient:

- Les binaires du runner
- Les fichiers de configuration
- Les journaux d'exécution
- Un répertoire `_work` où les workflows sont exécutés

## Structure des répertoires

```
actions-runner/
├── bin/                  # Binaires du runner
├── externals/            # Dépendances externes
├── _work/                # Répertoire de travail où les workflows sont exécutés
│   └── {repo-name}/      # Un répertoire par dépôt
│       └── {job-name}/   # Un répertoire par job
├── .runner               # Fichier de configuration du runner
├── .credentials          # Informations d'authentification (chiffrées)
├── .path                 # Variables d'environnement PATH
├── config.sh             # Script de configuration
├── run.sh                # Script pour démarrer le runner
└── svc.sh                # Script pour gérer le runner comme un service
```

## Répertoire de travail

Le répertoire `_work` est particulièrement important car c'est là que les workflows sont exécutés. Lorsqu'un workflow est déclenché, le runner:

1. Crée un répertoire pour le job dans `_work/{repo-name}/{job-name}/`
2. Clone le dépôt dans ce répertoire
3. Exécute les étapes du workflow dans ce répertoire

Après l'exécution du workflow, les fichiers générés restent dans ce répertoire jusqu'à ce qu'ils soient nettoyés par le runner ou manuellement.

## Configuration comme service

Pour que le runner s'exécute en arrière-plan et démarre automatiquement au démarrage de la machine, vous pouvez le configurer comme un service:

```bash
cd actions-runner
./svc.sh install
./svc.sh start
```

Cela crée un service système (systemd sur Linux, launchd sur macOS, ou service Windows) qui démarre automatiquement le runner.

## Mise à jour du runner

Le runner se met à jour automatiquement lorsque de nouvelles versions sont disponibles. Cependant, vous pouvez également le mettre à jour manuellement:

```bash
cd actions-runner
./config.sh
```

## Nettoyage

Si vous souhaitez nettoyer les fichiers générés par les workflows, vous pouvez supprimer le contenu du répertoire `_work`:

```bash
cd actions-runner
rm -rf _work/*
```

Cependant, soyez prudent car cela supprimera tous les fichiers générés par les workflows précédents.

## Plusieurs runners

Vous pouvez installer plusieurs runners sur la même machine en créant plusieurs répertoires `actions-runner` et en configurant chaque runner avec un nom différent:

```bash
mkdir actions-runner-1
cd actions-runner-1
# Télécharger et configurer le runner avec un nom spécifique
./config.sh --name "runner-1"
```

Cela vous permet d'exécuter plusieurs workflows en parallèle sur la même machine.
