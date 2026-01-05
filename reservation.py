from datetime import *
class Reservation:
    compteur=1
    
    def __init__(self, livre, utilisateur, date_demande):
        self.__id_reservation=f"RES-{Reservation.compteur}"
        self.__livre = livre
        self.__utilisateur = utilisateur
        self.__date_demande = date_demande
        Reservation.compteur+=1
        
    @property
    def date_demande(self):
        return self.__date_demande
    
    @property
    def id_reservation(self):
        return self.__id_reservation
    
    @property
    def livre(self):
        return self.__livre
    
    @property
    def utilisateur(self):
        return self.__utilisateur
    
    
    def notifier_disponibilite(self):
        nom_fichier = "notifications_reservations.txt"
        date_notif = date.today()
        
        message = (
            f"--- NOTIFICATION DE DISPONIBILITÉ ---\n"
            f"Date : {date_notif}\n"
            f"Utilisateur : {self.utilisateur.nom} (ID: {self.utilisateur.id_utilisateur})\n"
            f"Livre disponible : {self.livre.titre} (ISBN: {self.livre.isbn})\n"
            f"Action : Merci de passer à la bibliothèque pour récupérer votre exemplaire.\n"
            f"{'-' * 40}\n"
        )
        
        with open(nom_fichier, "a", encoding="utf-8") as f:
            f.write(message)
        
        print(f"Notification générée dans {nom_fichier} pour {self.utilisateur.nom}")
    
    
    
    def to_dict(self):
        return {
            "id_reservation":self.__id_reservation,
            "id_utilisateur":self.__utilisateur.id_utilisateur,
            "isbn":self.__livre.isbn,
            "date_demande":str(self.__date_demande)
            
            
        }

    @classmethod
    def from_dict(cls,data,liste_utilisateur,liste_livres):
        isbn_cherche = data["isbn"]
        id_utilisateur_cherché = data["id_utilisateur"]
        
        livre_cherche = None
        utilisateur_cherche = None

        for i in liste_livres:
            if i.isbn == isbn_cherche:
                livre_cherche = i
                break

        for j in liste_utilisateur:
            if j.id_utilisateur == id_utilisateur_cherché:
                utilisateur_cherche = j
                break
        nouvel_reservation = cls(
            livre=livre_cherche,
            utilisateur=utilisateur_cherche,
            date_demande=datetime.strptime(data['date_demande'], "%Y-%m-%d").date()
        )
        
        nouvel_reservation.__id_reservation=data["id_reservation"]
        
        return nouvel_reservation