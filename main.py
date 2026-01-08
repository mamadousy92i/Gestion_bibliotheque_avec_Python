import sys
import os
import re
import csv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Bibliothéque.bibliotheque import Bibliotheque
from Bibliothéque.livre import Livre
from Bibliothéque.etudiant import Etudiant
from Bibliothéque.enseignant import Enseignant
from Bibliothéque.admin import PersonnelAdministratif

STATUTS = ["disponible", "emprunté", "réservé", "perdu", "endommagé"]

def afficher_menu_principal():
    # Un petit menu pour s'orienter dans la bibliothèque
    print("\n" + "="*40)
    print("   GESTION DE BIBLIOTHÈQUE - MENU PRINCIPAL")
    print("="*40)
    print("1. Gestion des Livres")
    print("2. Gestion des Utilisateurs")
    print("3. Gestion des Emprunts et Retours")
    print("4. Rapports et Statistiques")
    print("5. Quitter (À bientôt !)")
    print("="*40)

def afficher_menu_livres():
    print("\n--- GESTION DES LIVRES ---")
    print("1. Ajouter un livre")
    print("2. Ajouter un exemplaire")
    print("3. Modifier un livre")
    print("4. Supprimer un livre")
    print("5. Rechercher un livre")
    print("6. Retour au menu principal")

def afficher_menu_utilisateurs():
    print("\n--- GESTION DES UTILISATEURS ---")
    print("1. Ajouter un étudiant")
    print("2. Ajouter un enseignant")
    print("3. Ajouter un personnel administratif")
    print("4. Modifier un utilisateur")
    print("5. Supprimer un utilisateur")
    print("6. Rechercher un utilisateur")
    print("7. Lister tous les utilisateurs")
    print("8. Retour au menu principal")

def afficher_menu_emprunts():
    print("\n--- GESTION DES EMPRUNTS & RETOURS ---")
    print("1. Emprunter un livre")
    print("2. Retourner un livre")
    print("3. Renouveler un emprunt")
    print("4. Voir les emprunts en cours")
    print("5. Retour au menu principal")

def saisir_entree(message, obligatoire=True):
    while True:
        valeur = input(f"{message} (ou 'q' pour annuler) : ").strip()
        if valeur.lower() == 'q':
            return None
        if obligatoire and not valeur:
            print("Erreur : Ce champ est obligatoire.")
        else:
            return valeur

def prompt_email():
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    while True:
        email = input("Email (ou 'q' pour annuler) : ").strip()
        if email.lower() == 'q':
            return None
        if re.match(pattern, email):
            return email
        print("[ERREUR] Format d'email invalide.")
        print("Exemple : nom@domaine.com")
        if input("Réessayer ? (o/n) : ").lower() != 'o':
            return None

def selectionner_session(biblio):
    while True:
        # L'écran d'accueil, le point de départ
        print(f"\n=== BIENVENUE À LA {biblio.nom.upper()} ===")
        print("1. Se connecter (Déjà membre)")
        print("2. Créer un compte (Rejoignez-nous !)")
        print("3. Continuer en curieux (Invité)")
        print("4. Quitter l'application")
        choix = input("Votre choix : ")

        if choix == "1":
            id_utilisateur = saisir_entree("Entrez votre ID (ex: ADM-1, ETU-1)")
            if not id_utilisateur: continue
            user = biblio.utilisateur.get(id_utilisateur)
            if user:
                print(f"Bonjour {user.nom} !")
                return user.type_utilisateur, id_utilisateur
            else:
                print("[ERREUR] ID introuvable.")
        
        elif choix == "2":
            user = creer_compte_interactif(biblio)
            if user:
                print(f"Compte créé avec succès ! Votre ID est : {user.id_utilisateur}")
                return user.type_utilisateur, user.id_utilisateur
        
        elif choix == "3":
            return "INVITE", None
        
        elif choix == "4":
            return None, None
        else:
            print("Choix invalide.")

def creer_compte_interactif(biblio):
    print("\n--- INSCRIPTION ---")
    print("1. Étudiant")
    print("2. Enseignant")
    print("3. Retour")
    u_type = input("Choix : ")

    if u_type == "3": return None

    nom = saisir_entree("Nom complet")
    if not nom: return None
    email = prompt_email()
    if not email: return None

    if u_type == "1":
        niv = saisir_entree("Niveau d'étude")
        if not niv: return None
        fil = saisir_entree("Filière")
        if not fil: return None
        u = Etudiant(nom, email, niv, fil)
    elif u_type == "2":
        dep = saisir_entree("Département")
        if not dep: return None
        u = Enseignant(nom, email, dep)
    else:
        print("Type invalide.")
        return None

    biblio.ajouter_utilisateur(u)
    return u

