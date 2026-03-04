import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from langchain_core.tools import tool

from utils.notion_helpers import get_prix_unitaire, log_to_notion

load_dotenv()

def _send_email (to_email: str, subject: str, body: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = os.environ["SENDER_EMAIL"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as server:
        server.starttls()
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        server.sendmail(os.environ["SENDER_EMAIL"], to_email, msg.as_string())

@tool
def envoyer_commande_fournisseur(
    ingredient: str,
    quantite: str,
    unite: str,
    fournisseur: str,
    email_fournisseur: str,
    notes: str = "",
) -> str:
    """
    Envoie un email de commande à un fournisseur et enregistre la commande dans Notion.
    Utilise ce tool quand Madeleine veut commander un ingrédient auprès d'un fournisseur.

    Paramètres :
    - ingredient : nom de l'ingrédient (ex: "Farine T65")
    - quantite : quantité souhaitée (ex: "50")
    - unite : unité (ex: "kg", "L", "g", "unités")
    - fournisseur : nom du fournisseur (ex: "Minoterie Dupont")
    - email_fournisseur : adresse email du fournisseur
    - notes : remarques optionnelles
    """

    body = f"""Madame, Monsieur,

    Je me permets de vous contacter afin de passer commande pour notre boulangerie artisanale.

    Nous souhaiterions commander :
    - Produit    : {ingredient}
    - Quantité   : {quantite} {unite}
    {"  - Remarques : " + notes if notes else ""}

    Merci de confirmer la disponibilité et le délai de livraison.

    Cordialement,
    Madeleine Croûton
    Chez Madeleine — Boulangerie Artisanale
    Saint-Germain-des-Croissants
    """
    prix_unitaire = get_prix_unitaire(ingredient)
    montant_estime = round(prix_unitaire * float(quantite), 2)

    quantite_note = f"{quantite} {unite}"
    notes_completes = f"{quantite_note}" + (f" — {notes}" if notes else "")

    _send_email(email_fournisseur, f"Commande — {ingredient}", body)

    log_to_notion(
        fournisseur=fournisseur,
        produits=ingredient,
        email_fournisseur=email_fournisseur,
        notes=notes_completes,
        montant_estime=montant_estime,
    )

    return (
        f"Commande envoyée à {fournisseur} ({email_fournisseur}) "
        f"pour {quantite} {unite} de {ingredient} "
        f"(montant estimé : {montant_estime} €), et enregistrée dans Notion."
    )
