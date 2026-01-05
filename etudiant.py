from Bibliothéque.utilisateur import Utilisateur

class Etudiant(Utilisateur):
    def __init__(self, nom, email, niveau_etude, filiere, id_utilisateur=None):
        super().__init__(nom, email, "ETUDIANT", prefixe="ETU", id_utilisateur=id_utilisateur)
        self.__niveau_etude = niveau_etude
        self.__filiere = filiere
        self._limite_emprunt_max = 3 # Un étudiant peut avoir 3 livres, c'est déjà pas mal !
    @property
    def niveau_etude(self):
        return self.__niveau_etude

    @niveau_etude.setter
    def niveau_etude(self, valeur):
        self.__niveau_etude = valeur
        
    @property
    def filiere(self):
        return self.__filiere

    @filiere.setter
    def filiere(self, valeur):
        self.__filiere = valeur

    def to_dict(self):
        liste_ids = []
        
        for emprunt in self.liste_emprunt_en_cour:
            liste_ids.append(emprunt.id_emprunt)
        
        historique_data = [emp.to_dict() for emp in self.historique_emprunts]
        
        return {
            "id_utilisateur": self.id_utilisateur,
            "nom": self.nom,
            "email": self.email,
            "type_utilisateur": self.type_utilisateur,
            "niveau_etude": self.niveau_etude,
            "filiere": self.filiere,
            "liste_emprunt_en_cour": liste_ids,
            "historique_emprunts": historique_data,
            "nb_emprunts_total": self.nb_emprunts_total
        }

    @classmethod 
    def from_dict(cls, data):
        etudiant = cls(
            nom=data["nom"],
            email=data["email"],
            niveau_etude=data["niveau_etude"],
            filiere=data["filiere"],
            id_utilisateur=data["id_utilisateur"]
        )
        etudiant.nb_emprunts_total = data.get("nb_emprunts_total", 0)
        return etudiant