import os
from datetime import date, timedelta
from fpdf import FPDF
from langchain_core.tools import tool
from utils.notion_helpers import get_prix_produit


def _generate_pdf(client: str, evenement: str, lignes: list[dict], total: float, validite: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Chez Madeleine - Boulangerie Artisanale", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Saint-Germain-des-Croissants", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "DEVIS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Info block
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Client      : {client}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Evenement   : {evenement}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Date        : {date.today().isoformat()}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Validite    : jusqu'au {validite}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Table header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 8, "Produit", border=1, fill=True)
    pdf.cell(25, 8, "Qte", border=1, fill=True, align="C")
    pdf.cell(35, 8, "Prix unit.", border=1, fill=True, align="C")
    pdf.cell(35, 8, "Sous-total", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    # Table rows
    pdf.set_font("Helvetica", "", 10)
    for ligne in lignes:
        pdf.cell(90, 7, ligne["produit"], border=1)
        pdf.cell(25, 7, str(ligne["quantite"]), border=1, align="C")
        pdf.cell(35, 7, f"{ligne['prix_unitaire']:.2f} EUR", border=1, align="C")
        pdf.cell(35, 7, f"{ligne['sous_total']:.2f} EUR", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)

    # Total
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(150, 8, "TOTAL TTC")
    pdf.cell(35, 8, f"{total:.2f} EUR", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Payment terms
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Acompte 30% a la commande : {round(total * 0.3, 2):.2f} EUR", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Solde a la livraison       : {round(total * 0.7, 2):.2f} EUR", new_x="LMARGIN", new_y="NEXT")

    # Save
    os.makedirs("devis", exist_ok=True)
    filename = f"devis/devis_{client.replace(' ', '_')}_{date.today().isoformat()}.pdf"
    pdf.output(filename)
    return filename


@tool
def generer_devis(client: str, evenement: str, items: str) -> str:
    """
    Génère un devis pour une commande spéciale (mariage, anniversaire, événement).
    Utilise ce tool quand Madeleine reçoit une demande de devis pour un événement.

    Paramètres :
    - client : nom du client (ex: "Famille Dupont")
    - evenement : type d'événement (ex: "Mariage", "Anniversaire", "Réunion d'entreprise")
    - items : liste des produits et quantités, format "produit:quantite" séparés par des virgules
              ex: "Croissant pur beurre:100,Éclair au chocolat:50,Brioche tressée:10"
    """
    lignes = []
    total = 0.0
    validite = (date.today() + timedelta(days=30)).isoformat()

    for item in items.split(","):
        item = item.strip()
        if ":" not in item:
            continue
        produit, qte_str = item.rsplit(":", 1)
        produit = produit.strip()
        try:
            qte = int(qte_str.strip())
        except ValueError:
            continue

        prix_unitaire = get_prix_produit(produit)
        sous_total = round(prix_unitaire * qte, 2)
        total += sous_total
        lignes.append({
            "produit": produit,
            "quantite": qte,
            "prix_unitaire": prix_unitaire,
            "sous_total": sous_total,
        })

    total = round(total, 2)
    pdf_path = _generate_pdf(client, evenement, lignes, total, validite)

    # Text summary for the agent
    lignes_text = "\n".join(
        f"  - {l['produit']:<35} x{l['quantite']:<5} @ {l['prix_unitaire']:.2f}€ = {l['sous_total']:.2f}€"
        for l in lignes
    )

    return f"""
DEVIS — Chez Madeleine

Client    : {client}
Événement : {evenement}
Validité  : jusqu'au {validite}

{lignes_text}

TOTAL TTC : {total:.2f} €
Acompte (30%) : {round(total * 0.3, 2):.2f} €
Solde à la livraison : {round(total * 0.7, 2):.2f} €

PDF généré : {pdf_path}
"""