def rechercher_livres_texte(biblio):
    """Recherche avancée pour interface texte."""
    while True:
        print("\n--- RECHERCHE AVANCÉE ---")
        print("1. Par mot-clé (Titre, Auteur, ISBN)")
        print("2. Par disponibilité (Statut)")
        print("3. Retour")
        choix = input("Votre choix : ")
        
        if choix == "3": break
        
        if choix == "1":
            term = saisir_entree("Terme de recherche")
            if not term: continue
            res = biblio.recherche_par_mot_clé(term)
            if res:
                for l in res:
                    tous = [e for e in biblio.exemplaires.values() if e.livre.isbn == l.isbn]
                    dispos = [e for e in tous if e.statut.value == "disponible"]
                    print(f"[{l.isbn}] {l.titre} - {l.auteur} | Dispo: {len(dispos)}/{len(tous)}")
            else: print("Aucun résultat.")
            input("Appuyez sur Entrée...")

        elif choix == "2":
            print("\nStatuts disponibles :")
            for i, st in enumerate(STATUTS, 1):
                print(f"{i}. {st}")
            
            try:
                idx = int(input("Choix du statut (N°) : ")) - 1
                if 0 <= idx < len(STATUTS):
                    statut_choisi = STATUTS[idx]
                    found = False
                    print(f"\n--- LIVRES AYANT DES EXEMPLAIRES '{statut_choisi.upper()}' ---")
                    for livre in biblio.catalogue.values():
                        # On cherche les exemplaires de ce livre qui ont ce statut
                        exs = [e for e in biblio.exemplaires.values() 
                              if e.livre.isbn == livre.isbn and e.statut.value == statut_choisi]
                        if exs:
                            print(f"[{livre.isbn}] {livre.titre} | {len(exs)} exemplaire(s)")
                            found = True
                    if not found: print(f"Aucun exemplaire trouvé avec le statut '{statut_choisi}'.")
                else: print("Choix invalide.")
            except ValueError: print("Saisie invalide.")
            input("Appuyez sur Entrée...")

def menu_recherche_simplifie(biblio):
    rechercher_livres_texte(biblio)

def menu_mes_emprunts(biblio, uid):
    while True:
        print(f"\n--- MES EMPRUNTS & RÉSERVATIONS ({uid}) ---")
        active = [e for e in biblio.emprunt_en_cour.values() if e.utilisateur.id_utilisateur == uid]
        if active:
            for e in active:
                print(f"- {e.exemplaire.livre.titre} (ID: {e.id_emprunt}) - Retour prévu : {e.date_retour_prevue}")
        else:
            print("Aucun emprunt en cours.")
            
        print("\n--- MES RÉSERVATIONS EN ATTENTE ---")
        found_res = False
        if uid in [u.id_utilisateur for u in biblio.utilisateur.values()]:     
            for isbn, reservations in biblio.reservations.items():
                for res in reservations:
                    if res.utilisateur.id_utilisateur == uid:
                        print(f"- [RÉSERVÉ] {res.livre.titre} (ISBN: {res.livre.isbn}) - Date : {res.date_reservation}")
                        found_res = True
        
        if not found_res:
            print("Aucune réservation en cours.")
        
        print("\n1. Réserver un livre")
        print("2. Retour")
        choix = input("Votre choix : ")
        if choix == "2": break
        if choix == "1":
            retour_accueil = lister_livres(biblio, show_exemplaires=True)
            if retour_accueil: break

def afficher_profil(biblio, uid):
    user = biblio.rechercher_utilisateur(uid)
    if not user: return
    print(f"\n--- MON PROFIL ({uid}) ---")
    print(f"Nom : {user.nom}")
    print(f"Email : {user.email}")
    print(f"Type : {user.type_utilisateur}")
    print(f"Total d'emprunts effectués : {user.nb_emprunts_total}")
    input("Appuyez sur Entrée...")

