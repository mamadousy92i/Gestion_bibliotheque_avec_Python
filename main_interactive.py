
import sys
import os
import re
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Bibliothéque.bibliotheque import Bibliotheque
from Bibliothéque.livre import Livre
from Bibliothéque.etudiant import Etudiant
from Bibliothéque.enseignant import Enseignant
from Bibliothéque.admin import PersonnelAdministratif


def effacer_ecran():
    os.system('cls' if os.name == 'nt' else 'clear')




STATUTS = ["disponible", "emprunté", "réservé", "perdu", "endommagé"]

def demander_email():
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$" # sa c'est le regex
    while True:
        email = inquirer.text(message="Email :", validate=EmptyInputValidator()).execute()
        if re.match(pattern, email):
            return email
        print("[ERREUR] Format d'email invalide. Exemple valide : nom.prenom@domaine.com")
        ressayer = inquirer.confirm(message="Voulez-vous ressaisir l'email ?", default=True).execute()
        if not ressayer:
            return None

def obtenir_utilisateur_id(biblio, id_utilisateur):
    return biblio.utilisateur.get(id_utilisateur)

def obtenir_livre_isbn(biblio, isbn):
    return biblio.catalogue.get(isbn)

def lister_exemplaire_isbn(biblio, isbn, filtre_statut=None):
    exs = [e for e in biblio.exemplaires.values() if e.livre.isbn == isbn]
    if filtre_statut:
        exs = [e for e in exs if e.statut.value == filtre_statut]
    return exs

def demander_isbn_ou_selectionner(biblio, message="Sélectionner un livre ou saisir l'ISBN :"):
    livres = list(biblio.catalogue.values())
    if not livres:
        print("Aucun livre dans le catalogue.")
        return None
    action = inquirer.select(
        message=message,
        choices=[
            Choice("saisir", "✏️ Saisir l'ISBN manuellement"),
            Choice("choisir", "📚 Choisir le livre dans la liste"),
            Choice("retour", "↩️ Retour"),
        ],
        default="choisir",
    ).execute()
    if action == "retour":
        return None
    if action == "saisir":
        isbn = inquirer.text(message="ISBN du livre :", validate=EmptyInputValidator()).execute()
        if obtenir_livre_isbn(biblio, isbn):
            return isbn
        print("[ERREUR] ISBN introuvable dans le catalogue.")
        return None
    else:
        isbn = inquirer.select(
            message="Livre :",
            choices=[Choice(l.isbn, f"{l.titre} ({l.isbn})") for l in livres] + [Choice("retour", "↩️ Retour")]
        ).execute()
        if isbn == "retour":
            return None
        return isbn

def demander_quantite(message="Combien d'exemplaires voulez-vous ajouter ?", valeur_defaut=1):
    action = inquirer.select(
        message="Souhaitez-vous préciser le nombre ?",
        choices=[
            Choice("fixer", "🧮 Saisir un nombre"),
            Choice("retour", "↩️ Retour"),
        ],
        default="fixer",
    ).execute()
    if action == "retour":
        return None
    quantite = inquirer.number(message=message, min_allowed=1).execute()
    try:
        return int(quantite)
    except Exception:
        return 1

def iterer_reservations(biblio):
    for nom in ["reservations_en_cours", "reservations", "liste_reservations", "reservations_actives"]:
        objet = getattr(biblio, nom, None)
        if objet:
            if isinstance(objet, dict):
                return list(objet.items())
            elif isinstance(objet, list):
                out = []
                for i, r in enumerate(objet, start=1):
                    id_res = getattr(r, "id_reservation", str(i))
                    out.append((id_res, r))
                return out
    return []


# ----------------------------- Main -----------------------------

# ----------------------------- Système de Session -----------------------------

