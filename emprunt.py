from datetime import *


class Emprunt:

    compteur = 1
    penalité = 100
    duree_renouvellement = 7

    def __init__(
        self,
        exemplaire,
        utilisateur,
        date_emprunt,
        date_retour_prevue,
        date_retour_effective=None,
        est_actif=True,
    ):
        # On crée un nouvel emprunt, l'acte de naissance d'un prêt
        self.__id_emprunt = f"EMP-{Emprunt.compteur}"
        self.__exemplaire = exemplaire
        self.__utilisateur = utilisateur
        self.__date_emprunt = date_emprunt
        self.__date_retour_prevue = date_retour_prevue
        self.__date_retour_effective = date_retour_effective
        self.__est_actif = est_actif
        Emprunt.compteur += 1

    @property
    def id_emprunt(self):
        return self.__id_emprunt

    @property
    def exemplaire(self):
        return self.__exemplaire

    # @livre.setter
    # def livre(self,livre):  # a voir si c'est logique de mettre un setter car normalement c'est un objet issu de la classe livre
    #     self.__livre=livre

    # parreille pour utilisateur
    @property
    def utilisateur(self):
        return self.__utilisateur

    @property
    def date_emprunt(self):
        return self.__date_emprunt

    @property
    def date_retour_prevue(self):
        return self.__date_retour_prevue

    @date_retour_prevue.setter
    def date_retour_prevue(self, date_retour_prevue):
        self.__date_retour_prevue = date_retour_prevue

    @property
    def date_retour_effective(self):
        return self.__date_retour_effective

    @date_retour_effective.setter
    def date_retour_effective(self, date_retour_effective):
        self.__date_retour_effective = date_retour_effective

    # pareille aussi ici je pense qu'on peut ne pas mettre un setter
    @property
    def est_actif(self):
        return self.__est_actif

    @est_actif.setter
    def est_actif(self, est_actif):
        self.__est_actif = est_actif

    # ici je met mes methodes
    """
    Méthodes
● est_en_retard()
● calcul_penalite()
● renouveler()
● cloturer()
● to_dict()
● from_dict()
    """
    
    
    def retourner_emprunt(self):
        self.date_retour_effective = date.today()
        self.est_actif = False

    def est_en_retard(self):
        # On vérifie si l'utilisateur est toujours dans les clous ou s'il a traîné
        date_a_verifier = self.date_retour_effective if self.date_retour_effective else date.today()          
        
        if date_a_verifier > self.__date_retour_prevue:
                print("Ah ! Le livre est en retard.")
                return True
        return False

    def _calculer_penalité(self):
        # Pas de pitié pour les retardataires : 100 unités par jour !
        if self.est_en_retard():
            date_fin = self.date_retour_effective if self.date_retour_effective else date.today()
            jour = date_fin - self.__date_retour_prevue
            
            return  Emprunt.penalité * jour.days
        return 0

    def renouveler_emprunt(self):
        self.date_retour_prevue = self.__date_retour_prevue + timedelta(
            days=Emprunt.duree_renouvellement
        )

    def to_dict(self):
        return {
            "id_emprunt": self.__id_emprunt,
            "id_exemplaire": self.exemplaire.id_exemplaire,
            "id_utilisateur": self.utilisateur.id_utilisateur,
            "date_emprunt": str(self.__date_emprunt),
            "date_retour_prevue": str(self.__date_retour_prevue),
            "date_retour_effective": str(self.__date_retour_effective),
            "est_actif": self.__est_actif,
        }

    @classmethod
    def from_dict(cls, data, liste_exemplaire, listes_utilisateurs):
        id_exemplaire_cherche = data["id_exemplaire"]
        id_utilisateur_cherché = data["id_utilisateur"]

        exemplaire_cherche = None
        utilisateur_cherche = None

        for i in liste_exemplaire:
            if i.id_exemplaire == id_exemplaire_cherche:
                exemplaire_cherche = i
                break

        for j in listes_utilisateurs:
            if j.id_utilisateur == id_utilisateur_cherché:
                utilisateur_cherche = j
                break

        if data["date_retour_effective"] == "None":
            date_retour_effective = None
        else:
            date_retour_effective = datetime.strptime(
                data["date_retour_effective"], "%Y-%m-%d"
            ).date()

        nouvel_emprunt = cls(
            exemplaire=exemplaire_cherche,
            utilisateur=utilisateur_cherche,
            date_emprunt=datetime.strptime(data["date_emprunt"], "%Y-%m-%d").date(),
            date_retour_prevue=datetime.strptime(
                data["date_retour_prevue"], "%Y-%m-%d"
            ).date(),
            date_retour_effective=date_retour_effective,
            est_actif=data["est_actif"],
        )

        nouvel_emprunt.__id_emprunt = data["id_emprunt"]

        return nouvel_emprunt


