import os
import requests
from dotenv import load_dotenv

from langchain_core.tools import tool

load_dotenv()


HEADERS = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

DB_IDS = {
    "stocks": os.environ["NOTION_STOCKS_DB_ID"],
    "products": os.environ["NOTION_PRODUCTS_DB_ID"],
    "sales": os.environ["NOTION_SALES_DB_ID"],
    "orders": os.environ["NOTION_ORDERS_DB_ID"],
}

def _get_prop(prop: dict) -> str:
    """Extract a readable value from a Notion property."""
    t = prop["type"]
    if t == "title":
        return "".join(r["plain_text"] for r in prop["title"])
    if t == "rich_text":
        return "".join(r["plain_text"] for r in prop["rich_text"])
    if t == "number":
        return str(prop["number"]) if prop["number"] is not None else "N/A"
    if t == "select":
        return prop["select"]["name"] if prop["select"] else "N/A"
    if t == "email":
        return prop["email"] or "N/A"
    if t == "date":
        return prop["date"]["start"] if prop["date"] else "N/A"
    if t == "formula":
        f = prop["formula"]
        ft = f.get("type")
        if ft == "number":
            return str(f["number"]) if f["number"] is not None else "N/A"
        if ft == "string":
            return f["string"] or "N/A"
        if ft == "boolean":
            return str(f["boolean"])
        return "N/A"
    if t == "checkbox":
        return "Oui" if prop["checkbox"] else "Non"
    return "N/A"

def query_notion(db_key: str, filters: dict | None = None) -> list[dict]:
    db_id = DB_IDS[db_key]
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    body = {"filter": filters} if filters else {}
    response = requests.post(url, headers=HEADERS, json=body)
    response.raise_for_status()
    rows = []
    for page in response.json()["results"]:
        row = {key: _get_prop(val) for key, val in page["properties"].items()}
        row["_page_id"] = page["id"]
        rows.append(row)
    return rows

@tool
def consulter_boulangerie(query_type: str) -> str:
    """
    Consulte la base de données de la boulangerie Chez Madeleine.

    query_type doit être l'une des valeurs suivantes :
    - "stocks" : tous les ingrédients en stock
    - "alerts" : uniquement les ingrédients sous le seuil d'alerte (à commander)
    - "products" : catalogue des produits, prix de vente, marges
    - "sales" : historique des ventes
    - "orders" : commandes fournisseurs passées
    """
    if query_type == "alerts":
        rows = query_notion("stocks")
        sous_seuil = [
            r for r in rows
            if float(r["Quantité en stock"]) < float(r["Seuil alerte"])
        ]
        if not sous_seuil:
            return "Tous les stocks sont au-dessus du seuil d'alerte. Rien à commander."
        lines = ["=== INGREDIENTS SOUS LE SEUIL D'ALERTE ==="]
        for r in sous_seuil:
            lines.append(
                f"{r['Ingrédient']} : {r['Quantité en stock']} {r['Unité']} "
                f"(seuil : {r['Seuil alerte']} {r['Unité']}) "
                f"— Fournisseur : {r['Fournisseur']} ({r['Email fournisseur']})"
            )
        return "\n".join(lines)

    if query_type not in ("stocks", "products", "sales", "orders"):
        return f"Type invalide : '{query_type}'. Choisir parmi : stocks, alerts, products, sales, orders."

    rows = query_notion(query_type)
    if not rows:
        return "Aucune donnée trouvée."

    lines = [f"=== {query_type.upper()} ({len(rows)} entrées) ==="]
    for row in rows:
        row_str = " | ".join(f"{k}: {v}" for k, v in row.items() if k != "_page_id")
        lines.append(row_str)
    return "\n".join(lines)