def selectionner_session(biblio):
    """Petit écran d'accueil pour commencer l'aventure !"""
    while True:
        effacer_ecran()
        print(f"=== BIENVENUE À LA {biblio.nom.upper()} ===")
        choix = inquirer.select(
            message="On fait quoi aujourd'hui ?",
            choices=[
                Choice("connexion", "🔑 Se connecter (Déjà membre)"),
                Choice("inscription", "📝 Créer un compte (Bienvenue !)"),
                Choice("invite", "👤 Continuer en curieux (Invité)"),
                Choice("quitter", "🚪 Quitter (À la prochaine !)"),
            ],
            default="connexion"
        ).execute()

        if choix == "connexion":
            id_utilisateur = inquirer.text(message="Entrez votre ID (ex: ADM-1, ETU-1) :", validate=EmptyInputValidator()).execute()
            utilisateur = obtenir_utilisateur_id(biblio, id_utilisateur)
            if utilisateur:
                print(f"Bonjour {utilisateur.nom} !")
                input("\nAppuyez sur Entrée pour accéder au menu...")
                return utilisateur.type_utilisateur, id_utilisateur
            else:
                print("[ERREUR] ID introuvable.")
                input("\nAppuyez sur Entrée pour recommencer...")

        elif choix == "inscription":
            utilisateur = creer_compte_interactif(biblio)
            if utilisateur:
                print(f"Compte créé avec succès ! Votre ID est : {utilisateur.id_utilisateur}")
                input("\nNotez bien votre ID et appuyez sur Entrée...")
                return utilisateur.type_utilisateur, utilisateur.id_utilisateur
            else:
                input("\nInscription annulée. Appuyez sur Entrée...")

        elif choix == "invite":
            return "INVITE", None

        elif choix == "quitter":
            return None, None

def creer_compte_interactif(biblio):
    """Petit formulaire pour rejoindre le club."""
    effacer_ecran()
    print("--- INSCRIPTION ---")
    type_u = inquirer.select(
        message="Vous êtes plutôt... ?",
        choices=[
            Choice("etudiant", "🎓 Étudient studieux"),
            Choice("enseignant", "👨‍🏫 Enseignant passionné"),
            Choice("retour", "↩️ Oups, retour !"),
        ]
    ).execute()

    if type_u == "retour":
        return None

    nom = inquirer.text(message="Nom complet :", validate=EmptyInputValidator()).execute()
    email = demander_email()
    if not email:
        return None

    if type_u == "etudiant":
        niv = inquirer.text(message="Niveau d'étude :").execute()
        fil = inquirer.text(message="Filière :").execute()
        u = Etudiant(nom, email, niv, fil)
    else:
        dep = inquirer.text(message="Département :").execute()
        u = Enseignant(nom, email, dep)

    biblio.ajouter_utilisateur(u)
    return u

# ----------------------------- Main -----------------------------

def main():
    biblio = Bibliotheque("Ma Bibliothèque Universitaire")
    
    while True:
        role, current_user_id = selectionner_session(biblio)
        if not role:
            print("Au revoir !")
            break
        
        while True:
            effacer_ecran()
            print(f"=== {biblio.nom.upper()} - {role} ===")
            
            # Options adaptées au rôle
            options = []
            if role == "ADMIN":
                options = [
                    Choice("liste", "🗂️ Lister les livres"),
                    Choice("emprunt", "🤝 Emprunter un livre"),
                    Choice("gestion_livres", "📚 Gestion des Livres"),
                    Choice("gestion_utilisateurs", "👥 Gestion des Utilisateurs"),
                    Choice("suivi_emprunts", "📂 Suivi des Emprunts"),
                    Choice("stats", "📊 Statistiques & CSV"),
                ]
            elif role in ["ETUDIANT", "ENSEIGNANT", "USER"]:
                options = [
                    Choice("liste", "🗂️ Lister les livres"),
                    Choice("emprunt", "🤝 Emprunter un livre"),
                    Choice("recherche", "🔍 Rechercher un livre"),
                    Choice("mes_emprunts", "📖 Mes Emprunts en cours"),
                    Choice("profil", "👤 Mon Profil"),
                ]
            else: # INVITE
                options = [
                    Choice("liste", "🗂️ Lister les livres"),
                    Choice("recherche", "🔍 Rechercher un livre"),
                ]
            
            options.append(Choice("deconnexion", "🚪 Déconnexion"))
            
            choix = inquirer.select(
                message="Menu Principal :",
                choices=options,
            ).execute()

            if choix == "deconnexion":
                break
            
            # Navigation
            if choix == "liste":
                lister_livres_interactif(biblio)
            elif choix == "emprunt":
                effectuer_emprunt_interactif(biblio, current_user_id)
            elif choix == "gestion_livres":
                gestion_livres(biblio)
            elif choix == "gestion_utilisateurs":
                gestion_utilisateurs(biblio)
            elif choix == "suivi_emprunts":
                gestion_emprunts(biblio)
            elif choix == "stats":
                afficher_stats(biblio, role=role)
            elif choix == "recherche":
                menu_recherche_simplifie(biblio)
            elif choix == "mes_emprunts":
                menu_mes_emprunts(biblio, current_user_id)
            elif choix == "profil":
                afficher_profil(biblio, current_user_id)

