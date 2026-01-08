from Bibliothéque.livre import *
from datetime import datetime
from Bibliothéque.emprunt import *
from Bibliothéque.exemplaire import *
from Bibliothéque.reservation import *
from Bibliothéque.utilisateur import *
from Bibliothéque.etudiant import Etudiant
from Bibliothéque.enseignant import Enseignant
from Bibliothéque.admin import PersonnelAdministratif
        
import json
import os
import csv
class Bibliotheque:
    
    def __init__(self,nom):
        self.__nom=nom
        self.__exemplaires={}
        self.__catalogue={}
        self.__utilisateurs={}
        self.__emprunt_en_cour={}
        self.__reservations = {}
        self.charger_donnees()
    
    @property
    def nom(self):
        return self.__nom
    

    @property
    def exemplaires(self):
        return self.__exemplaires
    
    @property
    def utilisateur(self):
        return self.__utilisateurs
    
    @property
    def emprunt_en_cour(self):
        return self.__emprunt_en_cour
    
    @property
    def reservations(self):
        return self.__reservations
    
    @property
    def catalogue(self):
        return self.__catalogue
    
    
    

    def ajouter_au_catalogue(self,livre):
        if self.__catalogue.get(livre.isbn):
            return "ce livre existe deja dans le catalogue ajouter pluto un exemplaire"
        else:
            self.__catalogue[livre.isbn]=livre
            self.sauvegarder_donnees()
            self.enregistrer_action("catalogue", f"Ajout du livre {livre.titre} (ISBN: {livre.isbn})")
            return "ajouté au catalogue avec succes"
        
    
    def ajouter_exemplaire(self,isbn):
        livre_correspondant=self.__catalogue.get(isbn)
        
        if livre_correspondant:
            nouvel_ex=Exemplaire(livre_correspondant)
            self.__exemplaires[nouvel_ex.id_exemplaire]=nouvel_ex
            self.sauvegarder_donnees()
            self.enregistrer_action("exemplaire", f"Nouvel exemplaire créé : {nouvel_ex.id_exemplaire} pour le livre {livre_correspondant.titre}")

            return f"exemplaire du livre : {livre_correspondant.titre} ajouter avec succes"
        else:
            return "le livre n'existe pas"
        
        
    
    def ajouter_utilisateur(self,utilisateur):
        self.__utilisateurs[utilisateur.id_utilisateur] = utilisateur
        self.sauvegarder_donnees()
        self.enregistrer_action("utilisateur", f"Nouvel utilisateur inscrit : {utilisateur.nom} (ID: {utilisateur.id_utilisateur}, Type: {utilisateur.type_utilisateur})")

    def modifier_livre(self, isbn, **kwargs):
        livre = self.__catalogue.get(isbn)
        if not livre:
            return "Livre introuvable."
        
        modifications = []
        if "titre" in kwargs:
            modifications.append(f"titre: {livre.titre} -> {kwargs['titre']}")
            livre.titre = kwargs["titre"]
            
        if "auteur" in kwargs:
            modifications.append(f"auteur: {livre.auteur} -> {kwargs['auteur']}")
            livre.auteur = kwargs["auteur"]
            
        if "categorie" in kwargs:
            modifications.append(f"categorie: {livre.categorie} -> {kwargs['categorie']}")
            livre.categorie = kwargs["categorie"]
            
        if "anne_publication" in kwargs:
            modifications.append(f"année: {livre.anne_publication} -> {kwargs['anne_publication']}")
            livre.anne_publication = kwargs["anne_publication"]
            
        if modifications:
            self.sauvegarder_donnees()
            self.enregistrer_action("modification_livre", f"Livre {isbn} modifié : {', '.join(modifications)}")
            return "Livre modifié avec succès."
        return "Aucune modification effectuée."

    def supprimer_livre(self, isbn):
        if isbn not in self.__catalogue:
            return "Livre introuvable."
        
        # Vérifier s'il y a des exemplaires rattachés
        for exemplaire in self.__exemplaires.values():
            if exemplaire.livre.isbn == isbn:
                return "Impossible de supprimer : des exemplaires de ce livre existent."
        
        del self.__catalogue[isbn]
        self.sauvegarder_donnees()
        self.enregistrer_action("suppression_livre", f"Livre supprimé du catalogue (ISBN: {isbn})")
        return "Livre supprimé avec succès."

    def modifier_utilisateur(self, id_utilisateur, **kwargs):
        user = self.__utilisateurs.get(id_utilisateur)
        if not user:
            return "Utilisateur introuvable."
        
        modifications = []
        if "email" in kwargs:
            modifications.append(f"email: {user.email} -> {kwargs['email']}")
            user.email = kwargs["email"]
            
        if "nom" in kwargs:
            modifications.append(f"nom: {user.nom} -> {kwargs['nom']}")
            user.nom = kwargs["nom"]
            
        # Champs spécifiques aux sous-classes
        if isinstance(user, Etudiant):
            if "niveau_etude" in kwargs:
                user.niveau_etude = kwargs["niveau_etude"]
            if "filiere" in kwargs:
                user.filiere = kwargs["filiere"]
        
        elif isinstance(user, Enseignant):
             if "departement" in kwargs:
                user.departement = kwargs["departement"]
                
        if modifications:
            self.sauvegarder_donnees()
            self.enregistrer_action("modification_utilisateur", f"Utilisateur {id_utilisateur} modifié : {', '.join(modifications)}")
            return "Utilisateur modifié avec succès."
        return "Aucune modification effectuée."

    def supprimer_utilisateur(self, id_utilisateur):
        user = self.__utilisateurs.get(id_utilisateur)
        if not user:
            return "Utilisateur introuvable."
            
        if user.liste_emprunt_en_cour:
            return "Impossible de supprimer : l'utilisateur a des emprunts en cours."
            
        del self.__utilisateurs[id_utilisateur]
        self.sauvegarder_donnees()
        self.enregistrer_action("suppression_utilisateur", f"Utilisateur supprimé (ID: {id_utilisateur})")
        return "Utilisateur supprimé avec succès."

    def rechercher_utilisateur(self,id_utilisateur):
        return self.__utilisateurs.get(id_utilisateur)

    def recherche_utilisateurs_par_mot_clé(self, mot_clé):
        """ Recherche un utilisateur par nom, email ou ID (insensible à la casse). """
        mot_clé = mot_clé.lower()
        resultats = []
        for u in self.__utilisateurs.values():
            if (mot_clé in u.nom.lower() or 
                mot_clé in u.email.lower() or 
                mot_clé in u.id_utilisateur.lower()):
                resultats.append(u)
        return resultats
    
    
    
