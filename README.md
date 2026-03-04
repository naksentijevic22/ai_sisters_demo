# 🥐 Chez Madeleine — Assistant IA Boulangerie

Agent conversationnel IA pour aider Madeleine Croûton à gérer sa boulangerie artisanale.
Développé dans le cadre du test technique AI Sisters.

---

## Architecture

```
aisisters_test/
├── main.py                  # Interface Streamlit
├── agent/
│   ├── graph.py             # Agent LangGraph (ReAct)
│   └── prompts.py           # System prompt
├── tools/
│   ├── notion_reader.py     # Tool 1 : lecture base Notion
│   ├── email_sender.py      # Tool 2 : envoi email + écriture Notion
│   └── devis_generator.py   # Tool 3 : génération de devis PDF
├── utils/
│   └── notion_helpers.py    # Fonctions partagées (prix produits/ingrédients)
├── devis/                   # Devis PDF générés (auto-créé)
├── .env.example             # Template des variables d'environnement
└── requirements.txt
```

---

## Stack technique

| Composant | Technologie |
|---|---|
| Orchestration agent | LangGraph (`create_react_agent`) |
| LLM | Mistral Large (via `langchain-mistralai`) |
| Base de données | Notion API (REST) |
| Envoi email | SMTP / Mailtrap sandbox |
| Génération PDF | fpdf2 |
| Interface | Streamlit |

---

## Les 3 tools

### Tool 1 — `consulter_boulangerie`
Lit les données de la boulangerie depuis Notion.
- `stocks` : ingrédients, quantités, fournisseurs, prix
- `alerts` : ingrédients sous le seuil d'alerte *(filtrage Python, pas LLM)*
- `products` : catalogue produits, prix de vente, marges
- `sales` : historique des ventes
- `orders` : commandes fournisseurs passées

### Tool 2 — `envoyer_commande_fournisseur`
- Génère et envoie un email de commande au fournisseur via SMTP
- Calcule le montant estimé depuis les prix en stock
- Enregistre la commande dans la table "Commandes Fournisseurs" de Notion

### Tool 3 — `generer_devis`
- Génère un devis pour une commande événementielle (mariage, séminaire…)
- Récupère les prix de vente depuis le catalogue Notion
- Exporte un PDF dans le dossier `devis/`

---

## Installation

### 1. Cloner le repo et créer l'environnement virtuel

```bash
git clone <repo-url>
cd aisisters_test
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Remplir `.env` avec vos credentials :

```env
MISTRAL_API_KEY=your_mistral_key

NOTION_TOKEN=secret_xxx
NOTION_STOCKS_DB_ID=xxx
NOTION_PRODUCTS_DB_ID=xxx
NOTION_SALES_DB_ID=xxx
NOTION_ORDERS_DB_ID=xxx

SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_user
SMTP_PASSWORD=your_mailtrap_password
SENDER_EMAIL=madeleine@chez-madeleine.fr
```

### 3. Lancer l'application

```bash
streamlit run main.py
```

---

## Exemples de questions

**Stocks & produits**
- *"Combien de beurre il me reste ?"*
- *"Quels ingrédients sont sous le seuil d'alerte ?"*
- *"C'est quoi ma marge sur les éclairs au chocolat ?"*
- *"Quel est mon produit le plus rentable ?"*

**Ventes**
- *"Combien de croissants j'ai vendu la semaine dernière ?"*
- *"Compare mes ventes de baguettes le samedi versus le lundi."*

**Commandes fournisseurs**
- *"Commande 50kg de farine T65 chez Minoterie Dupont"*
- *"Il me reste plus assez de beurre, commande 20kg à la Laiterie du Midi"*

**Devis**
- *"Fais un devis pour le mariage Dupont : 200 croissants et 50 éclairs"*
- *"Un client veut 80 pains au chocolat pour un séminaire, fais le devis"*

---

## Choix techniques

**LangGraph `create_react_agent`** — pattern ReAct (Reason + Act) : le LLM raisonne, choisit un tool, observe le résultat, et itère jusqu'à avoir une réponse complète. Choix du prebuilt pour sa simplicité et sa lisibilité lors de la démo.

**Mistral Large** — bon équilibre performance/coût, excellente compréhension du français.

**Notion REST API directe** — contournement d'un bug de compatibilité de `notion-client` 3.0 qui a supprimé la méthode `databases.query()`. Utilisation de `requests` directement sur l'API REST.

**Filtrage en Python** — les comparaisons numériques (ex: stocks sous seuil d'alerte) sont faites en Python côté tool, pas déléguées au LLM, pour éviter les erreurs de raisonnement arithmétique.

**Matching partiel des noms** — la recherche de produits et ingrédients utilise une correspondance partielle (`in`) plutôt qu'une égalité stricte, pour tolérer les variations de nommage (ex: *"Quiche lorraine"* → *"Quiche lorraine (part)"*).
