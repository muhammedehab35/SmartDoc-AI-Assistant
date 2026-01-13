"""
Emergency Agent - Gestion des urgences avec LangGraph
"""

import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from typing import TypedDict, List, Dict
from datetime import datetime

from database import db
from utils import sns_helper, generate_id


# ===== ÉTAT DE L'AGENT =====

class EmergencyState(TypedDict):
    """État de l'emergency agent"""
    user_id: str
    message: str
    context: dict
    severity: str  # "critical", "high", "medium", "low"
    emergency_type: str  # "fall", "pain", "breathing", "other"
    actions_taken: List[str]
    contacts_notified: List[Dict]
    guidance: str
    response: str
    error: str


# ===== INITIALISATION LLM =====

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.2,  # Plus déterministe pour urgences
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)


# ===== NŒUDS DU GRAPH =====

def assess_severity(state: EmergencyState) -> EmergencyState:
    """
    Nœud 1: Évalue la gravité de l'urgence
    """
    print("[EMERGENCY] Évaluation de la gravité...")

    message = state["message"].lower()

    # Mots-clés critiques (urgence immédiate)
    critical_keywords = [
        "douleur poitrine", "mal poitrine", "coeur",
        "respirer", "souffle", "respiration",
        "tombé", "chute", "tombe",
        "saigne", "sang",
        "inconscient", "évanoui",
        "paralysie", "bras engourdi", "jambe engourdie",
        "confusion", "tête qui tourne",
        "crise", "convulsion"
    ]

    # Mots-clés haute priorité
    high_keywords = [
        "aide", "urgent", "mal", "douleur forte",
        "peur", "angoisse", "aide-moi"
    ]

    # Détecter le type d'urgence
    if any(k in message for k in ["tombé", "chute", "tombe"]):
        state["emergency_type"] = "fall"
    elif any(k in message for k in ["poitrine", "coeur", "douleur"]):
        state["emergency_type"] = "pain"
    elif any(k in message for k in ["respirer", "souffle"]):
        state["emergency_type"] = "breathing"
    else:
        state["emergency_type"] = "other"

    # Évaluation de base par mots-clés
    if any(keyword in message for keyword in critical_keywords):
        severity_guess = "critical"
    elif any(keyword in message for keyword in high_keywords):
        severity_guess = "high"
    else:
        severity_guess = "medium"

    # Demander à Claude pour confirmer
    system_prompt = """
Tu es un médecin urgentiste expert.

Analyse ce message d'une personne âgée et évalue la gravité:

- critical: Danger vital immédiat (appeler 15 IMMÉDIATEMENT)
- high: Situation préoccupante (contacter famille et médecin)
- medium: Inconfort significatif (surveiller, consulter si persiste)
- low: Inquiétude mineure

Réponds UNIQUEMENT avec un mot: critical, high, medium ou low
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Message: {state['message']}")
        ])

        severity = response.content.strip().lower()

        # Validation
        if severity not in ["critical", "high", "medium", "low"]:
            severity = severity_guess

        state["severity"] = severity
        print(f"[EMERGENCY] Gravité évaluée: {severity} (type: {state['emergency_type']})")

    except Exception as e:
        print(f"[EMERGENCY] Erreur évaluation: {e}")
        state["severity"] = severity_guess
        state["error"] = str(e)

    return state


def notify_emergency_contacts(state: EmergencyState) -> EmergencyState:
    """
    Nœud 2: Notifie les contacts d'urgence
    """
    print("[EMERGENCY] Notification des contacts...")

    user_profile = state["context"].get("user_profile", {})
    emergency_contacts = user_profile.get("emergency_contacts", [])
    user_name = user_profile.get("name", "Utilisateur")
    user_phone = user_profile.get("phone", "")

    severity = state["severity"]
    message = state["message"]

    if not emergency_contacts:
        print("[EMERGENCY] Aucun contact d'urgence configuré")
        state["actions_taken"].append("⚠️ Aucun contact d'urgence configuré")
        return state

    # Envoyer SMS seulement si gravité élevée
    if severity in ["critical", "high"]:
        print(f"[EMERGENCY] Envoi de {len(emergency_contacts)} SMS...")

        results = sns_helper.send_emergency_sms(
            contacts=emergency_contacts,
            user_name=user_name,
            message=message,
            severity=severity
        )

        state["contacts_notified"] = results

        for result in results:
            if result['success']:
                state["actions_taken"].append(f"✅ SMS envoyé à {result['contact']}")
                print(f"[EMERGENCY] SMS envoyé à {result['contact']}")
            else:
                state["actions_taken"].append(f"❌ Échec SMS à {result['contact']}")
                print(f"[EMERGENCY] Échec SMS à {result['contact']}")

    else:
        print("[EMERGENCY] Gravité faible, pas de notification SMS")
        state["actions_taken"].append("ℹ️ Gravité faible, contacts non alertés")

    return state


def log_emergency(state: EmergencyState) -> EmergencyState:
    """
    Nœud 3: Enregistre l'urgence dans DynamoDB
    """
    print("[EMERGENCY] Enregistrement de l'urgence...")

    try:
        emergency_data = {
            'emergency_id': generate_id('emg'),
            'user_id': state['user_id'],
            'timestamp': datetime.utcnow().isoformat(),
            'severity': state['severity'],
            'emergency_type': state['emergency_type'],
            'message': state['message'],
            'actions_taken': state['actions_taken'],
            'contacts_notified': [c['contact'] for c in state['contacts_notified']],
            'resolved': False
        }

        db.save_emergency(emergency_data)

        state["actions_taken"].append("📝 Urgence enregistrée dans le système")
        print(f"[EMERGENCY] Urgence enregistrée: {emergency_data['emergency_id']}")

    except Exception as e:
        print(f"[EMERGENCY] Erreur enregistrement: {e}")
        state["error"] = str(e)

    return state


def provide_immediate_guidance(state: EmergencyState) -> EmergencyState:
    """
    Nœud 4: Fournit des conseils immédiats
    """
    print("[EMERGENCY] Génération des conseils immédiats...")

    severity = state["severity"]
    emergency_type = state["emergency_type"]
    message = state["message"]
    user_name = state["context"].get("user_profile", {}).get("name", "")

    # Guidance spécifique par type d'urgence
    if emergency_type == "fall":
        guidance_context = """
