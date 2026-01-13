"""
Symptom Agent - Analyse des symptômes et gestion des rendez-vous avec LangGraph
"""

import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from typing import TypedDict, List, Dict
from datetime import datetime, timedelta

from database import db
from utils import format_datetime


# ===== ÉTAT DE L'AGENT =====

class SymptomState(TypedDict):
    """État du symptom agent"""
    user_id: str
    message: str
    context: dict
    severity: str  # "mild", "moderate", "severe", "critical"
    symptoms: List[str]
    recommendations: List[str]
    appointments: List[Dict]
    response: str
    error: str


# ===== INITIALISATION LLM =====

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3,
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)


# ===== NŒUDS DU GRAPH =====

def analyze_symptom(state: SymptomState) -> SymptomState:
    """
    Nœud 1: Analyse les symptômes mentionnés
    """
    print("[SYMPTOM] Analyse des symptômes...")

    message = state["message"]
    user_name = state["context"].get("user_profile", {}).get("name", "")
    medical_conditions = state["context"].get("user_profile", {}).get("medical_conditions", [])

    system_prompt = f"""
Tu es un médecin assistant expert qui évalue les symptômes.

Patient: {user_name}
Conditions médicales connues: {', '.join(medical_conditions) if medical_conditions else 'Aucune'}

Message du patient: {message}

Analyse les symptômes et réponds avec un JSON structuré:
{{
    "severity": "mild|moderate|severe|critical",
    "symptoms": ["symptôme 1", "symptôme 2"],
    "needs_immediate_attention": true|false
}}

Critères de gravité:
- mild: Inconfort léger, pas urgent (ex: petit mal de tête, fatigue)
- moderate: Symptômes gênants mais pas alarmants (ex: mal de tête persistant, nausées)
- severe: Symptômes préoccupants nécessitant consultation rapide (ex: douleur forte, vomissements)
- critical: Urgence médicale immédiate (ex: douleur poitrine, difficulté respirer, confusion)

Réponds UNIQUEMENT avec le JSON, rien d'autre.
"""

    try:
        response = llm.invoke([SystemMessage(content=system_prompt)])

        # Parser la réponse JSON
        import json
        result = json.loads(response.content)

        state["severity"] = result.get("severity", "mild")
        state["symptoms"] = result.get("symptoms", [])

        print(f"[SYMPTOM] Gravité: {state['severity']}, Symptômes: {state['symptoms']}")

    except Exception as e:
        print(f"[SYMPTOM] Erreur analyse: {e}")
        # Fallback: analyse simple par mots-clés
        message_lower = message.lower()

        critical_keywords = ["poitrine", "respirer", "confusion", "inconscient", "paralysie"]
        severe_keywords = ["douleur forte", "vomissement", "fièvre élevée", "saigne"]

        if any(k in message_lower for k in critical_keywords):
            state["severity"] = "critical"
        elif any(k in message_lower for k in severe_keywords):
            state["severity"] = "severe"
        elif any(k in message_lower for k in ["mal", "douleur", "fatigue"]):
            state["severity"] = "moderate"
        else:
            state["severity"] = "mild"

        state["symptoms"] = ["Symptôme mentionné dans le message"]
        state["error"] = str(e)

    return state


def check_medication_side_effects(state: SymptomState) -> SymptomState:
    """
    Nœud 2: Vérifie si les symptômes peuvent être des effets secondaires
    """
    print("[SYMPTOM] Vérification effets secondaires médicaments...")

    medications = state["context"].get("medications", [])
    symptoms = state["symptoms"]

    if not medications:
        print("[SYMPTOM] Aucun médicament à vérifier")
        return state

    med_names = [m['name'] for m in medications]
    symptoms_text = ", ".join(symptoms)

    system_prompt = f"""
Tu es un pharmacien expert.

Médicaments du patient: {', '.join(med_names)}
Symptômes rapportés: {symptoms_text}

Ces symptômes pourraient-ils être des effets secondaires de ces médicaments?

Réponds de manière simple:
- Si possible lien: explique brièvement
- Si peu probable: rassure
- Recommande toujours de consulter médecin/pharmacien

Sois bref et clair (2-3 phrases max).
"""

    try:
        response = llm.invoke([SystemMessage(content=system_prompt)])
        side_effects_info = response.content

        # Ajouter à la réponse finale
        state["recommendations"].append(f"ℹ️ Concernant vos médicaments: {side_effects_info}")

        print("[SYMPTOM] Vérification effets secondaires terminée")

    except Exception as e:
        print(f"[SYMPTOM] Erreur vérification effets: {e}")
        state["error"] = str(e)

    return state


