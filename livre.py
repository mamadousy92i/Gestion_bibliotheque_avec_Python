from enum import Enum

class StatutLivre(Enum):
    DISPONIBLE = "disponible"
    EMPRUNTE = "emprunté"
    RESERVE = "réservé"
    PERDU = "perdu"
    ENDOMMAGE = "endommagé"

class Livre:
    def __init__(self, isbn, titre, auteur,anne_publication,categorie, statut=StatutLivre.DISPONIBLE):
        self.__isbn = isbn
        self.__titre = titre
        self.__auteur = auteur
        self.__statut = statut
        self.__anne_publication= anne_publication
        self.__categorie = categorie
        self.__nb_emprunts_total = 0 # On commence à zéro,

    @property
    def isbn(self): 
        return self.__isbn

    @property
    def titre(self): 
        return self.__titre

    @titre.setter
    def titre(self, valeur):
        self.__titre = valeur

    @property
    def auteur(self): 
        return self.__auteur

    @auteur.setter
    def auteur(self, valeur):
        self.__auteur = valeur
    
    @property
    def anne_publication(self):
        return self.__anne_publication

    @anne_publication.setter
    def anne_publication(self, valeur):
        self.__anne_publication = valeur
    
    @property
    def categorie(self):
        return self.__categorie

    @categorie.setter
    def categorie(self, valeur):
        self.__categorie = valeur

    @property
    def statut(self):
        return self.__statut

    @statut.setter
    def statut(self, nouveau_statut):
        if isinstance(nouveau_statut, StatutLivre):
            self.__statut = nouveau_statut
        else:
            raise ValueError("Oups ! Le statut doit être de type StatutLivre.")
    
    @property
    def nb_emprunts_total(self):
        return self.__nb_emprunts_total

    @nb_emprunts_total.setter
    def nb_emprunts_total(self, valeur):
        self.__nb_emprunts_total = valeur
    
    def incrementer_compteur(self):
        self.__nb_emprunts_total += 1

    def to_dict(self):
        return {
            "isbn": self.isbn,
            "titre": self.titre,
            "auteur": self.auteur,
            "anne_publication":self.anne_publication,
            "categorie":self.categorie,
            "statut": self.statut.value,
            "nb_emprunts_total": self.nb_emprunts_total
        }

    @classmethod
    def from_dict(cls, data):
        statut_str = data.get("statut", "disponible")
        livre = cls(
            isbn=data["isbn"],
            titre=data["titre"],
            auteur=data["auteur"],
            anne_publication=int(data["anne_publication"]),
            categorie=data["categorie"],
            statut=StatutLivre(statut_str)
        )
        # Restaurer le compteur d'emprunts
        livre.nb_emprunts_total = data.get("nb_emprunts_total", 0)
        return livre

    def __str__(self):
        return f"[{self.isbn}] {self.titre} - {self.auteur} (Statut: {self.statut.value})"