def lister_livres(biblio, show_exemplaires=False):
    print("\n--- CATALOGUE DES LIVRES ---")
    livres = list(biblio.catalogue.values())
    if not livres:
        print("Le catalogue est vide.")
        return False
    
    for livre in livres:
        # On calcule le nombre d'exemplaires disponibles pour ce livre
        tous = [e for e in biblio.exemplaires.values() if e.livre.isbn == livre.isbn]
        dispos = [e for e in tous if e.statut.value == "disponible"]
        
        # Formatage humain : [ISBN] Titre - Auteur (Annee)
        info = f"[{livre.isbn}] {livre.titre} - {livre.auteur} ({livre.anne_publication})"
        print(f"{info} | Dispo: {len(dispos)}/{len(tous)}")
    
    input("\nAppuyez sur Entrée...")
    return False

def effectuer_emprunt_flux(biblio, id_utilisateur=None):
    if not id_utilisateur:
        id_utilisateur = saisir_entree("ID utilisateur")
        if not id_utilisateur: return
        if id_utilisateur not in biblio.utilisateur:
            print("[ERREUR] Utilisateur introuvable.")
            return

    # Vérification des retards bloquants
    retards = [emp for emp in biblio.emprunt_en_cour.values() 
              if emp.utilisateur.id_utilisateur == id_utilisateur and emp.est_en_retard()]
    if retards:
        print(f"[BLOCAGE] Vous avez {len(retards)} livre(s) en retard. Vous devez les rendre avant de pouvoir emprunter à nouveau.")
        return

    isbn = saisir_entree("ISBN du livre à emprunter")
    if not isbn: return
    if isbn not in biblio.catalogue:
        print("[ERREUR] ISBN introuvable dans le catalogue.")
        return

    # On vérifie la disponibilité
    tous = [e for e in biblio.exemplaires.values() if e.livre.isbn == isbn]
    dispos = [e for e in tous if e.statut.value == "disponible"]

    if not dispos:
        print("\n[INFO] Aucun exemplaire disponible pour ce livre.")
        choix = input("Souhaitez-vous le réserver ? (o/n) : ").lower()
        if choix == 'o':
            print(biblio.effectuer_reservation(isbn, id_utilisateur))
        return

    # Si dispo, on liste et on fait choisir
    print("\nExemplaires disponibles :")
    for e in dispos:
        print(f"- {e.id_exemplaire}")
    
    id_ex = saisir_entree("Saisissez l'identifiant de l'exemplaire à emprunter")
    if not id_ex: return
    
    try:
        print(biblio.effectuer_emprunt(id_ex, id_utilisateur))
    except Exception as e:
        print(f"[ERREUR] {e}")

def main():
    biblio = Bibliotheque("Ma Bibliothèque Universitaire")
    
    while True:
        role, current_user_id = selectionner_session(biblio)
        if not role:
            print("Au revoir !")
            break
        
        while True:
            print(f"\n=== {biblio.nom.upper()} - MODE {role} ===")
            if role == "ADMIN":
                print("1. Lister les livres")
                print("2. Emprunter un livre")
                print("3. Retourner un livre")
                print("4. Gestion des Livres (Ajout/Modif/Supp)")
                print("5. Gestion des Utilisateurs")
                print("6. Statistiques & CSV")
                print("7. Déconnexion")
            elif role in ["ETUDIANT", "ENSEIGNANT", "USER"]:
                print("1. Lister les livres")
                print("2. Emprunter un livre")
                print("3. Rechercher un livre")
                print("4. Mes Emprunts & Réservations")
                print("5. Mon Profil")
                print("6. Déconnexion")
            else: # INVITE
                print("1. Lister les livres")
                print("2. Rechercher un livre")
                print("3. Déconnexion")

            choix = input("Votre choix : ")
            
            if role == "ADMIN":
                if choix == "1": lister_livres(biblio, show_exemplaires=True)
                elif choix == "2": effectuer_emprunt_flux(biblio, current_user_id)
                elif choix == "3":
                    id_emp = saisir_entree("ID Emprunt à retourner : ")
                    res = biblio.retourner_livre(id_emp)
                    print(res if res else "Livre retourné avec succès.")
                elif choix == "4": gestion_livres(biblio)
                elif choix == "5": gestion_utilisateurs(biblio)
                elif choix == "6": afficher_stats(biblio, role=role)
                elif choix == "7": break
            elif role in ["ETUDIANT", "ENSEIGNANT", "USER"]:
                if choix == "1": lister_livres(biblio)
                elif choix == "2": effectuer_emprunt_flux(biblio, current_user_id)
                elif choix == "3": menu_recherche_simplifie(biblio)
                elif choix == "4": menu_mes_emprunts(biblio, current_user_id)
                elif choix == "5": afficher_profil(biblio, current_user_id)
                elif choix == "6": break
            else:
                if choix == "1": lister_livres(biblio)
                elif choix == "2": menu_recherche_simplifie(biblio)
                elif choix == "3": break

