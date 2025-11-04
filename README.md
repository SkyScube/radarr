# Radarr

**Radarr** est un outil Python d'audit et de reporting pour Active Directory. Il permet de collecter et d'exporter des informations détaillées sur les utilisateurs, groupes, ordinateurs et contrôleurs de domaine via SSH en exécutant des commandes PowerShell distantes.

## Fonctionnalités

- **Audit des utilisateurs du domaine** : Liste tous les utilisateurs avec leurs propriétés (compte actif, verrouillé, expiration du mot de passe, etc.)
- **Inventaire des groupes Active Directory** : Énumère tous les groupes du domaine
- **Inventaire des machines** : Collecte la liste des ordinateurs avec leurs adresses IP
- **Informations sur les contrôleurs de domaine** : Récupère les détails des DC avec leurs rôles FSMO
- **Export multi-format** : Génère des rapports JSON structurés et des rapports HTML
- **Architecture modulaire** : Code organisé en classes réutilisables

## Prérequis

- Python 3.8+
- Accès SSH à un contrôleur de domaine Windows avec PowerShell
- Module ActiveDirectory PowerShell installé sur le serveur cible
- Compte avec droits d'administrateur de domaine

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-utilisateur/radarr.git
cd radarr
```

2. Installez les dépendances :
```bash
pip install -r requierements.txt
```

Les principales dépendances incluent :
- `paramiko` : Pour les connexions SSH
- `beautifulsoup4` : Pour le traitement HTML
- `requests` : Pour les requêtes HTTP
- `nbconvert` : Pour la conversion de formats

## Utilisation

### Mode basique

Pour exécuter toutes les collectes de données et générer un rapport JSON :

```bash
python multi_export.py --name mon_rapport
```

### Mode sélectif

Pour collecter uniquement certaines informations :

```bash
# Utilisateurs uniquement
python multi_export.py --users --name utilisateurs

# Groupes et ordinateurs
python multi_export.py --groups --computers --name inventaire

# Contrôleurs de domaine uniquement
python multi_export.py --domain-controllers --name dc_audit
```

### Exécution directe

Pour un test rapide avec `index.py` :

```python
from classe import ssh
from index import commande

# Configuration de connexion
hostname = "192.168.151.39"
username = "Administrateur"
password = "VotreMotDePasse"

# Connexion et collecte
t = ssh(hostname, username, password)
command = commande()
t.connect()

# Exécuter les commandes
users = command.user_domain(t)
groups = command.group_user_domain(t)
computers = command.computers_domain(t)
dcs = command.domain_controllers(t)

