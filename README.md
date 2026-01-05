# Système de Gestion de Bibliothèque Universitaire

Ce projet est une application robuste de gestion de bibliothèque développée en Python. Il propose deux interfaces (standard et interactive) pour gérer efficacement les livres, les exemplaires, les utilisateurs et les transactions (emprunts/retours/réservations).

## 📋 Sommaire
1. [Prérequis](#prérequis)
2. [Structure du Projet](#structure-du-projet)
3. [Installation et Exécution](#installation-et-exécution)
4. [Fonctionnalités Principales](#fonctionnalités-principales)
5. [Gestion des Rôles](#gestion-des-rôles)
6. [Persistance et Audit](#persistance-et-audit)

---

## 🛠 Prérequis
- **Python 3.8+**
- **Bibliothèques Python :**
  - `InquirerPy` (uniquement pour la version interactive)
  - `csv`, `re`, `json`, `datetime`, `os`, `sys` (incluses dans la bibliothèque standard Python)

---

## 📂 Structure du Projet
Le projet est organisé de manière modulaire :

- `main.py` : Point d'entrée de l'interface en ligne de commande (CLI) standard.
- `main_interactive.py` : Point d'entrée de l'interface visuelle et interactive (recommandé).
- `bibliotheque.py` : Cœur du système orchestrant toutes les opérations (Logique métier).
- `livre.py` : Définition des ouvrages et des statuts (Disponible, Emprunté, etc.).
- `exemplaire.py` : Gestion des copies physiques individuelles des livres.
- `utilisateur.py` : Classe de base abstraite pour les membres.
- `etudiant.py`, `enseignant.py`, `admin.py` : Spécificités pour chaque type d'utilisateur.
- `emprunt.py` : Gestion du cycle de vie d'un prêt.
- `reservation.py` : Gestion des files d'attente.
- `data_bibliotheque.json` : Base de données au format JSON.
- `bibliotheque.log` : Journal d'audit des actions effectuées.
- `notifications_reservations.txt` : Registre des notifications envoyées.

---

## 🚀 Installation et Exécution

### 1. Installation
Clonez ou téléchargez le projet, puis installez la dépendance pour l'interface interactive :
```bash
pip install InquirerPy
```

### 2. Lancement
Vous avez le choix entre deux modes :

- **Mode Interactif (Conseillé)** : Navigation aux flèches, menus fluides.
  ```bash
  python3 main_interactive.py
  ```
- **Mode Standard** : Menus numérotés classiques.
  ```bash
  python3 main.py
  ```

### 3. Droits d'écriture (Linux/macOS)
Pour permettre l'exportation des statistiques CSV et la mise à jour des logs, assurez-vous que le dossier possède les droits d'écriture :
```bash
chmod u+w ~/Bibliothéque/
```

---

## ✨ Fonctionnalités Principales

### 🔐 Système de Session
- **Connexion** : Authentification par ID unique (ex: ADM-1, ETU-2).
- **Inscription** : Création de compte Étudiant ou Enseignant avec validation d'email (Regex).
- **Mode Invité** : Consultation rapide du catalogue sans compte.

### 📚 Gestion du Catalogue
- **Lister les livres** : Aperçu immédiat du catalogue depuis le menu principal.
- **Ajout/Suppression** : Gestion complète des références et des exemplaires physiques (Admins uniquement).
- **Recherche multicritère** : Trouvé par titre, auteur ou ISBN.

### 🤝 Prêts et Réservations
- **Emprunt Intelligent** : Le système vérifie automatiquement la disponibilité.
- **Réservation Automatique** : Si aucun exemplaire n'est disponible lors d'une tentative d'emprunt, le système vous propose instantanément de réserver l'ouvrage.
- **Retours et Renouvellements** : Gestion simplifiée des retours avec calcul de pénalités de retard.

### 📊 Statistiques et Export
- **Rapports détaillés** : Top 5 des livres empruntés, utilisateurs les plus actifs, livres jamais empruntés.
- **Export CSV** : Les administrateurs peuvent exporter l'intégralité des statistiques en un clic.

---

## 👥 Gestion des Rôles

| Fonctionnalité | Invité | Étudiant / Enseignant | Administrateur |
| :--- | :---: | :---: | :---: |
| Lister/Rechercher des livres | ✅ | ✅ | ✅ |
| Voir son profil | ❌ | ✅ | ✅ |
| Emprunter/Réserver | ❌ | ✅ | ✅ |
| Gérer les ouvrages | ❌ | ❌ | ✅ |
| Gérer les utilisateurs | ❌ | ❌ | ✅ |
| Statistiques & Export CSV | ❌ | ❌ | ✅ |

---

## 🛡 Persistance et Audit
Le système garantit l'intégrité de vos données :
- **Persistance** : Sauvegarde automatique dans `data_bibliotheque.json` après chaque modification.
- **Audit** : Chaque action (emprunt, inscription, etc.) est tracée dans `bibliotheque.log`.
- **Notifications** : Les alertes de disponibilité pour les réservations sont consignées dans `notifications_reservations.txt`.