def gestion_livres(biblio):
    while True:
        afficher_menu_livres()
        choix = input("Votre choix : ")
        if choix == "6": break
        
        if choix == "1":
            isbn = saisir_entree("ISBN")
            if not isbn: continue
            titre = saisir_entree("Titre")
            if not titre: continue
            auteur = saisir_entree("Auteur")
            if not auteur: continue
            try:
                annee_saisie = saisir_entree("Année de publication")
                if not annee_saisie: continue
                annee = int(annee_saisie)
            except ValueError:
                print("[ERREUR] Année invalide.")
                continue
            categorie = saisir_entree("Catégorie")
            if not categorie: continue
            livre = Livre(isbn, titre, auteur, annee, categorie)
            print(biblio.ajouter_au_catalogue(livre))
            
            reponse_ex = input("Ajouter des exemplaires ? (o/n ou 'q' pour annuler) : ").lower()
            if reponse_ex == 'o':
                try:
                    quantite_saisie = input("Combien ? : ").strip()
                    if quantite_saisie.lower() == 'q': continue
                    quantite = int(quantite_saisie)
                    for _ in range(quantite): print(biblio.ajouter_exemplaire(isbn))
                except ValueError: print(biblio.ajouter_exemplaire(isbn))
                
        elif choix == "2":
            isbn = saisir_entree("ISBN du livre")
            if not isbn: continue
            try:
                quantite_saisie = input("Combien ? (ou 'q' pour annuler) : ").strip()
                if quantite_saisie.lower() == 'q': continue
                quantite = int(quantite_saisie)
                for _ in range(quantite): print(biblio.ajouter_exemplaire(isbn))
            except ValueError: print(biblio.ajouter_exemplaire(isbn))

        elif choix == "3":
            isbn = saisir_entree("ISBN du livre à modifier")
            if not isbn: continue
            if isbn not in biblio.catalogue:
                print("[ERREUR] ISBN introuvable.")
                continue
            print("Laissez vide pour ne pas modifier. Tapez 'q' pour annuler.")
            titre = input("Nouveau Titre : ").strip()
            if titre.lower() == 'q': continue
            auteur = input("Nouvel Auteur : ").strip()
            if auteur.lower() == 'q': continue
            categorie = input("Nouvelle Catégorie : ").strip()
            if categorie.lower() == 'q': continue
            annee = input("Nouvelle Année : ").strip()
            if annee.lower() == 'q': continue
            
            parametres = {}
            if titre: parametres["titre"] = titre
            if auteur: parametres["auteur"] = auteur
            if categorie: parametres["categorie"] = categorie
            if annee:
                try: parametres["anne_publication"] = int(annee)
                except ValueError: pass
            print(biblio.modifier_livre(isbn, **parametres))

        elif choix == "4":
            isbn = saisir_entree("ISBN à supprimer")
            if not isbn: continue
            if input(f"Confirmer la suppression de {isbn} ? (o/n) : ").lower() == 'o':
                print(biblio.supprimer_livre(isbn))

        elif choix == "5":
            rechercher_livres_texte(biblio)