Personne âgée qui est tombée.
Instructions:
1. Ne pas se lever trop vite
2. Vérifier s'il y a des douleurs
3. Demander de l'aide pour se relever
4. S'asseoir et se reposer
"""
    elif emergency_type == "breathing":
        guidance_context = """
Problème respiratoire.
Instructions:
1. S'asseoir bien droit
2. Essayer de respirer calmement
3. Ouvrir une fenêtre
4. Ne pas paniquer
"""
    elif emergency_type == "pain":
        guidance_context = """
Douleur signalée.
Instructions:
1. S'asseoir ou s'allonger
2. Noter où ça fait mal
3. Rester calme
4. Appeler de l'aide si douleur intense
"""
    else:
        guidance_context = "Situation d'urgence générale."

    system_prompt = f"""
Tu es un assistant d'urgence médicale parlant à {user_name}, une personne âgée.

Situation: {message}
Type d'urgence: {emergency_type}
Gravité: {severity}

{guidance_context}

Fournis des conseils IMMÉDIATS et CLAIRS:
- Instructions numérotées très simples
- Phrases courtes et directes
- Ton rassurant mais sérieux
- Maximum 4-5 instructions

Si gravité CRITICAL: rappeler d'appeler le 15 en PREMIER
Si gravité HIGH: recommander d'appeler médecin rapidement
Si gravité MEDIUM/LOW: rassurer et donner conseils pratiques

