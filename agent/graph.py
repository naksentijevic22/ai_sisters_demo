import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent

from agent.prompts import SYSTEM_PROMPT

from tools.notion_reader import consulter_boulangerie
from tools.email_sender import envoyer_commande_fournisseur
from tools.devis_generator import generer_devis

load_dotenv()

llm = ChatMistralAI(
    model_name="mistral-large-latest",
    api_key=os.environ["MISTRAL_API_KEY"], # type: ignore
)

tools = [consulter_boulangerie, envoyer_commande_fournisseur, generer_devis]

agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
