# Guide d'installation

Ce guide vous explique comment installer et configurer l'outil d'export de rapports Active Directory.

## Prérequis

- Python 3.7 ou supérieur
- Git
- Accès réseau au serveur Active Directory cible

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/BTS-ESNA-2024-2026/Projet-RADAR-B.git
cd Projet-Radar-B
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
```

### 3. Activer l'environnement virtuel

**Sous Linux/macOS :**
```bash
source venv/bin/activate
```

**Sous Windows :**
```cmd
venv\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requierements.txt
pip install paramiko
```

> **Note :** Le package `paramiko` est nécessaire pour la connexion SSH mais n'est pas listé dans `requierements.txt`. Il doit être installé manuellement.

## Configuration

Par défaut, l'outil est configuré pour se connecter à :
- **Hôte :** `192.168.151.39`
- **Utilisateur :** `Administrateur`
- **Mot de passe :** `AdminP4ss`

Pour modifier ces paramètres, éditez le fichier `multi_export.py` et modifiez les constantes dans la classe `ADReportExporter` :
```python
DEFAULT_HOST = "192.168.151.39"
DEFAULT_USERNAME = "Administrateur"
DEFAULT_PASSWORD = "AdminP4ss"
```

## Vérification de l'installation

Pour vérifier que l'installation s'est bien déroulée, exécutez :

```bash
python multi_export.py --help
```

Vous devriez voir s'afficher l'aide de la commande avec toutes les options disponibles.

## Désactivation de l'environnement virtuel

Lorsque vous avez terminé, vous pouvez désactiver l'environnement virtuel avec :

```bash
deactivate
```