def menu_recherche_simplifie(biblio):
    while True:
        effacer_ecran()
        choix = inquirer.select(
            message="Recherche & Consultation :",
            choices=[
                Choice("rechercher", "🔍 Rechercher un livre"),
                Choice("retour", "↩️ Retour"),
            ]
        ).execute()
        if choix == "retour": break
        if choix == "rechercher":
            terme = inquirer.text(message="Terme de recherche :").execute()
            resultats = biblio.recherche_par_mot_clé(terme)
            if resultats:
                for livre in resultats:
                    tous = [e for e in biblio.exemplaires.values() if e.livre.isbn == livre.isbn]
                    dispos = [e for e in tous if e.statut.value == "disponible"]
                    print(f"[{livre.isbn}] {livre.titre} - {livre.auteur} | Dispo: {len(dispos)}/{len(tous)}")
            else: print("Aucun résultat.")
            input("\nAppuyez sur Entrée...")

def menu_mes_emprunts(biblio, uid):
    while True:
        effacer_ecran()
        print(f"--- MES EMPRUNTS & RÉSERVATIONS ({uid}) ---")
        user = biblio.rechercher_utilisateur(uid)
        
        # Affichage emprunts
        active = [e for e in biblio.emprunt_en_cour.values() if e.utilisateur.id_utilisateur == uid]
        if active:
            for e in active:
                print(f"📖 {e.exemplaire.livre.titre} (ID: {e.id_emprunt}) - Retour prévu : {e.date_retour_prevue}")
        else:
            print("Aucun emprunt en cours.")
        
        print("-" * 20)
        choice = inquirer.select(
            message="Actions :",
            choices=[
                Choice("reserve", "🕒 Réserver un livre"),
                Choice("back", "↩️ Retour"),
            ]
        ).execute()
        
        if choice == "back": break
        if choice == "reserve":
            lister_livres_interactif(biblio)

def afficher_profil(biblio, id_utilisateur):
    effacer_ecran()
    utilisateur = biblio.rechercher_utilisateur(id_utilisateur)
    print(f"--- MON PROFIL ({id_utilisateur}) ---")
    print(f"Nom : {utilisateur.nom}")
    print(f"Email : {utilisateur.email}")
    print(f"Type : {utilisateur.type_utilisateur}")
    print(f"Total d'emprunts effectués : {utilisateur.nb_emprunts_total}")
    input("\nAppuyez sur Entrée...")

def lister_livres_interactif(biblio):
    effacer_ecran()
    print("--- CATALOGUE DES LIVRES ---")
    livres = list(biblio.catalogue.values())
    if not livres:
        print("Aucun livre dans la bibliothèque.")
        input("\nAppuyez sur Entrée...")
        return

    for livre in livres:
        tous = [e for e in biblio.exemplaires.values() if e.livre.isbn == livre.isbn]
        dispos = [e for e in tous if e.statut.value == "disponible"]
        print(f"[{livre.isbn}] {livre.titre} - {livre.auteur} ({livre.anne_publication}) | Dispo: {len(dispos)}/{len(tous)}")
    
    input("\nAppuyez sur Entrée...")

def effectuer_emprunt_interactif(biblio, id_utilisateur=None):
    effacer_ecran()
    if not id_utilisateur:
        id_utilisateur = inquirer.text(message="ID utilisateur :", validate=EmptyInputValidator()).execute()
        if not obtenir_utilisateur_id(biblio, id_utilisateur):
            print("[ERREUR] Utilisateur introuvable.")
            input("\nAppuyez sur Entrée...")
            return

    # Vérification des retards bloquants
    retards = [emp for emp in biblio.emprunt_en_cour.values() 
              if emp.utilisateur.id_utilisateur == id_utilisateur and emp.est_en_retard()]
    if retards:
        print(f"[BLOCAGE] Vous avez {len(retards)} livre(s) en retard. Vous devez les rendre avant de pouvoir emprunter à nouveau.")
        input("\nAppuyez sur Entrée...")
        return

    isbn = demander_isbn_ou_selectionner(biblio, message="Emprunter - choisir le livre :")
    if not isbn:
        return

    disponibles = lister_exemplaire_isbn(biblio, isbn, filtre_statut="disponible")
    
    if not disponibles:
        print("\n[INFO] Tous les exemplaires de ce livre sont actuellement indisponibles.")
        reserver = inquirer.confirm(message="Souhaitez-vous le réserver ?", default=True).execute()
        if reserver:
            print(biblio.effectuer_reservation(isbn, id_utilisateur))
        input("\nAppuyez sur Entrée...")
        return

    id_ex = inquirer.select(
        message="Sélectionnez l'exemplaire :",
        choices=[Choice(e.id_exemplaire, f"{e.id_exemplaire}") for e in disponibles] + [Choice("retour", "↩️ Retour")]
    ).execute()

    if id_ex == "retour":
        return

    try:
        print(biblio.effectuer_emprunt(id_ex, id_utilisateur))
    except Exception as e:
        print(f"[ERREUR] {e}")
    input("\nAppuyez sur Entrée...")



