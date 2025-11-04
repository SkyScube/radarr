# Guide d'utilisation

Ce guide vous explique comment utiliser l'outil d'export de rapports Active Directory.

## Démarrage rapide

### Activation de l'environnement virtuel

Avant d'utiliser l'outil, activez l'environnement virtuel :

```bash
source venv/bin/activate
```

### Exécution basique

Pour générer un export complet avec tous les rapports disponibles :

```bash
python multi_export.py --name inventaire
```

Cette commande génère un fichier `inventaire.json` contenant tous les rapports Active Directory.

## Options disponibles

### Nom du fichier de sortie (obligatoire)

L'option `--name` est **obligatoire** et définit le nom du fichier JSON généré :

```bash
python multi_export.py --name mon_rapport
```

Résultat : `mon_rapport.json`

### Rapports sélectifs

Par défaut, tous les rapports sont générés. Vous pouvez sélectionner des rapports spécifiques :

#### Rapport des utilisateurs

```bash
python multi_export.py --name users_report --users
```

#### Rapport des groupes

```bash
python multi_export.py --name groups_report --groups
```

#### Rapport des ordinateurs

```bash
python multi_export.py --name computers_report --computers
```

#### Rapport des contrôleurs de domaine

```bash
python multi_export.py --name dc_report --domain-controllers
```

### Combinaison de rapports

Vous pouvez combiner plusieurs options pour générer uniquement les rapports souhaités :

```bash
python multi_export.py --name custom_report --users --groups
```

Cette commande génère un fichier contenant uniquement les rapports des utilisateurs et des groupes.

## Types de rapports disponibles

| Rapport | Option | Description |
|---------|--------|-------------|
| Utilisateurs | `--users` | Liste tous les utilisateurs du domaine Active Directory |
| Groupes | `--groups` | Liste tous les groupes et leurs membres |
| Ordinateurs | `--computers` | Liste toutes les machines du domaine |
| Contrôleurs de domaine | `--domain-controllers` | Liste les contrôleurs de domaine |

## Structure du fichier de sortie

Le fichier JSON généré a la structure suivante :

```json
{
  "serveur": "192.168.151.39",
  "rapports": [
    {
      "rapport": "users",
      "titre": "Utilisateurs du domaine",
      "donnees": [...]
    },
    {
      "rapport": "groups",
      "titre": "Groupes Active Directory",
      "donnees": [...]
    }
  ]
}
```

## Exemples d'utilisation

### Exemple 1 : Export complet pour inventaire

```bash
python multi_export.py --name inventaire
```

Génère un export complet avec tous les rapports.

### Exemple 2 : Audit des utilisateurs uniquement

```bash
python multi_export.py --name audit_users --users
```

Génère uniquement le rapport des utilisateurs.

### Exemple 3 : Rapport infrastructure

```bash
python multi_export.py --name infrastructure --computers --domain-controllers
```

Génère un rapport contenant les ordinateurs et les contrôleurs de domaine.

## Affichage de l'aide

Pour afficher toutes les options disponibles :

```bash
python multi_export.py --help
```

## Dépannage

### Erreur de connexion SSH

Si vous rencontrez une erreur de connexion, vérifiez :
- Que le serveur Active Directory est accessible (ping, réseau)
- Que les identifiants dans `multi_export.py` sont corrects
- Que le port SSH (22) est ouvert sur le serveur

### Fichier de sortie non créé

Vérifiez :
- Que vous avez les droits d'écriture dans le répertoire courant
- Que l'option `--name` est bien spécifiée
- Que la connexion SSH s'est bien établie (consultez les messages d'erreur)

## Notes importantes

- L'outil se connecte par défaut à `192.168.151.39` avec les identifiants configurés
- Les fichiers JSON sont générés dans le répertoire courant
- Une connexion SSH active est requise pour chaque exécution
- Les données sont collectées en temps réel depuis le serveur Active Directory
