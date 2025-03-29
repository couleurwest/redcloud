# RedCloud

## 🚀 Présentation
**RedCloud** est une passerelle entre **Redmine** et **Nextcloud Deck**, permettant une gestion centralisée des tickets sous forme de tableau kanban.

### 🎯 Fonctionnalités principales
- 📌 **Création automatique des Decks** dans Nextcloud à partir d'un projet Redmine.
- 🏷️ **Étiquettes des tâches** basées sur les trackers Redmine.
- 📊 **Colonnes dynamiques** représentant les statuts du projet.
- 🔄 **Mise à jour bidirectionnelle** entre Redmine et Deck :
  - Création et modification des tâches.
  - Mise à jour des statuts, dates et commentaires.
- ⚙️ **Sélection des statuts** (manuel ou récupération automatique depuis Redmine).

## 🛠️ Installation
### Prérequis
- Un serveur **Redmine** avec une API activée.
- Un serveur **Nextcloud** avec l’application **Deck** installée.
- Python 3 et les dépendances nécessaires.

### 🔧 Configuration
1. Clonez le dépôt :
   ```sh
   git clone https://github.com/votre-utilisateur/redcloud.git
   cd redcloud
   ```
2. Installez les dépendances :
   ```sh
   pip install -r requirements.txt
   ```
   
   ```sh
   python redcloud.py
   ```

## 📌 Usage
- **Création automatique** : Ajoutez un projet Redmine, un Deck sera généré avec ses colonnes et étiquettes.
- **Mise à jour des tâches** : Modifiez une carte dans Deck, elle sera mise à jour dans Redmine (et inversement).
- **Gestion des commentaires** : Ajoutez un commentaire sur une carte, il sera enregistré dans Redmine.

## 📝 Licence
RedCloud est distribué sous licence **Apache 2.0**. Consultez le fichier [`LICENSE`](./LICENSE) pour plus de détails.

## 🤝 Contribuer
Les contributions sont les bienvenues !
- **Forkez** le projet 🍴
- **Créez une branche** (`git checkout -b feature-amélioration`)
- **Proposez une Pull Request** ✅

## 📧 Contact
Pour toute question, ouvrez une issue ou contactez-moi à [email@example.com](mailto:email@example.com).

---

🚀 *RedCloud, simplifiez la gestion de vos tickets Redmine avec Nextcloud Deck !*