def gestion_utilisateurs(biblio):
    while True:
        afficher_menu_utilisateurs()
        choix = input("Votre choix : ")
        if choix == "8": break

        if choix in ["1", "2", "3"]:
            nom = saisir_entree("Nom complet : ")
            email = prompt_email()
            if not email: continue
            if choix == "1":
                niv = saisir_entree("Niveau : ")
                fil = saisir_entree("Filière : ")
                u = Etudiant(nom, email, niv, fil)
            elif choix == "2":
                dep = saisir_entree("Département : ")
                u = Enseignant(nom, email, dep)
            else:
                ser = saisir_entree("Service : ")
                u = PersonnelAdministratif(nom, email, ser)
            biblio.ajouter_utilisateur(u)
            print(f"Utilisateur ajouté. ID: {u.id_utilisateur}")

        elif choix == "4":
            id_utilisateur = saisir_entree("ID Utilisateur à modifier")
            if not id_utilisateur: continue
            if id_utilisateur not in biblio.utilisateur:
                print("[ERREUR] Utilisateur introuvable.")
                continue
            print("Laissez vide pour ne pas modifier. Tapez 'q' pour annuler.")
            nom = input("Nouveau Nom : ").strip()
            if nom.lower() == 'q': continue
            email = input("Nouvel Email : ").strip()
            if email.lower() == 'q': continue
            parametres = {}
            if nom: parametres["nom"] = nom
            if email: parametres["email"] = email
            print(biblio.modifier_utilisateur(id_utilisateur, **parametres))

        elif choix == "5":
            id_utilisateur = saisir_entree("ID Utilisateur à supprimer")
            if not id_utilisateur: continue
            if input(f"Confirmer suppression de {id_utilisateur} ? (o/n) : ").lower() == 'o':
                print(biblio.supprimer_utilisateur(id_utilisateur))

        elif choix == "6":
            mot_clé = saisir_entree("Nom, Email ou ID à rechercher")
            if not mot_clé: continue
            resultats = biblio.recherche_utilisateurs_par_mot_clé(mot_clé)
            if resultats:
                print(f"\n--- RÉSULTATS DE RECHERCHE ({len(resultats)}) ---")
                for u in resultats:
                    print(f"- {u.nom} (ID: {u.id_utilisateur}) [{u.type_utilisateur}]")
            else:
                print("Aucun utilisateur trouvé.")
            input("\nAppuyez sur Entrée...")

        elif choix == "7":
            print("\n--- LISTE COMPLÈTE DES UTILISATEURS ---")
            for u in biblio.utilisateur.values():
                print(f"- {u.nom} (ID: {u.id_utilisateur}) [{u.type_utilisateur}]")
            input("\nAppuyez sur Entrée...")

def gestion_emprunts(biblio):
    while True:
        afficher_menu_emprunts()
        choix = input("Votre choix : ")
        if choix == "6": break

        elif choix == "1":
            effectuer_emprunt_flux(biblio)

        elif choix == "2":
            id_emprunt = saisir_entree("ID Emprunt")
            if not id_emprunt: continue
            # Calcul de la pénalité potentielle avant retour pour affichage
            emprunt = biblio.emprunt_en_cour.get(id_emprunt)
            if emprunt and emprunt.est_en_retard():
                penalite = emprunt._calculer_penalité()
                print(f"[ATTENTION] Ce livre est en retard. Pénalité estimée : {penalite} unités.")
            
            resultat = biblio.retourner_livre(id_emprunt)
            print(resultat if resultat else "Livre retourné avec succès.")

        elif choix == "3":
            id_emprunt = saisir_entree("ID Emprunt à renouveler")
            if not id_emprunt: continue
            print(biblio.renouveler_livre(id_emprunt))

        elif choix == "4":
            if not biblio.emprunt_en_cour: print("Aucun emprunt en cours.")
            for id_emprunt, emprunt in biblio.emprunt_en_cour.items():
                print(f"- {id_emprunt} : {emprunt.exemplaire.livre.titre} par {emprunt.utilisateur.nom} (Retour le {emprunt.date_retour_prevue})")

def afficher_stats(biblio, role="INVITE"):
    print("\n=== RAPPORT STATISTIQUE ===")
    stats = biblio.generer_rapport_statistique()
    
    # Répartition par statut
    repartition = {s: 0 for s in STATUTS}
    for e in biblio.exemplaires.values():
        st = e.statut.value
        if st in repartition: repartition[st] += 1

    print("• Nombre total des livres par Statut :")
    for st in STATUTS: print(f"   - {st} : {repartition[st]}")

    print(f"\n• Nombre de livres empruntés, réservés, perdus ou endommagés :")
    for st in ["emprunté", "réservé", "perdu", "endommagé"]:
        print(f"   - {st} : {repartition[st]}")

    print("\n• Top 5 des livres les plus empruntés :")
    for l in stats['top_5_livres']: print(f"   - {l.titre} ({l.nb_emprunts_total} emprunts)")

    print("\n• Top 5 des utilisateurs les plus actifs :")
    for u in stats['top_5_users']: print(f"   - {u.nom} ({u.nb_emprunts_total} emprunts)")

    total_emp = sum(u.nb_emprunts_total for u in biblio.utilisateur.values())
    print(f"\n• Nombre total d’emprunts effectués : {total_emp}")

    print("\n• Liste des livres jamais empruntés :")
    for l in stats['livres_jamais_empruntes'][:10]: print(f"   - {l.titre} ({l.isbn})")

    if role == "ADMIN":
        if input("\nExporter ces statistiques en CSV ? (o/n) : ").lower() == 'o':
            print(biblio.exporter_statistiques_csv())
    
    input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
