# Déclenchement du pipeline GitHub Actions

Ce document explique pourquoi le pipeline GitHub Actions peut ne pas démarrer et comment le déclencher manuellement.

## Raisons possibles pour lesquelles le pipeline ne démarre pas

D'après le fichier `.github/workflows/build-template.yml`, le pipeline est configuré pour se déclencher dans les cas suivants:

1. Lors d'un push sur la branche `main` qui modifie des fichiers dans le dossier `packer/` ou le fichier `.github/workflows/build-template.yml`
2. Lors d'une pull request vers la branche `main`
3. Manuellement via l'interface GitHub Actions (workflow_dispatch)

Si vous avez commité les modifications mais que le pipeline ne démarre pas, cela peut être dû à l'une des raisons suivantes:

### 1. Le commit n'a pas été poussé vers la branche `main`

Vérifiez que vous avez bien poussé votre commit vers la branche `main` et non vers une autre branche:

```bash
git branch  # Affiche la branche actuelle
git push origin main  # Pousse les commits vers la branche main
```

### 2. Le commit n'a modifié que le fichier `process_template.py`

Le fichier `process_template.py` n'est pas dans la liste des chemins qui déclenchent le workflow. Seuls les fichiers dans le dossier `packer/` et le fichier `.github/workflows/build-template.yml` déclenchent le workflow.

Pour que le workflow se déclenche, vous devez modifier l'un des fichiers suivants:
- Un fichier dans le dossier `packer/`
- Le fichier `.github/workflows/build-template.yml`

Vous pouvez également ajouter le fichier `process_template.py` à la liste des chemins qui déclenchent le workflow:

```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'packer/**'
      - '.github/workflows/build-template.yml'
      - 'process_template.py'  # Ajoutez cette ligne
```

### 3. Le runner auto-hébergé n'est pas en ligne

Vérifiez que le runner auto-hébergé est en ligne et correctement configuré:

1. Allez dans les paramètres de votre dépôt GitHub
2. Cliquez sur "Actions" dans le menu de gauche
3. Cliquez sur "Runners"
4. Vérifiez que le runner avec le label `self-hosted` est en ligne (point vert)

Si le runner n'est pas en ligne, vous devez le démarrer:

```bash
cd /chemin/vers/le/runner
./run.sh
```

## Déclenchement manuel du workflow

Si vous ne pouvez pas résoudre le problème, vous pouvez déclencher manuellement le workflow:

1. Allez dans l'onglet "Actions" de votre dépôt GitHub
2. Cliquez sur "Build and Upload Template" dans la liste des workflows
3. Cliquez sur "Run workflow"
4. Sélectionnez la branche sur laquelle vous voulez exécuter le workflow
5. Entrez le nom du template à construire (par défaut: `debian12`)
6. Cliquez sur "Run workflow"

## Modification du workflow pour inclure `process_template.py`

Pour que le workflow se déclenche automatiquement lorsque vous modifiez le fichier `process_template.py`, vous pouvez modifier le fichier `.github/workflows/build-template.yml`:

```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'packer/**'
      - '.github/workflows/build-template.yml'
      - 'process_template.py'  # Ajoutez cette ligne
      - '*.py'  # Ou cette ligne pour inclure tous les fichiers Python
```

Après avoir modifié le fichier, poussez les modifications vers la branche `main`:

```bash
git add .github/workflows/build-template.yml
git commit -m "Ajout de process_template.py aux déclencheurs du workflow"
git push origin main
