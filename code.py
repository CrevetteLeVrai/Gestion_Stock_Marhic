"""
Module de gestion de stock d'entrepôt et de préparation de colis.
Simule un système FIFO avec gestion d'alertes et tri volumétrique.
"""
import collections

class Entrepot:
    """
    Gère le stock selon la méthode FIFO (Premier Entré, Premier Sorti).
    Maintient un log d'alertes statique limité à 3 entrées.
    """
    def __init__(self):
        # Stockage : Dictionnaire de files d'attente (deque)
        self.stock = collections.defaultdict(collections.deque)
        # Log des alertes (Limité à 3 produits maximum)
        self.log_alertes = []
        # Liste pour stocker les colis une fois fermés
        self.liste_colis = []
        # Seuil minimum : Alerte si quantité strictement inférieure à 2
        self.seuil_min = 2
        self.initialiser_stock_defaut()

    def initialiser_stock_defaut(self):
        """Charge un stock de départ pour faciliter les tests."""
        self.ajouter_lot("A3, A3, B5, B5, C1, C1, A2, A2")

    def ajouter_lot(self, chaine_produits):
        """
        Traite une chaîne (ex: 'A1, B2') et ajoute les produits au stock.
        Gère la mise en majuscule automatique.
        """
        # Nettoyage : découpage, suppression espaces, mise en majuscule
        produits = [p.strip().upper() for p in chaine_produits.split(',')]

        for id_produit in produits:
            # Vérification basique du format (ex: "A1" min 2 chars)
            if len(id_produit) >= 2 and id_produit[0].isalpha():
                self.stock[id_produit].append(id_produit)
                
                # À chaque ajout, on vérifie si cela résout une alerte existante
                self.verifier_et_nettoyer_alerte(id_produit)
            else:
                print(f"Format invalide ignoré : {id_produit}")

    def verifier_et_nettoyer_alerte(self, id_produit):
        """
        Vérifie si le niveau de stock actuel permet de retirer une alerte du log.
        """
        quantite = len(self.stock[id_produit])
        
        # Si le produit est listé dans le log des alertes
        if id_produit in self.log_alertes:
            if quantite >= self.seuil_min:
                # Condition remplie : On supprime l'alerte
                self.log_alertes.remove(id_produit)
                print(f" RÉSOLU : Alerte {id_produit} retirée du log (Stock {quantite} >= {self.seuil_min}).")
            else:
                # Feedback important : On a ajouté du stock, mais pas assez
                print(f" STOCK BAS : {id_produit} ajouté, mais seuil non atteint ({quantite}/{self.seuil_min}). Alerte maintenue.")

    def enregistrer_alerte(self, id_produit):
        """
        Génère une alerte si le stock est bas et s'il y a de la place dans le log.
        """
        # Si le stock est suffisant ou si l'alerte est déjà notée, on ignore
        if len(self.stock[id_produit]) >= self.seuil_min:
            return
        if id_produit in self.log_alertes:
            return

        # Vérification de la capacité du log (Max 3 slots)
        if len(self.log_alertes) < 3:
            self.log_alertes.append(id_produit)
            print(f"!!! ALERTE ACTIVÉE : {id_produit} (Stock critique) !!!")
        else:
            # Cas où le log est plein : l'alerte est perdue (comportement demandé)
            print(f" LOG PLEIN (3/3) : Impossible de logger l'alerte pour {id_produit}. Traitez les urgences !")

    def afficher_inventaire(self):
        """Affiche le contenu actuel du stock."""
        print("\n--- ÉTAT DE L'INVENTAIRE ---")
        if not self.stock:
            print("(Inventaire vide)")
  
        # Tri alphabétique des produits pour l'affichage
        for id_produit, articles in sorted(self.stock.items()):
            quantite = len(articles)
            # Marqueur visuel pour identifier les stocks bas
            etat = " (BAS)" if quantite < self.seuil_min else ""
            print(f"Produit : {id_produit} | Quantité : {quantite}{etat}")

class Conditionnement:
    """Gère l'assemblage des colis et le tri par volume."""

    @staticmethod
    def preparer_colis(entrepot, chaine_commande):
        """
        Crée un colis en retirant les produits du stock.
        Les produits sont triés par volume décroissant (les gros au fond).
        """
        contenu_colis = []
        liste_commande = [p.strip().upper() for p in chaine_commande.split(',')]
        
        for id_produit in liste_commande:
            if not id_produit: 
                continue # Ignore les entrées vides

            # Vérifie si le produit est disponible dans l'entrepôt
            if id_produit in entrepot.stock and entrepot.stock[id_produit]:
                # On déduit le volume depuis le nom (ex: A3 -> 3). 0 si erreur.
                try:
                    volume = int(id_produit[1:])
                except ValueError:
                    volume = 0
                
                # Ajout temporaire au colis
                contenu_colis.append({'id': id_produit, 'vol': volume})
                # Retrait physique du stock
                entrepot.stock[id_produit].popleft()
            else:
                print(f" RUPTURE : {id_produit} manquant (Backorder).")
            
            # Vérification systématique de l'alerte APRES le prélèvement
            entrepot.enregistrer_alerte(id_produit)

        # Tri : Volume décroissant (simulation physique, gros objets en bas)
        contenu_colis.sort(key=lambda x: x['vol'], reverse=True)

        if contenu_colis:
            entrepot.liste_colis.append(contenu_colis)
            print(f" Colis créé avec succès ({len(contenu_colis)} articles).")

    @staticmethod
    def afficher_colis(entrepot):
        """Affiche les colis (vue verticale : le haut de la pile est le haut du carton)."""
        if not entrepot.liste_colis:
            print("\nAucun colis en zone d'expédition.")
            return

        for index, colis in enumerate(entrepot.liste_colis):
            print(f"\n--- COLIS N°{index + 1} ---")
            # reversed() permet d'afficher le dernier élément ajouté en haut
            for article in reversed(colis):
                print(f"|  [{article['id']}]  |")
            print("--------------")

def main():
    """Menu principal interactif."""
    entrepot = Entrepot()
    emballage = Conditionnement()
    
    while True:
        print("\n1.Ajout | 2.Colis | 3.Stock | 4.Voir Colis | 5.Alertes | 6.Quitter")
        
        choix = input("Votre choix : ")
        
        if choix == "1": 
            entrepot.ajouter_lot(input("Produits à entrer : "))
        elif choix == "2": 
            emballage.preparer_colis(entrepot, input("Liste commande : "))
        elif choix == "3": 
            entrepot.afficher_inventaire()
        elif choix == "4": 
            emballage.afficher_colis(entrepot)
        elif choix == "5": 
            print(f" Log des alertes : {entrepot.log_alertes}")
        elif choix == "6": 
            print("Arrêt du système.")
            break
        else:
            print("Choix inconnu.")

if __name__ == "__main__":
    main()