#     Recherche par titre, auteur, catégorie
# — Recherche par ISBN et année de publication
# — Recherche par disponibilité
# — Recherche par mots-clés
    
    """ Recherche par ISBN """
    
    def rechercher_livre(self,isbn):
        return self.__catalogue.get(isbn)
    
    """ Recherche par auteur """
    
    def recherche_par_auteur(self,auteur):
        livres=self.__catalogue.values()
        resultats=[]
        
        for livre in livres:
            if livre.auteur == auteur:
                resultats.append(livre)
        return resultats
    
    """ Recherche par titre """
    
    def recherche_par_titre(self,titre):
        livres=self.__catalogue.values()
        resultats=[]
        
        for livre in livres:
            if livre.titre == titre:
                resultats.append(livre)
        return resultats
    
    """ Recherche par categorie """
    
    def recherche_par_categorie(self,categorie):
        livres=self.__catalogue.values()
        resultats=[]
        
        for livre in livres:
            if livre.categorie == categorie:
                resultats.append(livre)
        return resultats


    """ Recherche par disponibilité """
    def recherche_par_disponibilite(self,disponibilite):
        exemplaires=self.__exemplaires.values()
        resultats=[]
        
        for exemplaire in exemplaires:
            if exemplaire.statut == disponibilite:
                resultats.append(exemplaire)
        return resultats

    """ Recherche par mot clés """
    def recherche_par_mot_clé(self,mot_clé):
        livres=self.__catalogue.values()
        resultats=[]
        
        for livre in livres:
            chaine_tmp=livre.auteur+" "+livre.isbn+" "+livre.categorie+" "+livre.titre
            if mot_clé.lower() in chaine_tmp.lower():
                resultats.append(livre)
        return resultats

        
    """EMPRUNT"""
    
    def effectuer_emprunt(self,id_exemplaire,id_utilisateur):
        # On commence par aller chercher qui veut quoi et si ça existe vraiment
        user=self.rechercher_utilisateur(id_utilisateur)
        exemplaire=self.__exemplaires.get(id_exemplaire)        
        if user ==None:
            raise ValueError("Oups, cet utilisateur n'existe pas dans notre base.")
        if exemplaire == None:
            raise ValueError("Désolé, ce livre est introuvable.")
        
        if exemplaire.statut != StatutLivre.DISPONIBLE:
            return f"Ah mince, le livre est déjà {exemplaire.statut.value}. Faudra repasser !"
        else:
            # On vérifie si l'utilisateur n'a pas déjà trop abusé de son quota
            if user.peut_emprunter_livre():
                date_emprunt=date.today()
                date_retour_prevue=date_emprunt+timedelta(days=14) # Default 14 days if not specified in Emprunt class
                
                new_emprunt=Emprunt(exemplaire,user,date_emprunt,date_retour_prevue)
                exemplaire.statut=StatutLivre.EMPRUNTE
                user.liste_emprunt_en_cour.append(new_emprunt)
                
                # Mise à jour des compteurs statistiques
                exemplaire.livre.incrementer_compteur()
                user.incrementer_nb_emprunts()
                
                self.__emprunt_en_cour[f"{new_emprunt.id_emprunt}"]=new_emprunt
                self.sauvegarder_donnees()
                self.enregistrer_action("emprunt", f"L'utilisateur {id_utilisateur} a pris l'exemplaire {id_exemplaire}")
                return "Emprunt effectué avec succès."
            else:
                return f"Votre quota d'emprunt de livre est deja de {user.limite_emprunt_max} rendez un livre avant de pouvoir en emprunter un autre"
            
    
    
    def retourner_livre(self,id_emprunt):
        # On récupère l'emprunt. S'il n'y a rien, c'est que c'est déjà réglé ou une erreur.
        emprunt=self.__emprunt_en_cour.get(id_emprunt)
        if emprunt==None :
            return "Visiblement cet emprunt n'existe pas ou le livre a déjà été rendu."
        
        emprunt.date_retour_effective=date.today()
        
        # On n'oublie pas de mettre ça dans l'historique pour garder une trace propre
        emprunt.utilisateur.ajouter_a_historique(emprunt)
        emprunt.utilisateur.liste_emprunt_en_cour.remove(emprunt)
        
        # Ciao l'emprunt actif
        del self.__emprunt_en_cour[id_emprunt]
        
        isbn_exemplaire=emprunt.exemplaire.livre.isbn
        liste_attente=self.__reservations.get(isbn_exemplaire)

        if liste_attente:
            premier_reservaion=liste_attente.pop(0)
            premier_reservaion.notifier_disponibilite()
            emprunt.exemplaire.statut=StatutLivre.RESERVE

        else:
            emprunt.exemplaire.statut=StatutLivre.DISPONIBLE
        self.sauvegarder_donnees()
        self.enregistrer_action("retour", f"Retour de l'emprunt ID: {id_emprunt}")

    def effectuer_reservation(self,isbn,id_utilisateur):
        user = self.rechercher_utilisateur(id_utilisateur)
        livre=self.rechercher_livre(isbn)
        
        if not user:
            return " utilisateur introuvable"
        if not livre:
            return " Livre introuvable dans le catalogue"
        
        nouvel_res=Reservation(livre,user,date.today())
        
        if isbn not in self.__reservations:
            self.__reservations[isbn]=[]
        
        self.__reservations[isbn].append(nouvel_res)
        self.sauvegarder_donnees()
        self.enregistrer_action("reservation", f"L'utilisateur {id_utilisateur} a réservé le livre ISBN: {isbn}")

        return f"Reservation confirmé pour le livre {livre.titre} Position_attente : {len(self.__reservations[isbn])}"
    
    def renouveler_livre(self, id_emprunt):
        emprunt = self.__emprunt_en_cour.get(id_emprunt)
        if not emprunt:
            return "Emprunt introuvable."
            
        isbn = emprunt.exemplaire.livre.isbn
        if isbn in self.__reservations and len(self.__reservations[isbn]) > 0:
            return "Impossible de renouveler : ce livre est réservé par d'autres utilisateurs."
            
        emprunt.renouveler_emprunt()
        self.sauvegarder_donnees()
        self.enregistrer_action("renouvellement", f"Emprunt {id_emprunt} renouvelé jusqu'au {emprunt.date_retour_prevue}")
        return f"Renouvellement effectué. Nouvelle date de retour : {emprunt.date_retour_prevue}"

    def generer_rapport_statistique(self):
        total_livres = len(self.__catalogue)
        total_exemplaires = len(self.__exemplaires)
        
        exemplaires_disponibles = sum(1 for e in self.__exemplaires.values() if e.statut == StatutLivre.DISPONIBLE)
        
        livres_par_statut = {}
        for statut in StatutLivre:
            count = sum(1 for e in self.__exemplaires.values() if e.statut == statut)
            livres_par_statut[statut.value] = count
            
        livres_tries = sorted(self.__catalogue.values(), key=lambda l: l.nb_emprunts_total, reverse=True)
        top_5_livres = livres_tries[:5]
        
        users_tries = sorted(self.__utilisateurs.values(), key=lambda u: u.nb_emprunts_total, reverse=True)
        top_5_users = users_tries[:5]
        
        livres_jamais_empruntes = [l for l in self.__catalogue.values() if l.nb_emprunts_total == 0]
        
        return {
            "total_livres": total_livres,
            "total_exemplaires": total_exemplaires,
            "exemplaires_disponibles": exemplaires_disponibles,
            "livres_par_statut": livres_par_statut,
            "top_5_livres": top_5_livres,
            "top_5_users": top_5_users,
            "livres_jamais_empruntes": livres_jamais_empruntes
        }

    def exporter_statistiques_csv(self, filename=None):
        stats = self.generer_rapport_statistique()
        
        # Horodatage pour éviter d'écraser les fichiers
        if filename is None:
            maintenant = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"statistiques_bibliotheque_{maintenant}.csv"
        
        # Utilisation du chemin absolu pour plus de clarté en cas d'erreur
        filepath = os.path.abspath(filename)
            
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(["--- RESUME GLOBAL ---"])
                writer.writerow(["Indicateur", "Valeur"])
                writer.writerow(["Total Livres", stats["total_livres"]])
                writer.writerow(["Total Exemplaires", stats["total_exemplaires"]])
                writer.writerow(["Exemplaires Disponibles", stats["exemplaires_disponibles"]])
                writer.writerow([])
                
                writer.writerow(["--- EXEMPLAIRES PAR STATUT ---"])
                writer.writerow(["Statut", "Nombre"])
                for statut, count in stats["livres_par_statut"].items():
                    writer.writerow([statut, count])
                writer.writerow([])
                
                writer.writerow(["--- TOP 5 LIVRES LES PLUS EMPRUNTES ---"])
                writer.writerow(["Titre", "ISBN", "Nombre d'emprunts"])
                for livre in stats["top_5_livres"]:
                    writer.writerow([livre.titre, livre.isbn, livre.nb_emprunts_total])
                
            return f"Statistiques exportées avec succès dans :\n{filepath}"
        except PermissionError:
            return f"[ERREUR] Permission refusée. Impossible d'écrire le fichier dans :\n{filepath}\nVérifiez que le dossier est accessible en écriture et qu'un autre programme ne verrouille pas le fichier."
        except Exception as e:
            return f"Erreur lors de l'exportation CSV : {e}"

    def recherche_par_annee(self, annee):
        return [l for l in self.__catalogue.values() if l.anne_publication == annee]
    
    
    def sauvegarder_donnees(self):
        donnees_globales={
            "catalogue":{},
            "utilisateurs":{},
            "exemplaires":{},
            "emprunts":{},
            "reservations":{}
            
        }
        
        for isbn,livre in self.__catalogue.items():
            donnees_globales["catalogue"][isbn]=livre.to_dict()

        for id_utilisateur,user in self.__utilisateurs.items():
            donnees_globales["utilisateurs"][id_utilisateur]=user.to_dict()
        
        for id_exemplaire,exemplaire in self.__exemplaires.items():
            donnees_globales["exemplaires"][id_exemplaire]=exemplaire.to_dict()
            
        for id_emprunt,emprunt in self.__emprunt_en_cour.items():
            donnees_globales["emprunts"][id_emprunt]=emprunt.to_dict()
            
        #icic jai pas appliquer la meme logique car dans la liste de reservation chaque reservation est une liste
        for isbn, liste_attente in self.__reservations.items():
            # On crée une liste de dictionnaires pour cet ISBN
            liste_dicts = []
            for res in liste_attente:
                liste_dicts.append(res.to_dict())
            
            donnees_globales["reservations"][isbn] = liste_dicts

        with open("data_bibliotheque.json", "w", encoding="utf-8") as f:
            json.dump(donnees_globales, f, indent=4, ensure_ascii=False)
            
        print("Sauvegarde réussie dans data_bibliotheque.json")
        
        """
        Charger les donnéee existantes
        """
    def charger_donnees(self):
        # On vérifie si on a quelque chose à charger, sinon on démarre à vide
        if not os.path.exists("data_bibliotheque.json"):
            return

        with open("data_bibliotheque.json", "r", encoding="utf-8") as f:
            donnees = json.load(f)

        # On commence par recharger les bases : le Catalogue
        for isbn, d in donnees["catalogue"].items():
            self.__catalogue[isbn] = Livre.from_dict(d)

        # Ensuite on s'occupe des gens, en respectant leur grade
        for uid, d in donnees["utilisateurs"].items():
            u_type = d["type_utilisateur"]
            if u_type == "ETUDIANT":
                self.__utilisateurs[uid] = Etudiant.from_dict(d)
            elif u_type == "ENSEIGNANT":
                self.__utilisateurs[uid] = Enseignant.from_dict(d)
            elif u_type == "ADMIN":
                self.__utilisateurs[uid] = PersonnelAdministratif.from_dict(d)
        
        # Mise à jour du compteur global des utilisateurs pour éviter les doublons d'ID
        if self.__utilisateurs:
            ids = [int(uid.split("-")[1]) for uid in self.__utilisateurs.keys()]
            Utilisateur.compteur = max(ids) + 1

        #  Recharger les Exemplaires (apres avoir recharger le catalogue
        for eid, d in donnees["exemplaires"].items():
            self.__exemplaires[eid] = Exemplaire.from_dict(d, self.__catalogue)
        
        if self.__exemplaires:
            ids = [int(eid.split("-")[1]) for eid in self.__exemplaires.keys()]
            Exemplaire.compteur = max(ids) + 1

        # on Recharge les Emprunts
        for eid, d in donnees["emprunts"].items():
            # Reconstruction de l'objet Emprunt
            nouvel_emp = Emprunt.from_dict(d, self.__exemplaires.values(), self.__utilisateurs.values())
            self.__emprunt_en_cour[eid] = nouvel_emp
            nouvel_emp.utilisateur.liste_emprunt_en_cour.append(nouvel_emp)
            
        if self.__emprunt_en_cour:
            ids = [int(eid.split("-")[1]) for eid in self.__emprunt_en_cour.keys()]
            Emprunt.compteur = max(ids) + 1

        #  Recharger les Réservations
        for isbn, liste_d in donnees["reservations"].items():
            self.__reservations[isbn] = [
                Reservation.from_dict(rd, self.__utilisateurs.values(), self.__catalogue.values()) 
                for rd in liste_d
            ]
        
        # Mise à jour du compteur des réservations
        toutes_res = [res for liste in self.__reservations.values() for res in liste]
        if toutes_res:
            ids = [int(r.id_reservation.split("-")[1]) for r in toutes_res]
            Reservation.compteur = max(ids) + 1
            
        # Recharger l'historique des emprunts pour les utilisateurs
        for uid, d_user in donnees["utilisateurs"].items():
            user = self.__utilisateurs.get(uid)
            # Vérifier si l'utilisateur existe et s'il a un historique sauvegardé
            if user and "historique_emprunts" in d_user:
                # Vérifier que c'est bien une liste de dictionnaires (nouveau format)
                hist_data = d_user["historique_emprunts"]
                if hist_data and isinstance(hist_data[0], dict):
                    for d_emp in hist_data:
                        try:
                            # Reconstruire l'objet Emprunt
                            # Note: On passe tous les exemplaires et utilisateurs pour la liaison
                            emp = Emprunt.from_dict(d_emp, self.__exemplaires.values(), self.__utilisateurs.values())
                            user.ajouter_a_historique(emp)
                        except Exception as e:
                            # On ignore silencieusement les erreurs de reconstruction d'historique 
                            # pour ne pas bloquer le chargement principal
                            pass
                elif hist_data and isinstance(hist_data[0], str):
                     # Ancien format (liste d'IDs) - On ne peut pas facilement restaurer les objets
                     # On laisse vide ou on pourrait essayer de chercher dans les archives si on en avait
                     pass
    
    
    
    def enregistrer_action(self, action, details):
        # on recupere le time d'abord
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # on formatte sa 
        ligne_log = f"[{horodatage}] - {action.upper()} : {details}\n"
        
        #on sauvegarde
        with open("bibliotheque.log", "a", encoding="utf-8") as f:
            f.write(ligne_log)