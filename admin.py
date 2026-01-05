from Bibliothéque.utilisateur import Utilisateur

class PersonnelAdministratif(Utilisateur):
    def __init__(self, nom, email, service, id_utilisateur=None):
        super().__init__(nom, email, "ADMIN", prefixe="ADM", id_utilisateur=id_utilisateur)
        self.__service = service
        self._limite_emprunt_max = 7 # Le staff a droit à 7 livres, privilège de l'administration !

    @property
    def service(self): 
        return self.__service

    @service.setter
    def service(self, valeur):
        self.__service = valeur

    def to_dict(self):
        return {
            "id_utilisateur": self.id_utilisateur,
            "nom": self.nom,
            "email": self.email,
            "type_utilisateur": self.type_utilisateur,
            "service": self.service,
            "liste_emprunt_en_cour": [e.id_emprunt for e in self.liste_emprunt_en_cour],
            "historique_emprunts": [e.to_dict() for e in self.historique_emprunts],
            "nb_emprunts_total": self.nb_emprunts_total
        }

    @classmethod 
    def from_dict(cls, data):
        admin = cls(data["nom"], data["email"], data["service"], data["id_utilisateur"])
        admin.nb_emprunts_total = data.get("nb_emprunts_total", 0)
        return admin