IMPORTANT: Reste calme et rassurant dans ton ton.
"""

    try:
        response = llm.invoke([SystemMessage(content=system_prompt)])
        state["guidance"] = response.content
        print("[EMERGENCY] Conseils générés")

    except Exception as e:
        print(f"[EMERGENCY] Erreur génération conseils: {e}")

        # Fallback guidance
        if severity == "critical":
            state["guidance"] = """
🚨 URGENCE VITALE

1. Appelez le 15 (SAMU) IMMÉDIATEMENT
2. Ne restez pas seul(e)
3. Restez calme et suivez les instructions du SAMU
4. Vos proches sont prévenus
"""
        elif severity == "high":
            state["guidance"] = """
⚠️ SITUATION URGENTE

1. Appelez votre médecin maintenant
2. Si aggravation, appelez le 15
3. Restez au téléphone avec moi
4. Vos proches sont prévenus
"""
        else:
            state["guidance"] = """
💙 JE SUIS LÀ POUR VOUS

1. Restez calme
2. Asseyez-vous confortablement
3. Respirez calmement
4. Je surveille votre situation
"""

        state["error"] = str(e)

    return state


def create_final_response(state: EmergencyState) -> EmergencyState:
    """
    Nœud 5: Crée la réponse finale complète
    """
    print("[EMERGENCY] Création de la réponse finale...")

    severity = state["severity"]
    guidance = state["guidance"]
    actions_taken = state["actions_taken"]
    user_name = state["context"].get("user_profile", {}).get("name", "")

    # En-tête basé sur gravité
    if severity == "critical":
        header = f"🚨 {user_name.upper()}, C'EST UNE URGENCE!"
    elif severity == "high":
        header = f"⚠️ {user_name}, situation urgente"
    else:
        header = f"💙 {user_name}, je suis là pour vous"

    # Construction de la réponse
    response_parts = [
        header,
        "",
        "📋 CE QUE VOUS DEVEZ FAIRE:",
        guidance,
        ""
    ]

    # Actions effectuées
    if actions_taken:
        response_parts.append("✅ ACTIONS EFFECTUÉES:")
        for action in actions_taken:
            response_parts.append(f"  {action}")
        response_parts.append("")

    # Message de fin
    if severity == "critical":
        response_parts.append("🚑 LES SECOURS SONT EN ROUTE")
        response_parts.append("💙 Vous n'êtes pas seul(e)")
    elif severity == "high":
        response_parts.append("👥 Vos proches sont prévenus")
        response_parts.append("💙 De l'aide arrive")
    else:
        response_parts.append("💙 N'hésitez pas à me reparler")
        response_parts.append("📞 Je suis toujours disponible")

    state["response"] = "\n".join(response_parts)

    print("[EMERGENCY] Réponse finale créée")

    return state


# ===== CONSTRUCTION DU GRAPH LANGGRAPH =====

def create_emergency_graph():
    """
    Crée le graph LangGraph pour l'emergency agent
    """
    print("[EMERGENCY] Création du graph LangGraph...")

    workflow = StateGraph(EmergencyState)

    # Ajouter les nœuds
    workflow.add_node("assess", assess_severity)
    workflow.add_node("notify", notify_emergency_contacts)
    workflow.add_node("log", log_emergency)
    workflow.add_node("guidance", provide_immediate_guidance)
    workflow.add_node("create_response", create_final_response)

    # Flow séquentiel
    workflow.set_entry_point("assess")
    workflow.add_edge("assess", "notify")
    workflow.add_edge("notify", "log")
    workflow.add_edge("log", "guidance")
    workflow.add_edge("guidance", "create_response")
    workflow.add_edge("create_response", END)

    return workflow.compile()


# Créer l'instance du graph (singleton)
emergency_agent = create_emergency_graph()

print("[EMERGENCY] Graph LangGraph créé avec succès!")
