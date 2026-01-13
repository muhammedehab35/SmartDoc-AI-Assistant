"""
Orchestrator Agent - Router principal avec LangGraph
"""

import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated, List
import operator
from datetime import datetime

from database import db
from utils import lambda_helper, generate_id


# ===== ÉTAT DE L'AGENT =====

class OrchestratorState(TypedDict):
    """État de l'orchestrator"""
    messages: Annotated[List, operator.add]
    user_id: str
    intent: str
    context: dict
    next_agent: str
    final_response: str
    error: str


# ===== INITIALISATION LLM =====

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3,
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)


# ===== NŒUDS DU GRAPH =====

def analyze_intent(state: OrchestratorState) -> OrchestratorState:
    """
    Nœud 1: Analyse l'intention de l'utilisateur
    """
    print("[ORCHESTRATOR] Analyse de l'intention...")

    user_message = state["messages"][-1].content if state["messages"] else ""

    system_prompt = """
Tu es un classificateur d'intention expert pour un assistant médical senior.

Analyse le message et retourne UNE SEULE catégorie parmi:

- medication: Questions sur médicaments, posologie, rappels, interactions
  Exemples: "Quels sont mes médicaments?", "Quand prendre mon Doliprane?", "C'est quoi mon traitement?"

- symptom: Symptômes de santé, douleurs, malaises, questions médicales
  Exemples: "J'ai mal à la tête", "Je ne me sens pas bien", "J'ai de la fièvre"

- appointment: Rendez-vous médicaux, calendrier, docteurs
  Exemples: "Quand est mon RDV?", "Rendez-vous chez le cardiologue", "Mon prochain docteur"

- emergency: Urgence, chute, douleur intense, appel à l'aide, danger
  Exemples: "Aide!", "Je suis tombé", "Douleur poitrine", "Urgence", "Au secours"

- general: Conversation générale, salutations, questions diverses
  Exemples: "Bonjour", "Comment ça va?", "Merci", "Qui es-tu?"

IMPORTANT: Réponds UNIQUEMENT avec le mot-clé de la catégorie, rien d'autre.

Si le message contient "urgence", "aide", "tombé", "douleur intense" → toujours répondre "emergency"
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Message à classifier: {user_message}")
        ])

        intent = response.content.strip().lower()

        # Validation de l'intent
        valid_intents = ["medication", "symptom", "appointment", "emergency", "general"]
        if intent not in valid_intents:
            intent = "general"

        state["intent"] = intent
        print(f"[ORCHESTRATOR] Intent détecté: {intent}")

    except Exception as e:
        print(f"[ORCHESTRATOR] Erreur analyse intent: {e}")
        state["intent"] = "general"
        state["error"] = str(e)

    return state


def load_user_context(state: OrchestratorState) -> OrchestratorState:
    """
    Nœud 2: Charge le contexte utilisateur depuis DynamoDB
    """
    print("[ORCHESTRATOR] Chargement du contexte utilisateur...")

    user_id = state["user_id"]
    state["context"] = {}

    try:
        # Récupérer profil utilisateur
        user_profile = db.get_user(user_id)
        if user_profile:
            state["context"]["user_profile"] = user_profile
            print(f"[ORCHESTRATOR] Profil chargé pour {user_profile.get('name', user_id)}")
        else:
            print(f"[ORCHESTRATOR] Aucun profil trouvé pour {user_id}")
            state["context"]["user_profile"] = {"user_id": user_id, "name": "Utilisateur"}

        # Récupérer médicaments actifs
        medications = db.get_user_medications(user_id, active_only=True)
        state["context"]["medications"] = medications
        print(f"[ORCHESTRATOR] {len(medications)} médicaments actifs")

        # Récupérer prochains rendez-vous
        appointments = db.get_user_appointments(user_id, limit=5)
        state["context"]["appointments"] = appointments
        print(f"[ORCHESTRATOR] {len(appointments)} rendez-vous à venir")

    except Exception as e:
        print(f"[ORCHESTRATOR] Erreur chargement contexte: {e}")
        state["error"] = str(e)

    return state


def route_to_agent(state: OrchestratorState) -> OrchestratorState:
    """
    Nœud 3: Détermine quel agent spécialisé appeler
    """
    print("[ORCHESTRATOR] Routing vers agent spécialisé...")

    intent = state["intent"]

    agent_mapping = {
        "medication": "medication-agent",
        "symptom": "symptom-agent",
        "appointment": "symptom-agent",  # Le symptom agent gère aussi les RDV
        "emergency": "emergency-agent",
        "general": "general-response"
    }

    next_agent = agent_mapping.get(intent, "general-response")
    state["next_agent"] = next_agent

    print(f"[ORCHESTRATOR] Agent sélectionné: {next_agent}")

    return state


def call_specialized_agent(state: OrchestratorState) -> OrchestratorState:
    """
    Nœud 4: Appelle l'agent spécialisé ou génère réponse générale
    """
    agent_name = state["next_agent"]

    print(f"[ORCHESTRATOR] Appel de l'agent: {agent_name}")

    if agent_name == "general-response":
        # Réponse générale directe
        state["final_response"] = generate_general_response(state)
        return state

    try:
        # Préparer le payload pour l'agent spécialisé
        payload = {
            "user_id": state["user_id"],
            "message": state["messages"][-1].content if state["messages"] else "",
            "context": state["context"]
        }

        # Appeler l'agent Lambda
        result = lambda_helper.invoke_agent(agent_name, payload)

        if "error" in result:
            state["final_response"] = "Désolé, une erreur est survenue. Pouvez-vous reformuler votre question?"
            state["error"] = result["error"]
        else:
            body = result.get("body", {})
            if isinstance(body, str):
                import json
                body = json.loads(body)

            state["final_response"] = body.get("response", "Désolé, je n'ai pas pu traiter votre demande.")

        print(f"[ORCHESTRATOR] Réponse reçue de {agent_name}")

    except Exception as e:
        print(f"[ORCHESTRATOR] Erreur appel agent: {e}")
        state["final_response"] = "Désolé, je rencontre une difficulté technique. Veuillez réessayer."
        state["error"] = str(e)

    return state


def generate_general_response(state: OrchestratorState) -> str:
    """
    Génère une réponse pour conversation générale
    """
    print("[ORCHESTRATOR] Génération réponse générale...")

    user_message = state["messages"][-1].content if state["messages"] else ""
    user_name = state["context"].get("user_profile", {}).get("name", "")

    system_prompt = f"""
