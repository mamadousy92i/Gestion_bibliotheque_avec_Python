from Bibliothéque.livre import StatutLivre
class Exemplaire:
    compteur=1
    
    def __init__(self,livre):
        # On donne une identité unique à cette copie physique du livre
        self.__id_exemplaire=f"EX001-{Exemplaire.compteur}"
        self.__livre=livre
        self.__statut=StatutLivre.DISPONIBLE
        Exemplaire.compteur+=1
        
        
    @property
    def id_exemplaire(self):
        return self.__id_exemplaire
    
    @property
    def livre(self):
        return self.__livre
    
    @property
    def statut(self):
        return self.__statut
    
    @statut.setter
    def statut(self,statut):
        self.__statut=statut
        
    
    def to_dict(self):
        return {
            "id_exemplaire": self.id_exemplaire,
            "isbn_livre": self.livre.isbn,
            "statut": self.statut.value
        }

    @classmethod
    def from_dict(cls, data, catalogue):
        # On retrouve le grand frère (le Livre) pour recréer l'Exemplaire
        livre = catalogue.get(data["isbn_livre"])
        nouvel_ex = cls(livre)
        nouvel_ex._Exemplaire__id_exemplaire = data["id_exemplaire"]
        nouvel_ex.statut = StatutLivre(data["statut"])
        return nouvel_ex