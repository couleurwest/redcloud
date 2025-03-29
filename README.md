# Redcloud

## 🚀 Présentation
**Redcloud** est une application desktop permettant de synchroniser facilement **Redmine** et **Nextcloud Deck**, en transformant les tickets en tableaux kanban.

### 🎯 Fonctionnalités principales
- 📌 **Création automatique des Decks** dans Nextcloud à partir des projets Redmine.
- 🏷️ **Attribution d'étiquettes** basée sur les trackers Redmine.
- 📊 **Colonnes dynamiques** représentant les statuts du projet.
- 🔄 **Ajout des éléments** sans modification des existants.
- ⚙️ **Configuration propre à chaque utilisateur** et chiffrée.

## 🛠️ Installation
### Prérequis
- Un serveur **Redmine** avec l'API activée.
- Un serveur **Nextcloud** avec l’application **Deck** installée.
- **Python 3** et les dépendances nécessaires.

### 🔧 Configuration
1. **Clonez le dépôt** :
   ```sh
   git clone https://github.com/votre-utilisateur/redcloud.git
   cd redcloud_app
   ```
2. **Installez les dépendances** :
   ```sh
   pip install -r requirements.txt
   ```
3. **Lancez l'application** :
   ```sh
   python redcloud_app.py
   ```

## 📌 Usage
- **Création automatique** : un projet Redmine génère un Deck avec ses colonnes et étiquettes.
- **Ajout des tâches** : nouvelles tâches synchronisées entre Redmine et Deck.
- **Aucun suivi des modifications** : l'application ne gère pas les conflits, elle ajoute simplement les nouveaux éléments.

## 🔐 Sécurité & Authentification
- L'authentification repose uniquement sur **Redmine**.
- La configuration est **chiffrée** avec une clé basée sur le mot de passe utilisateur.

## 📝 Licence
Redcloud est distribué sous licence **Apache 2.0**. Consultez le fichier [`LICENSE`](./LICENSE) pour plus de détails.

## 🤝 Contribuer
Les contributions sont les bienvenues !
- **Forkez** le projet 🍴
- **Créez une branche** (`git checkout -b feature-amélioration`)
- **Proposez une Pull Request** ✅

## 📧 Contact
Pour toute question, ouvrez une issue ou contactez-moi à [email@example.com](mailto:email@example.com).

---
🚀 *Redcloud, synchronisez vos tickets Redmine avec Nextcloud Deck en toute simplicité !*