Tu es un assistant médical bienveillant pour {user_name}, une personne âgée.

Réponds de manière:
- Chaleureuse et rassurante
- Simple et claire (phrases courtes)
- Empathique et patiente
- En français

Si c'est une salutation, salue chaleureusement.
Si c'est un remerciement, réponds poliment.
Si c'est une question générale, réponds simplement.

Reste toujours positif et encourageant.
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        return response.content

    except Exception as e:
        print(f"[ORCHESTRATOR] Erreur génération réponse: {e}")
        return "Bonjour! Comment puis-je vous aider aujourd'hui?"


def save_conversation(state: OrchestratorState) -> OrchestratorState:
    """
    Nœud 5: Sauvegarde la conversation dans DynamoDB
    """
    print("[ORCHESTRATOR] Sauvegarde de la conversation...")

    try:
        conversation_data = {
            'conversation_id': generate_id('conv'),
            'user_id': state['user_id'],
            'timestamp': datetime.utcnow().isoformat(),
            'user_message': state['messages'][-1].content if state['messages'] else "",
            'assistant_response': state['final_response'],
            'intent': state['intent'],
            'agent_used': state['next_agent']
        }

        db.save_conversation(conversation_data)
        print("[ORCHESTRATOR] Conversation sauvegardée")

    except Exception as e:
        print(f"[ORCHESTRATOR] Erreur sauvegarde conversation: {e}")
        state["error"] = str(e)

    return state


# ===== CONSTRUCTION DU GRAPH LANGGRAPH =====

def create_orchestrator_graph():
    """
    Crée le graph LangGraph orchestrateur
    """
    print("[ORCHESTRATOR] Création du graph LangGraph...")

    workflow = StateGraph(OrchestratorState)

    # Ajouter les nœuds
    workflow.add_node("analyze_intent", analyze_intent)
    workflow.add_node("load_context", load_user_context)
    workflow.add_node("route", route_to_agent)
    workflow.add_node("call_agent", call_specialized_agent)
    workflow.add_node("save", save_conversation)

    # Définir le flow
    workflow.set_entry_point("analyze_intent")
    workflow.add_edge("analyze_intent", "load_context")
    workflow.add_edge("load_context", "route")
    workflow.add_edge("route", "call_agent")
    workflow.add_edge("call_agent", "save")
    workflow.add_edge("save", END)

    return workflow.compile()


# Créer l'instance du graph (singleton)
orchestrator = create_orchestrator_graph()

print("[ORCHESTRATOR] Graph LangGraph créé avec succès!")
