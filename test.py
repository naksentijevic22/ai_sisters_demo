from agent.graph import agent

def test(message: str):
    print(f"\n{'='*60}")
    print(f"Madeleine : {message}")
    print('='*60)
    response = agent.invoke({
        "messages": [{"role": "user", "content": message}]
    })
    print(f"Agent : {response['messages'][-1].content}")

# --- Tool 1 : consulter_boulangerie ---

# # Stocks
# test("Combien de beurre il me reste ?")
# test("Quels sont les ingrédients en dessous du seuil d'alerte ?")
# test("C'est quoi le prix du kilo de farine T65 chez mon fournisseur ?")

# # Produits
# test("C'est quoi ma marge sur les éclairs au chocolat ?")
# test("Montre-moi tous mes produits avec leur prix de vente.")
# test("Quel est mon produit le plus rentable ?")

# # Ventes
# test("Combien de croissants j'ai vendu la semaine dernière ?")
# test("Quel est mon meilleur produit en chiffre d'affaires ?")
# test("Compare mes ventes de baguettes le samedi versus le lundi.")

# # --- Tool 2 : envoyer_commande_fournisseur ---

# test("Prépare une commande de 50kg de farine T65 chez Minoterie Dupont.")
# test("Il me reste plus assez de beurre, commande 20kg à la Laiterie du Midi.")

# # --- Tool 3 : generer_devis ---

# test("Fais-moi un devis pour le mariage Dupont : 200 croissants, 100 éclairs au chocolat et 20 brioches.")
# test("Un client veut commander 50 quiches et 80 pains au chocolat pour un séminaire. Fais le devis.")

# # --- Questions mixtes ---

# test("J'ai besoin de commander ce qui manque dans mes stocks. Qu'est-ce que je dois commander ?")