def generate_recommendations(state: SymptomState) -> SymptomState:
    """
    Nœud 3: Génère des recommandations basées sur la gravité
    """
    print("[SYMPTOM] Génération des recommandations...")

    severity = state["severity"]
    symptoms = state["symptoms"]
    user_name = state["context"].get("user_profile", {}).get("name", "")

    recommendations = []

    if severity == "critical":
        recommendations.append("🚨 URGENT: Appelez le 15 (SAMU) immédiatement")
        recommendations.append("🚑 Ne restez pas seul(e)")
        recommendations.append("📞 Prévenez vos proches")

    elif severity == "severe":
        recommendations.append("⚠️ Consultez un médecin aujourd'hui")
        recommendations.append("📞 Appelez votre médecin ou allez aux urgences")
        recommendations.append("👥 Informez un proche")

    elif severity == "moderate":
        recommendations.append("🏥 Consultez votre médecin dans les 24-48h")
        recommendations.append("📝 Notez l'évolution de vos symptômes")
        recommendations.append("💊 Prenez vos médicaments habituels")

    else:  # mild
        recommendations.append("😊 Ces symptômes sont généralement bénins")
        recommendations.append("💧 Reposez-vous et hydratez-vous")
        recommendations.append("📊 Surveillez l'évolution")
        recommendations.append("🏥 Si aggravation, consultez un médecin")

    state["recommendations"].extend(recommendations)

    print(f"[SYMPTOM] {len(recommendations)} recommandations générées")

    return state


def check_appointments(state: SymptomState) -> SymptomState:
    """
    Nœud 4: Vérifie les rendez-vous à venir
    """
    print("[SYMPTOM] Vérification des rendez-vous...")

    appointments = state["context"].get("appointments", [])
    state["appointments"] = appointments

    if appointments:
        next_appt = appointments[0]
        appt_info = f"""
📅 Votre prochain rendez-vous:
   {next_appt.get('title', 'Rendez-vous')}
   Le {next_appt.get('date', '')} à {next_appt.get('time', '')}
"""
        state["recommendations"].append(appt_info)
        print(f"[SYMPTOM] {len(appointments)} rendez-vous trouvés")
    else:
        print("[SYMPTOM] Aucun rendez-vous à venir")

    return state


def create_response(state: SymptomState) -> SymptomState:
    """
    Nœud 5: Crée la réponse finale complète
    """
    print("[SYMPTOM] Création de la réponse finale...")

    user_name = state["context"].get("user_profile", {}).get("name", "")
    severity = state["severity"]
    symptoms = state["symptoms"]
    recommendations = state["recommendations"]

    # En-tête basé sur la gravité
    if severity == "critical":
        header = f"⚠️ {user_name}, c'est une situation d'URGENCE!"
    elif severity == "severe":
        header = f"⚠️ {user_name}, vos symptômes nécessitent une attention médicale."
    elif severity == "moderate":
        header = f"💭 {user_name}, je comprends votre inquiétude."
    else:
        header = f"😊 {user_name}, ne vous inquiétez pas trop."

    # Construction de la réponse
    response_parts = [header, ""]

    if symptoms:
        response_parts.append("📋 Symptômes identifiés:")
        for symptom in symptoms:
            response_parts.append(f"  • {symptom}")
        response_parts.append("")

    response_parts.append("💡 Mes recommandations:")
    for rec in recommendations:
        response_parts.append(f"  {rec}")
    response_parts.append("")

    # Note finale rassurante
    if severity in ["mild", "moderate"]:
        response_parts.append("💙 N'hésitez pas à me reparler si vos symptômes changent.")
    else:
        response_parts.append("💙 Vous n'êtes pas seul(e). Faites-vous aider.")

    state["response"] = "\n".join(response_parts)

    print("[SYMPTOM] Réponse finale créée")

    return state


# ===== CONSTRUCTION DU GRAPH LANGGRAPH =====

def create_symptom_graph():
    """
    Crée le graph LangGraph pour le symptom agent
    """
    print("[SYMPTOM] Création du graph LangGraph...")

    workflow = StateGraph(SymptomState)

    # Ajouter les nœuds
    workflow.add_node("analyze", analyze_symptom)
    workflow.add_node("check_meds", check_medication_side_effects)
    workflow.add_node("recommend", generate_recommendations)
    workflow.add_node("check_appts", check_appointments)
    workflow.add_node("create_response", create_response)

    # Flow linéaire
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "check_meds")
    workflow.add_edge("check_meds", "recommend")
    workflow.add_edge("recommend", "check_appts")
    workflow.add_edge("check_appts", "create_response")
    workflow.add_edge("create_response", END)

    return workflow.compile()


# Créer l'instance du graph (singleton)
symptom_agent = create_symptom_graph()

print("[SYMPTOM] Graph LangGraph créé avec succès!")
