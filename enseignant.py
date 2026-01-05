from Bibliothéque.utilisateur import Utilisateur

class Enseignant(Utilisateur):
    def __init__(self, nom, email, departement, id_utilisateur=None):
        super().__init__(nom, email, "ENSEIGNANT", prefixe="ENS", id_utilisateur=id_utilisateur)
        self.__departement = departement
        self._limite_emprunt_max = 5

    @property
    def departement(self): 
        return self.__departement

    @departement.setter
    def departement(self, valeur):
        self.__departement = valeur

    def to_dict(self):
        liste_ids = []
        for e in self.liste_emprunt_en_cour:
            liste_ids.append(e.id_emprunt)
        
        historique_data = [emp.to_dict() for emp in self.historique_emprunts]
            
        return {
            "id_utilisateur": self.id_utilisateur,
            "nom": self.nom,
            "email": self.email,
            "type_utilisateur": self.type_utilisateur,
            "departement": self.departement,
            "liste_emprunt_en_cour": liste_ids,
            "historique_emprunts": historique_data,
            "nb_emprunts_total": self.nb_emprunts_total
        }

    @classmethod 
    def from_dict(cls, data):
        enseignant = cls(
            nom=data["nom"], 
            email=data["email"], 
            departement=data["departement"], 
            id_utilisateur=data["id_utilisateur"]
        )
        enseignant.nb_emprunts_total = data.get("nb_emprunts_total", 0)
        return enseignant