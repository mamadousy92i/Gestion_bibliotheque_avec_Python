<div align="center">

# RAPPORT DE PROJET : DIGITALISATION DE LA BIBLIOTHÈQUE DU DIT

**Auteur :** GROUPE 5 (MAMADOU SY, JAPHET, JOSUÉ et REDIS TONI)  
**Classe :** Master 1 Intelligence Artificielle (M1 IA)  
**Date :** Janvier 2026  
**Institution :** Dakar Institute of Technology (DIT)

</div>

---

## SOMMAIRE
1. [PRÉSENTATION GÉNÉRALE DE LA SOLUTION](#1-présentation-générale-de-la-solution)
2. [ANALYSE DU PROBLÈME ET MODÉLISATION (POO)](#2-analyse-du-problème-et-modélisation-poo)
3. [DESCRIPTION DES CLASSES ET MÉTHODES PRINCIPALES](#3-description-des-classes-et-méthodes-principales)
4. [DESCRIPTION TECHNIQUE DES MODULES](#4-description-technique-des-modules)
5. [SAUVEGARDE ET JOURNALISATION](#5-sauvegarde-et-journalisation)
6. [WORKFLOWS DÉTAILLÉS DE L'APPLICATION](#6-workflows-détaillés-de-lapplication)
7. [CAPTURES D’ÉCRAN ET DÉMONSTRATION](#7-captures-décran-et-démonstration)
8. [CONCLUSION ET PERSPECTIVES](#8-conclusion-et-perspectives)

<div style="page-break-after: always;"></div>

## 1. PRÉSENTATION GÉNÉRALE DE LA SOLUTION

Dans un contexte académique en constante évolution, la gestion manuelle de la bibliothèque du Dakar Institute of Technology (DIT) présente de nombreuses limites : erreurs humaines, absence d’historique fiable, difficulté de suivi des emprunts et impossibilité de produire des statistiques exploitables.

Face à ces constats, ce projet vise à concevoir et implémenter une application numérique complète de gestion de bibliothèque, développée en Python, reposant sur les principes de la Programmation Orientée Objet (POO).

### La solution proposée permet :
- La gestion centralisée des livres et de leurs exemplaires
- La gestion différenciée des utilisateurs (étudiants, enseignants, administrateurs)
- L’automatisation des emprunts, retours et réservations
- La persistance des données via des fichiers JSON
- La traçabilité complète des actions (Audit logging)
- La génération de rapports statistiques exploitables et exportation CSV

L’application a été pensée de manière modulaire, évolutive et maintenable, afin de pouvoir être enrichie ultérieurement (interface graphique, base de données, application web).

<div style="page-break-after: always;"></div>

## 2. ANALYSE DU PROBLÈME ET MODÉLISATION (POO)

### 2.1 Analyse du problème
Le système de gestion de bibliothèque doit répondre à plusieurs contraintes métiers :
- Un livre peut exister en plusieurs exemplaires.
- Un utilisateur possède une limite d’emprunt selon son rôle.
- Un livre indisponible peut être réservé.
- Les retards doivent être détectés automatiquement.
- Les données doivent être conservées après fermeture du programme.

Ces exigences ont conduit à une modélisation orientée objet, permettant de représenter fidèlement le monde réel.

### 2.2 Principes de Programmation Orientée Objet appliqués

#### Encapsulation
Les attributs sensibles tels que l'ISBN, les identifiants utilisateurs, les statuts des livres et les dates sont définis comme attributs privés (`__attribut`) et manipulés via des accesseurs (`@property` / setter) afin de garantir l’intégrité des données.

#### Héritage
Une classe mère `Utilisateur` centralise les attributs communs. Elle est spécialisée en :
- **Étudiant**
- **Enseignant**
- **Admin** (Personnel Administratif)

Chaque sous-classe définit ses propres règles métiers, notamment la limite maximale d’emprunts.

#### Polymorphisme
Certaines méthodes, comme `to_dict()`, sont implémentées dans plusieurs classes afin d'uniformiser la sauvegarde des objets et faciliter la sérialisation en JSON.

<div style="page-break-after: always;"></div>

## 3. DESCRIPTION DES CLASSES ET MÉTHODES PRINCIPALES

### 3.1 Classe Bibliotheque (Cœur du système)
La classe `Bibliotheque` agit comme orchestrateur principal.
- **Attributs :** `catalogue`, `utilisateurs`, `exemplaires`, `emprunt_en_cour`, `reservations`.
- **Méthodes clés :** `ajouter_au_catalogue()`, `effectuer_emprunt()`, `retourner_livre()`, `sauvegarder_donnees()`, `charger_donnees()`.

### 3.2 Gestion des rôles et fonctionnalités

| Fonctionnalité | Invité | Étudiant / Enseignant | Administrateur |
| :--- | :---: | :---: | :---: |
| Lister/Rechercher des livres | ✅ | ✅ | ✅ |
| Voir son profil | ❌ | ✅ | ✅ |
| Emprunter/Réserver | ❌ | ✅ | ✅ |
| Gérer les ouvrages | ❌ | ❌ | ✅ |
| Gérer les utilisateurs | ❌ | ❌ | ✅ |
| Statistiques & Export CSV | ❌ | ❌ | ✅ |

### 3.3 Gestion des utilisateurs
- **Étudiant :** 3 emprunts max.
- **Enseignant :** 5 emprunts max.
- **Admin :** 7 emprunts max.
- **Identifiants :** ETU-x, ENS-x, ADM-x générés automatiquement.

<div style="page-break-after: always;"></div>

## 4. DESCRIPTION TECHNIQUE DES MODULES

### Gestion des livres et exemplaires
- **Classe Livre :** Métadonnées (ISBN, Titre, Auteur, Année).
- **Classe Exemplaire :** Gère l'état physique (Disponible, Emprunté, Réservé, Perdu, Endommagé).

### Emprunts et réservations
- **Emprunts :** Calcul automatique de la date de retour, détection des retards et calcul des pénalités (100u/jour).
- **Réservations :** File d'attente automatique et notification consignée dans `notifications_reservations.txt`.

<div style="page-break-after: always;"></div>

## 5. SAUVEGARDE ET JOURNALISATION

- **Persistance :** Sauvegarde automatique dans `data_bibliotheque.json`.
- **Journalisation :** Chaque action (emprunt, retour, etc.) est tracée dans `bibliotheque.log` avec horodatage.
- **Statistiques :** Rapports détaillés (Top 5 livres/utilisateurs) avec option d'export CSV pour les administrateurs.

<div style="page-break-after: always;"></div>

## 6. WORKFLOWS DÉTAILLÉS DE L'APPLICATION

### 6.1 Workflow d'Emprunt (Cas nominal)
Le système guide l'utilisateur à travers la sélection du livre et de l'exemplaire, tout en vérifiant les quotas de son rôle.

```text
=== MENU EMPRUNT ===
? Emprunter - choisir le livre : 📚 Choisir dans la liste
❯ [1002] Le Petit Prince - Antoine de Saint-Exupéry
? Sélectionnez l'exemplaire : EX001-3 (Disponible)

[SYSTÈME] Vérification du quota pour ETU-1...
[SYSTÈME] Quota actuel : 1/3. Autorisation accordée.

[SUCCÈS] Emprunt validé. 
Livre : Le Petit Prince
Retour prévu : 2026-01-19 (14 jours)
```

### 6.2 Workflow de Retour de Livre
Le retour libère l'exemplaire et met à jour l'historique de l'utilisateur.

```text
=== MENU GESTION DES EMPRUNTS ===
? Action : ↩️ Retourner un livre
? ID utilisateur : ETU-1
? Emprunts en cours : 
❯ Le Petit Prince (ID: EMP-5)

[SYSTÈME] Enregistrement du retour...
[SYSTÈME] Exemplaire EX001-3 remis en statut 'disponible'.

[SUCCÈS] Livre retourné avec succès. Merci !
```

### 6.3 Workflow de Pénalité (Gestion du Retard)
Si un livre est rendu après la date prévue, le système calcule automatiquement la pénalité basée sur 100 unités par jour de retard.

```text
=== MENU GESTION DES EMPRUNTS ===
? Action : ↩️ Retourner un livre
? ID utilisateur : ETU-2
? Emprunts en cours : 
❯ Germinal (ID: EMP-2) - [EN RETARD]

[ATTENTION] Ce livre est en retard de 3 jours.
[SYSTÈME] Calcul de la pénalité : 3 jours x 100u = 300u.

? Confirmer le retour avec pénalité ? (Oui/Non) : Oui

[SUCCÈS] Livre retourné. Pénalité de 300u enregistrée au compte de ETU-2.
⚠️ Note : L'utilisateur est bloqué tant que le livre en retard n'est pas rendu.
```

<div style="page-break-after: always;"></div>

## 7. CAPTURES D’ÉCRAN ET DÉMONSTRATION

### 7.1 Menu Principal de l'application
Le menu principal offre une navigation fluide et intuitive grâce à l'utilisation d'InquirerPy.

```text
=== MA BIBLIOTHÈQUE UNIVERSITAIRE - ADMIN ===
? Menu Principal :
 🗂️ Lister les livres
 🤝 Emprunter un livre
 📚 Gestion des Livres
 👥 Gestion des Utilisateurs
 📂 Suivi des Emprunts
 📊 Statistiques & CSV
 🚪 Déconnexion
```

### 7.2 Exemple d'emprunt réussi
Gestion intelligente des stocks et des dates de retour.

```text
? Emprunter - choisir le livre : 📚 Choisir le livre dans la liste
? Livre : Le Petit Prince (1002)
? Sélectionnez l'exemplaire : EX001-3
[SUCCÈS] Emprunt effectué avec succès.
ID Emprunt : EMP-5
Date de retour prévue : 2026-01-19
```

### 7.3 Recherche avancée
Possibilité de trouver un ouvrage par mot-clé (Saisie tolérante).

```text
? Recherche : 🔤 Par mot-clé (Titre, Auteur, ISBN)
? Terme de recherche (Titre, Auteur, ISBN...) : Camus
[RÉSULTATS] 
- [1001] L'Étranger - Albert Camus | Dispo: 1/1
```

### 7.4 Fichier de journalisation (Audit Log)
Tracé exhaustif de chaque action système dans `bibliotheque.log`.

```text
[2026-01-05 15:21:48] - EMPRUNT : L'utilisateur ETU-1 a pris l'exemplaire EX001-1
[2026-01-05 15:23:12] - RETOUR : Retour de l'emprunt ID: EMP-1
[2026-01-05 15:23:45] - STATISTIQUES : Export CSV généré avec succès.
```

### 7.5 Export des statistiques (CSV)
Visualisation du fichier `statistiques_bibliotheque_20260105.csv`.

| Indicateur | Valeur |
| :--- | :--- |
| Total Livres | 12 |
| Total Exemplaires | 45 |
| Top 1 | Le Petit Prince (8 emprunts) |
| Top 2 | L'Étranger (5 emprunts) |

<div style="page-break-after: always;"></div>

## 8. CONCLUSION ET PERSPECTIVES

Ce projet a permis de mettre en pratique les concepts avancés de la POO en Python, tout en répondant à un besoin réel de digitalisation. L’application développée est fonctionnelle, modulaire et conforme aux bonnes pratiques.

**DIT – Année académique 2025–2026**