t.close_connection()
```

### Options disponibles

```
--users                  Inclut le rapport utilisateurs
--groups                 Inclut le rapport groupes
--computers              Inclut le rapport machines
--domain-controllers     Inclut le rapport contrôleurs de domaine
--name NOM              Nom du fichier JSON généré (obligatoire)
```

## Structure du projet

```
radarr/
├── classe.py               # Classe SSH pour connexions distantes
├── index.py                # Commandes principales d'audit AD
├── index2.py               # Version alternative des commandes
├── multi_export.py         # Script principal d'export multi-rapports
├── ad_commands.py          # Commandes AD additionnelles
├── commands.py             # Classes de base pour commandes PowerShell
├── executor.py             # Exécuteur de commandes
├── commande.ps1            # Scripts PowerShell
├── requierements.txt       # Dépendances Python
├── inventaire.json         # Exemple de sortie JSON
├── test.json               # Données de test
├── rapport.html            # Exemple de rapport HTML
├── tests/                  # Tests unitaires
│   └── test_multi_export.py
└── image/                  # Ressources images
```

## Format de sortie

Le rapport JSON généré contient une structure hiérarchique :

```json
{
  "serveur": "192.168.151.39",
  "rapports": [
    {
      "rapport": "users",
      "titre": "Utilisateurs du domaine",
      "donnees": [
        {
          "SamAccountName": "jdoe",
          "DisplayName": "John Doe",
          "UserPrincipalName": "jdoe@domain.local",
          "Enabled": "True",
          "LockedOut": "False",
          "PasswordNeverExpires": "False",
          "PasswordLastSet": "01/11/2025 10:30:00",
          "AccountExpirationDate": "",
          "IsExpired": "False"
        }
      ]
    }
  ]
}
```

## Architecture

### Composants principaux

1. **classe.py** : Classe `ssh` pour gérer les connexions SSH via Paramiko
2. **index.py** : Classe `commande` avec méthodes statiques pour interroger AD
3. **multi_export.py** : Orchestrateur principal avec architecture en couches :
   - `ReportConfig` : Configuration des rapports
   - `CLIArgumentParser` : Gestion des arguments CLI
   - `ADReportCollector` : Collecte des données via SSH
   - `JSONDocumentBuilder` : Construction et sauvegarde JSON
   - `ADReportExporter` : Orchestrateur principal

### Flux d'exécution

```
CLI Arguments → Parser → Collector (SSH + PowerShell) → Builder → JSON Output
```

## Sécurité

### Avertissements importants

- Les identifiants sont actuellement codés en dur dans certains fichiers (pour développement/test uniquement)
- Ne commitez JAMAIS des identifiants réels dans le code
- Utilisez des variables d'environnement ou un gestionnaire de secrets pour la production
- Assurez-vous que les connexions SSH sont sécurisées et chiffrées
- Limitez les droits d'accès aux rapports générés (peuvent contenir des informations sensibles)

### Bonnes pratiques recommandées

```python
import os

hostname = os.getenv('AD_HOST')
username = os.getenv('AD_USERNAME')
password = os.getenv('AD_PASSWORD')
```

## Configuration

Pour adapter le script à votre environnement, modifiez les constantes dans `multi_export.py` :

```python
DEFAULT_HOST = "votre-serveur.domain.local"
DEFAULT_USERNAME = "votre-compte-admin"
DEFAULT_PASSWORD = "utiliser-variable-environnement"
DEFAULT_OUTPUT_PATH = Path("./rapports")
```

## Tests

Pour exécuter les tests :

```bash
python -m pytest tests/
```

## Exemples d'utilisation avancée

### Script automatisé d'audit quotidien

```python
from pathlib import Path
from multi_export import ADReportExporter
from datetime import datetime

# Créer un rapport daté
date_str = datetime.now().strftime("%Y%m%d")
output_path = Path("./rapports") / date_str

exporter = ADReportExporter(
    host="dc01.domain.local",
    username="audit_account",
    password="secure_password",
    output_path=output_path
)
exporter.run()
```

### Intégration avec monitoring

Le format JSON structuré permet une intégration facile avec des systèmes de monitoring et d'analyse :
- Elasticsearch pour l'indexation
- Grafana pour la visualisation
- SIEM pour l'analyse de sécurité

## Dépannage

### Erreur de connexion SSH

```
Vérifiez que :
- Le port SSH (22) est ouvert sur le DC
- Les identifiants sont corrects
- Le compte a les droits nécessaires
```

### Erreur PowerShell "Module ActiveDirectory not found"

```powershell
# Sur le serveur Windows, installez le module :
Install-WindowsFeature -Name RSAT-AD-PowerShell
```

### Timeout lors de l'exécution

Pour les grands domaines, augmentez le timeout SSH dans `classe.py`.

## Contribution

Les contributions sont les bienvenues ! Merci de :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pousser vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Roadmap

- [ ] Support de l'authentification par clé SSH
- [ ] Export au format Excel
- [ ] Interface web pour visualisation des rapports
- [ ] Mode daemon pour collecte continue
- [ ] Support multi-domaines
- [ ] Détection d'anomalies de sécurité
- [ ] Alertes par email

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## Auteurs

Projet maintenu par l'équipe de développement.

## Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Contactez l'équipe de support

---

**Note** : Cet outil est destiné à des fins d'audit et d'administration légitimes. Utilisez-le de manière responsable et conformément aux politiques de sécurité de votre organisation.