# ----------------------------- Livres -----------------------------

def gestion_livres(biblio):
    while True:
        effacer_ecran()
        choix = inquirer.select(
            message="--- GESTION DES LIVRES ---",
            choices=[
                Choice("ajouter", "➕ Ajouter un livre"),
                Choice("ajouter_ex", "📖 Ajouter des exemplaires"),
                Choice("modifier", "✏️ Modifier un livre"),
                Choice("supprimer", "🗑️ Supprimer un livre"),
                Choice("rechercher", "🔍 Rechercher un livre"),
                Choice("retour", "↩️ Retour au menu principal"),
            ],
        ).execute()

        if choix == "ajouter":
            isbn = inquirer.text(message="ISBN :", validate=EmptyInputValidator()).execute()
            titre = inquirer.text(message="Titre :", validate=EmptyInputValidator()).execute()
            auteur = inquirer.text(message="Auteur :", validate=EmptyInputValidator()).execute()
            annee = inquirer.number(message="Année de publication :", min_allowed=0, validate=EmptyInputValidator()).execute()
            categorie = inquirer.text(message="Catégorie :", validate=EmptyInputValidator()).execute()
            livre = Livre(isbn, titre, auteur, int(annee), categorie)
            print(biblio.ajouter_au_catalogue(livre))

            # Ajout d'exemplaires immédiatement (avec quantité)
            if inquirer.confirm(message="Souhaitez-vous ajouter des exemplaires de ce livre maintenant ?", default=True).execute():
                cnt = ask_count()
                if cnt is not None:
                    for _ in range(cnt):
                        print(biblio.ajouter_exemplaire(isbn))
                else:
                    print("↩️ Retour sans ajout d'exemplaires.")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "add_ex":
            isbn = ask_isbn_or_select(biblio, message="Ajouter des exemplaires :")
            if isbn is None:
                continue
            cnt = ask_count()
            if cnt is None:
                continue
            for _ in range(cnt):
                print(biblio.ajouter_exemplaire(isbn))
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "edit":
            act = inquirer.select(
                message="Modifier un livre :",
                choices=[
                    Choice("type", "✏️ Saisir l'ISBN"),
                    Choice("pick", "📚 Choisir dans la liste"),
                    Choice("back", "↩️ Retour"),
                ],
                default="pick",
            ).execute()
            if act == "back":
                continue

            if act == "type":
                isbn = inquirer.text(message="ISBN du livre à modifier :", validate=EmptyInputValidator()).execute()
                if not get_book_by_isbn(biblio, isbn):
                    print("[ERREUR] ISBN introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
            else:
                livres = list(biblio.catalogue.values())
                if not livres:
                    print("Catalogue vide.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                isbn = inquirer.select(
                    message="Livre à modifier :",
                    choices=[Choice(l.isbn, f"{l.titre} ({l.isbn})") for l in livres] + [Choice("back", "↩️ Retour")]
                ).execute()
                if isbn == "retour":
                    continue

            print("Chaque champ est optionnel (laissez vide si vous ne souhaitez pas modifier).")
            titre = inquirer.text(message="Nouveau Titre (laissez vide si vous ne souhaitez pas modifier) :").execute()
            auteur = inquirer.text(message="Nouvel Auteur (laissez vide si vous ne souhaitez pas modifier) :").execute()
            categorie = inquirer.text(message="Nouvelle Catégorie (laissez vide si vous ne souhaitez pas modifier) :").execute()
            annee = inquirer.text(message="Nouvelle Année (laissez vide si vous ne souhaitez pas modifier) :").execute()

            parametres = {}
            if titre: parametres["titre"] = titre
            if auteur: parametres["auteur"] = auteur
            if categorie: parametres["categorie"] = categorie
            if annee:
                try:
                    parametres["anne_publication"] = int(annee)
                except Exception:
                    pass
            print(biblio.modifier_livre(isbn, **parametres))
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "supprimer":
            action = inquirer.select(
                message="Supprimer un livre :",
                choices=[
                    Choice("saisir", "✏️ Saisir l'ISBN"),
                    Choice("choisir", "📚 Choisir dans la liste"),
                    Choice("retour", "↩️ Retour"),
                ],
                default="choisir",
            ).execute()
            if action == "retour":
                continue

            if action == "saisir":
                isbn = inquirer.text(message="ISBN du livre à supprimer :", validate=EmptyInputValidator()).execute()
                if not obtenir_livre_isbn(biblio, isbn):
                    print("[ERREUR] ISBN introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
            else:
                livres = list(biblio.catalogue.values())
                if not livres:
                    print("Catalogue vide.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                isbn = inquirer.select(
                    message="Livre à supprimer :",
                    choices=[Choice(l.isbn, f"{l.titre} ({l.isbn})") for l in livres] + [Choice("retour", "↩️ Retour")]
                ).execute()
                if isbn == "retour":
                    continue

            if inquirer.confirm(message=f"Confirmer la suppression de {isbn} ?", default=False).execute():
                print(biblio.supprimer_livre(isbn))
            else:
                print("Suppression annulée.")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "rechercher":
            mode_recherche = inquirer.select(
                message="Recherche :",
                choices=[
                    Choice("mc", "🔤 Par mot-clé (Titre, Auteur, ISBN)"),
                    Choice("statut", "📦 Par disponibilité (statut)"),
                    Choice("retour", "↩️ Retour"),
                ],
                default="mc",
            ).execute()
            if mode_recherche == "retour":
                continue

            if mode_recherche == "mc":
                terme = inquirer.text(message="Terme de recherche (Titre, Auteur, ISBN...) :").execute()
                resultats = biblio.recherche_par_mot_clé(terme)
                if resultats:
                    for livre in resultats:
                        tous = [e for e in biblio.exemplaires.values() if e.livre.isbn == livre.isbn]
                        dispos = [e for e in tous if e.statut.value == "disponible"]
                        print(f"[{livre.isbn}] {livre.titre} - {livre.auteur} | Dispo: {len(dispos)}/{len(tous)}")
                else:
                    print("Aucun résultat.")
            else:
                statut = inquirer.select(message="Choisir le statut :", choices=STATUTS + ["↩️ Retour"]).execute()
                if statut == "↩️ Retour":
                    continue
                correspondances = []
                for livre in biblio.catalogue.values():
                    exs = lister_exemplaire_isbn(biblio, livre.isbn, filtre_statut=statut)
                    if exs:
                        correspondances.append((livre, exs))
                if correspondances:
                    for livre, exs in correspondances:
                        print(f"[{livre.isbn}] {livre.titre} - {livre.auteur} | Exemplaires avec statut {statut} : {len(exs)}")
                else:
                    print("Aucun livre ne correspond à ce statut.")
            input("\nAppuyez sur Entrée pour continuer...")


        elif choix == "retour":
            break


# ----------------------------- Utilisateurs -----------------------------

def gestion_utilisateurs(biblio):
    while True:
        effacer_ecran()
        choix = inquirer.select(
            message="--- GESTION DES UTILISATEURS ---",
            choices=[
                Choice("ajout_etu", "🎓 Ajouter un étudiant"),
                Choice("ajout_ens", "👨‍🏫 Ajouter un enseignant"),
                Choice("ajout_adm", "🏢 Ajouter un admin"),
                Choice("modifier", "✏️ Modifier un utilisateur"),
                Choice("supprimer", "🗑️ Supprimer un utilisateur"),
                Choice("rechercher", "🔍 Rechercher un utilisateur"),
                Choice("liste", "🗂️ Lister tous les utilisateurs"),
                Choice("retour", "↩️ Retour au menu principal"),
            ],
        ).execute()

        if choix in ["ajout_etu", "ajout_ens", "ajout_adm"]:
            nom = inquirer.text(message="Nom complet :", validate=EmptyInputValidator()).execute()
            email = demander_email()
            if email is None:
                print("Opération annulée (email invalide).")
                input("\nAppuyez sur Entrée pour continuer...")
                continue

            if choix == "ajout_etu":
                niv = inquirer.text(message="Niveau :").execute()
                fil = inquirer.text(message="Filière :").execute()
                u = Etudiant(nom, email, niv, fil)
            elif choix == "ajout_ens":
                dep = inquirer.text(message="Département :").execute()
                u = Enseignant(nom, email, dep)
            else:
                ser = inquirer.text(message="Service :").execute()
                u = PersonnelAdministratif(nom, email, ser)

            biblio.ajouter_utilisateur(u)
            print(f"Utilisateur créé avec succès. ID: {u.id_utilisateur}")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "modifier":
            mode_modif = inquirer.select(
                message="Modifier utilisateur :",
                choices=[
                    Choice("saisir", "✏️ Saisir l'ID utilisateur"),
                    Choice("choisir", "👥 Choisir dans la liste"),
                    Choice("back", "↩️ Retour"),
                ],
                default="pick",
            ).execute()
            if mode_modif == "retour":
                continue

            if mode_modif == "saisir":
                id_utilisateur = inquirer.text(message="ID utilisateur :", validate=EmptyInputValidator()).execute()
                utilisateur = obtenir_utilisateur_id(biblio, id_utilisateur)
                if not utilisateur:
                    print("[ERREUR] Utilisateur introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
            else:
                utilisateurs = list(biblio.utilisateur.values())
                if not utilisateurs:
                    print("Aucun utilisateur.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                id_utilisateur = inquirer.select(
                    message="Utilisateur à modifier :",
                    choices=[Choice(u.id_utilisateur, f"{u.nom} ({u.id_utilisateur})") for u in utilisateurs] + [Choice("retour", "↩️ Retour")]
                ).execute()
                if id_utilisateur == "retour":
                    continue

            print("Champs optionnels (laissez vide si vous ne souhaitez pas modifier).")
            nom = inquirer.text(message="Nouveau Nom (laissez vide si vous ne souhaitez pas modifier) :").execute()
            email = inquirer.text(message="Nouvel Email (laissez vide si vous ne souhaitez pas modifier) :").execute()
            parametres = {}
            if nom: parametres["nom"] = nom
            if email:
                if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
                    parametres["email"] = email
                else:
                    print("[ERREUR] Nouvel email invalide : modification ignorée pour l'email.")
            print(biblio.modifier_utilisateur(id_utilisateur, **parametres))
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "supprimer":
            mode_suppr = inquirer.select(
                message="Supprimer utilisateur :",
                choices=[
                    Choice("saisir", "✏️ Saisir l'ID utilisateur"),
                    Choice("choisir", "👥 Choisir dans la liste"),
                    Choice("retour", "↩️ Retour"),
                ],
            ).execute()
            if mode_suppr == "retour":
                continue

            if mode_suppr == "saisir":
                id_utilisateur = inquirer.text(message="ID utilisateur :", validate=EmptyInputValidator()).execute()
                if not obtenir_utilisateur_id(biblio, id_utilisateur):
                    print("[ERREUR] Utilisateur introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
            else:
                utilisateurs = list(biblio.utilisateur.values())
                if not utilisateurs:
                    print("Aucun utilisateur.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                id_utilisateur = inquirer.select(
                    message="Utilisateur à supprimer :",
                    choices=[Choice(u.id_utilisateur, f"{u.nom} ({u.id_utilisateur})") for u in utilisateurs] + [Choice("retour", "↩️ Retour")]
                ).execute()
                if id_utilisateur == "retour":
                    continue

            if inquirer.confirm(message=f"Confirmer la suppression de {id_utilisateur} ?", default=False).execute():
                print(biblio.supprimer_utilisateur(id_utilisateur))
            else:
                print("Suppression annulée.")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "rechercher":
            mot_clé = inquirer.text(message="Nom, Email ou ID à rechercher :").execute()
            if not mot_clé:
                continue
            resultats = biblio.recherche_utilisateurs_par_mot_clé(mot_clé)
            if resultats:
                print(f"\n--- RÉSULTATS DE RECHERCHE ({len(resultats)}) ---")
                for utilisateur in resultats:
                    print(f"- {utilisateur.nom} (ID: {utilisateur.id_utilisateur}) [{utilisateur.type_utilisateur}]")
            else:
                print("Aucun utilisateur trouvé.")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "liste":
            print("\n--- LISTE COMPLÈTE DES UTILISATEURS ---")
            for utilisateur in biblio.utilisateur.values():
                print(f"- {utilisateur.nom} (ID: {utilisateur.id_utilisateur}) [{utilisateur.type_utilisateur}]")
            input("\nAppuyez sur Entrée pour revenir...")

        elif choix == "retour":
            break


# ----------------------------- Emprunts / Retours / Réservations -----------------------------

def gestion_emprunts(biblio):
    while True:
        effacer_ecran()
        choix = inquirer.select(
            message="--- EMPRUNTS ET RETOURS ---",
            choices=[
                Choice("emprunter", "🤝 Emprunter un livre"),
                Choice("retourner", "↩️ Retourner un livre"),
                Choice("renouveler", "🔁 Renouveler un emprunt"),
                Choice("en_cours", "👀 Voir les emprunts en cours"),
                Choice("retour", "↩️ Retour au menu principal"),
            ],
        ).execute()

        if choix == "emprunter":
            effectuer_emprunt_interactif(biblio)

        elif choix == "retourner":
            id_utilisateur = inquirer.text(message="ID utilisateur :", validate=EmptyInputValidator()).execute()
            utilisateur = obtenir_utilisateur_id(biblio, id_utilisateur)
            if not utilisateur:
                print("[ERREUR] Utilisateur introuvable.")
                input("\nAppuyez sur Entrée pour continuer...")
                continue

            emprunts_actifs = [
                (id_emp, emp) for id_emp, emp in biblio.emprunt_en_cour.items()
                if emp.utilisateur.id_utilisateur == id_utilisateur
            ]
            if not emprunts_actifs:
                print("Aucun emprunt en cours pour cet utilisateur.")
                input("\nAppuyez sur Entrée pour continuer...")
                continue

            mode_retour = inquirer.select(
                message="Retour : sélectionner l'emprunt",
                choices=[
                    Choice("choisir", "📄 Choisir dans la liste"),
                    Choice("saisir", "✏️ Saisir l'ID emprunt"),
                    Choice("retour", "↩️ Retour"),
                ],
            ).execute()
            if mode_retour == "retour":
                continue

            if mode_retour == "saisir":
                id_emprunt = inquirer.text(message="ID emprunt :", validate=EmptyInputValidator()).execute()
            else:
                id_emprunt = inquirer.select(
                    message="Emprunts en cours :",
                    choices=[
                        Choice(id_emp, f"{emp.exemplaire.livre.titre} -> {emp.utilisateur.nom} ({id_emp})")
                        for id_emp, emp in emprunts_actifs
                    ] + [Choice("retour", "↩️ Retour")],
                ).execute()
                if id_emprunt == "retour":
                    continue

            # Calcul de la pénalité potentielle avant retour pour affichage
            emprunt = biblio.emprunt_en_cour.get(id_emprunt)
            if emprunt and emprunt.est_en_retard():
                penalite = emprunt._calculer_penalité()
                print(f"[ATTENTION] Ce livre est en retard. Pénalité estimée : {penalite} unités.")

            resultat = biblio.retourner_livre(id_emprunt)
            print(resultat if resultat else "Livre retourné avec succès.")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "renouveler":
            id_utilisateur = inquirer.text(message="ID utilisateur :", validate=EmptyInputValidator()).execute()
            utilisateur = obtenir_utilisateur_id(biblio, id_utilisateur)
            if not utilisateur:
                print("[ERREUR] Utilisateur introuvable.")
                input("\nAppuyez sur Entrée pour continuer...")
                continue

            emprunts_actifs = [
                (id_emp, emp) for id_emp, emp in biblio.emprunt_en_cour.items()
                if emp.utilisateur.id_utilisateur == id_utilisateur
            ]
            if not emprunts_actifs:
                print("Aucun emprunt en cours pour cet utilisateur.")
                input("\nAppuyez sur Entrée pour continuer...")
                continue

            id_emprunt = inquirer.select(
                message="Emprunt à renouveler :",
                choices=[Choice(id_emp, f"{emp.exemplaire.livre.titre} ({id_emp})") for id_emp, emp in emprunts_actifs] + [Choice("retour", "↩️ Retour")]
            ).execute()
            if id_emprunt == "retour":
                continue

            print(biblio.renouveler_livre(id_emprunt))
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "reserve":
            uid = inquirer.text(message="ID utilisateur :", validate=EmptyInputValidator()).execute()
            user = get_user_by_id(biblio, uid)
            if not user:
                print("[ERREUR] Utilisateur introuvable.")
                input("\nAppuyez sur Entrée pour continuer...")
                continue

            isbn = ask_isbn_or_select(biblio, message="Réservation - choisir le livre :")
            if not isbn:
                continue

            exs = list_exemplaires_by_isbn(biblio, isbn)
            for e in exs:
                print(f" -> {e.id_exemplaire} [{e.statut.value}]")

            mode_res = inquirer.select(
                message="Réserver :",
                choices=[
                    Choice("by_book", "📚 Réserver par livre (ISBN)"),
                    Choice("by_copy", "📄 Réserver un exemplaire (si supporté)"),
                    Choice("back", "↩️ Retour"),
                ],
                default="by_book",
            ).execute()
            if mode_res == "back":
                continue

            if mode_res == "by_book":
                print(biblio.effectuer_reservation(isbn, uid))
            else:
                eid = inquirer.text(message="ID exemplaire à réserver :", validate=EmptyInputValidator()).execute()
                if hasattr(biblio, "effectuer_reservation_exemplaire"):
                    print(biblio.effectuer_reservation_exemplaire(eid, uid))
                else:
                    print("⚠️ Réservation par exemplaire non supportée dans le modèle actuel.")

            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "reservations":
            # Affiche les réservations en cours
            elements = iterer_reservations(biblio)
            if not elements:
                print("Aucune réservation en cours.")
            else:
                for id_res, res in elements:
                    # Tolérant : on récupère ce qu'on peut afficher
                    utilisateur = getattr(res, "utilisateur", getattr(res, "user", None))
                    livre = getattr(res, "livre", None)
                    isbn = getattr(res, "isbn", getattr(livre, "isbn", "-"))
                    titre = getattr(livre, "titre", getattr(res, "titre", "Inconnu"))
                    date_res = getattr(res, "date_reservation", getattr(res, "date", ""))
                    nom_utilisateur = getattr(utilisateur, "nom", getattr(res, "nom_utilisateur", "Inconnu"))
                    print(f"- {id_res} : {titre} ({isbn}) -> {nom_utilisateur} {f'[{date_res}]' if date_res else ''}")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "en_cours":
            if not biblio.emprunt_en_cour:
                print("Aucun emprunt en cours.")
            else:
                for id_emprunt, emprunt in biblio.emprunt_en_cour.items():
                    print(f"- {id_emprunt} : {emprunt.exemplaire.livre.titre} par {emprunt.utilisateur.nom} (Retour le {emprunt.date_retour_prevue})")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "retour":
            break


# ----------------------------- Statistiques -----------------------------

def afficher_stats(biblio, role="INVITE"):
    while True:
        effacer_ecran()
        print("=== RAPPORT STATISTIQUE ===")

        # On utilise votre méthode si elle existe, avec valeurs par défaut
        stats = {}
        try:
            stats = biblio.generer_rapport_statistique() or {}
        except Exception:
            stats = {}

        total_emprunts_effectues = stats.get("total_emprunts_effectues", 0)
        # Si total_emprunts_effectues est 0, on essaye de compter dans l'historique
        if total_emprunts_effectues == 0:
            total_emprunts_effectues = sum(user.nb_emprunts_total for user in biblio.utilisateur.values())

        # Répartition par statut
        repartition = {s: 0 for s in STATUTS}
        for e in biblio.exemplaires.values():
            st = e.statut.value
            if st in repartition:
                repartition[st] += 1

        # Top 5 livres / utilisateurs
        top_5_livres = stats.get("top_5_livres", [])
        top_5_users = stats.get("top_5_users", [])

        # Livres jamais empruntés
        livres_jamais_empruntes = stats.get("livres_jamais_empruntes", [])

        # Affichage
        print("• Nombre total des livres par Statut :")
        for st in STATUTS:
            print(f"   - {st} : {repartition[st]}")
        
        print(f"\n• Nombre de livres empruntés, réservés, perdus ou endommagés :")
        print(f"   - empruntés : {repartition['emprunté']}")
        print(f"   - réservés  : {repartition['réservé']}")
        print(f"   - perdus    : {repartition['perdu']}")
        print(f"   - endommagés: {repartition['endommagé']}")

        print("\n• Top 5 des livres les plus empruntés :")
        if top_5_livres:
            for l in top_5_livres:
                print(f"   - {l.titre} ({l.nb_emprunts_total} emprunts)")
        else: print("   - (aucune donnée)")

        print("\n• Top 5 des utilisateurs les plus actifs :")
        if top_5_users:
            for u in top_5_users:
                print(f"   - {u.nom} ({u.nb_emprunts_total} emprunts)")
        else: print("   - (aucune donnée)")

        print(f"\n• Nombre total d’emprunts effectués : {total_emprunts_effectues}")

        print("\n• Liste des livres jamais empruntés :")
        if livres_jamais_empruntes:
            for l in livres_jamais_empruntes[:10]: # Limité à 10 pour l'affichage
                print(f"   - {l.titre} ({l.isbn})")
        else: print("   - (aucune donnée)")

        print("\n" + "-"*30)
        
        # Options selon rôle
        choix_options = [Choice("retour", "↩️ Retour au menu principal")]
        if role == "ADMIN":
            choix_options.insert(0, Choice("csv", "📄 Exporter ces statistiques en CSV"))
        
        action = inquirer.select(
            message="Options :",
            choices=choix_options
        ).execute()

        if action == "csv":
            print(f"\n{biblio.exporter_statistiques_csv()}")
            input("\nAppuyez sur Entrée...")
        else:
            break


if __name__ == "__main__":
   


    main()
