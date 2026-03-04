import os
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

NOTION_HEADERS = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def get_prix_unitaire(ingredient: str) -> float:
    url = f"https://api.notion.com/v1/databases/{os.environ['NOTION_STOCKS_DB_ID']}/query"
    response = requests.post(url, headers=NOTION_HEADERS, json={})
    response.raise_for_status()

    ingredient_lower = ingredient.lower().strip()
    for page in response.json()["results"]:
        props = page["properties"]
        nom = "".join(r["plain_text"] for r in props["Ingrédient"]["title"])
        nom_lower = nom.lower().strip()
        if ingredient_lower in nom_lower or nom_lower in ingredient_lower:
            return props["Prix unitaire (€)"]["number"] or 0.0
    return 0.0


def get_prix_produit(produit: str) -> float:
    url = f"https://api.notion.com/v1/databases/{os.environ['NOTION_PRODUCTS_DB_ID']}/query"
    response = requests.post(url, headers=NOTION_HEADERS, json={})
    response.raise_for_status()

    produit_lower = produit.lower().strip()
    for page in response.json()["results"]:
        props = page["properties"]
        nom = "".join(r["plain_text"] for r in props["Produit"]["title"])
        nom_lower = nom.lower().strip()
        # Match if either string contains the other
        if produit_lower in nom_lower or nom_lower in produit_lower:
            return props["Prix de vente TTC (€)"]["number"] or 0.0
    return 0.0



def log_to_notion(
    fournisseur: str,
    produits: str,
    email_fournisseur: str,
    notes: str = "",
    montant_estime: float = 0.0,
) -> None:
    reference = f"CMD-{date.today().isoformat()}-{fournisseur[:8].upper().replace(' ', '')}"
    payload = {
        "parent": {"database_id": os.environ["NOTION_ORDERS_DB_ID"]},
        "properties": {
            "Référence commande": {"title": [{"text": {"content": reference}}]},
            "Fournisseur": {"select": {"name": fournisseur}},
            "Produits commandés": {"rich_text": [{"text": {"content": produits}}]},
            "Email envoyé à": {"email": email_fournisseur},
            "Date commande": {"date": {"start": date.today().isoformat()}},
            "Statut": {"select": {"name": "Envoyée"}},
            "Notes": {"rich_text": [{"text": {"content": notes}}]},
            "Montant estimé (€)": {"number": montant_estime},
        },
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=payload)
    response.raise_for_status()