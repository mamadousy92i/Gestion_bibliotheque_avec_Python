from abc import ABC, abstractmethod

class Utilisateur(ABC):
    compteur = 1

    def __init__(self, nom, email, type_utilisateur, prefixe, id_utilisateur=None):
        if id_utilisateur:
            self.__id_utilisateur = id_utilisateur
        else:
            # Petite logique pour générer un ID qui claque (ex: ETU-1)
            self.__id_utilisateur = f"{prefixe}-{Utilisateur.compteur}"
            Utilisateur.compteur += 1
            
        self.__nom = nom
        self.__email = email
        self.__type_utilisateur = type_utilisateur
        self.__liste_emprunt_en_cour = []
        self._limite_emprunt_max = 0
        self.__historique_emprunts = []
        self.__nb_emprunts_total = 0

    @property
    def id_utilisateur(self):
        return self.__id_utilisateur

    @property
    def nom(self):
        return self.__nom

    @nom.setter
    def nom(self, valeur):
        self.__nom = valeur

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valeur):
        self.__email = valeur

    @property
    def type_utilisateur(self):
        return self.__type_utilisateur

    @property
    def liste_emprunt_en_cour(self):
        return self.__liste_emprunt_en_cour
    
    @property
    def limite_emprunt_max(self):
        return self._limite_emprunt_max
    
    @property
    def historique_emprunts(self):
        return self.__historique_emprunts
    
    @property
    def nb_emprunts_total(self):
        return self.__nb_emprunts_total

    @nb_emprunts_total.setter
    def nb_emprunts_total(self, valeur):
        self.__nb_emprunts_total = valeur
    
    def incrementer_nb_emprunts(self):
        self.__nb_emprunts_total += 1
    
    def ajouter_a_historique(self, emprunt):
        self.__historique_emprunts.append(emprunt)

    def peut_emprunter_livre(self):
        # On vérifie si l'utilisateur n'a pas déjà trop de livres sur les bras
        if len(self.liste_emprunt_en_cour) >= self._limite_emprunt_max:
            return False
        return True

