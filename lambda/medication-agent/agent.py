"""
Medication Agent - Gestion des médicaments avec LangGraph
"""

import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from typing import TypedDict, List, Dict, Any
from datetime import datetime, timedelta

from database import db
from utils import sns_helper, get_next_medication_time, format_datetime


# ===== ÉTAT DE L'AGENT =====

class MedicationState(TypedDict):
    """État du medication agent"""
    user_id: str
    message: str
    context: dict
    medications: List[Dict]
    action: str  # "info", "reminder", "interaction_check", "history"
    response: str
    error: str


# ===== INITIALISATION LLM =====

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3,
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)


# ===== FONCTIONS UTILITAIRES =====

def check_medication_time(medications: List[Dict]) -> List[Dict]:
    """Vérifie si c'est l'heure d'un médicament"""
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    due_meds = []
    for med in medications:
        for schedule in med.get('schedules', []):
            schedule_time = schedule.get('time', '00:00')
            hour, minute = map(int, schedule_time.split(':'))

            # Si dans la prochaine heure
            time_diff = (hour * 60 + minute) - (current_hour * 60 + current_minute)
            if 0 <= time_diff <= 60:
                due_meds.append({
                    'name': med['name'],
                    'dosage': med['dosage'],
                    'time': schedule_time,
                    'instructions': med.get('instructions', ''),
                    'minutes_until': time_diff
                })

    return due_meds


# ===== NŒUDS DU GRAPH =====

def determine_action(state: MedicationState) -> MedicationState:
    """
    Nœud 1: Détermine quelle action effectuer
    """
    print("[MEDICATION] Détermination de l'action...")

    message = state["message"].lower()

    # Mots-clés pour chaque action
    if any(word in message for word in ["rappel", "quand", "heure", "prochain", "prendre"]):
        state["action"] = "reminder"
    elif any(word in message for word in ["interaction", "ensemble", "danger", "mélanger"]):
        state["action"] = "interaction_check"
    elif any(word in message for word in ["historique", "pris", "oublié", "hier"]):
        state["action"] = "history"
    else:
        state["action"] = "info"

    print(f"[MEDICATION] Action déterminée: {state['action']}")

    return state


def load_medications(state: MedicationState) -> MedicationState:
    """
    Nœud 2: Charge les médicaments de l'utilisateur
    """
    print("[MEDICATION] Chargement des médicaments...")

    try:
        medications = db.get_user_medications(state["user_id"], active_only=True)
        state["medications"] = medications
        print(f"[MEDICATION] {len(medications)} médicaments chargés")
    except Exception as e:
        print(f"[MEDICATION] Erreur chargement médicaments: {e}")
        state["medications"] = []
        state["error"] = str(e)

    return state


def provide_medication_info(state: MedicationState) -> MedicationState:
    """
    Nœud 3: Fournit des informations sur les médicaments
    """
    print("[MEDICATION] Génération d'informations médicaments...")

    medications = state["medications"]
    message = state["message"]
    user_name = state["context"].get("user_profile", {}).get("name", "")

    if not medications:
        state["response"] = f"{user_name}, vous n'avez pas de médicaments enregistrés actuellement. Voulez-vous que je vous aide à en ajouter?"
        return state

    # Construire le contexte des médicaments
    meds_context = []
    for med in medications:
        schedules_str = ", ".join([s.get('time', '') for s in med.get('schedules', [])])
        meds_context.append(
            f"- {med['name']}: {med['dosage']}, à prendre à {schedules_str}. {med.get('instructions', '')}"
        )

    meds_text = "\n".join(meds_context)

    system_prompt = f"""
Tu es un assistant médical bienveillant pour {user_name}, une personne âgée.

Médicaments actuels:
{meds_text}

Question de l'utilisateur: {message}

Réponds à la question sur les médicaments de manière:
- Simple et très claire (phrases courtes)
- Sans jargon médical complexe
- Rassurante et encourageante
- En rappelant de toujours consulter un médecin pour tout doute

Si l'utilisateur demande ses médicaments, liste-les de façon claire avec emojis.
Utilise des emojis appropriés: 💊 pour médicament, ⏰ pour horaire, ℹ️ pour info.
"""

    try:
        response = llm.invoke([SystemMessage(content=system_prompt)])
        state["response"] = response.content
        print("[MEDICATION] Réponse générée avec succès")

    except Exception as e:
        print(f"[MEDICATION] Erreur génération réponse: {e}")
        state["response"] = f"Voici vos {len(medications)} médicaments:\n\n" + meds_text
        state["error"] = str(e)

    return state


def check_next_dose(state: MedicationState) -> MedicationState:
    """
    Nœud 4: Vérifie le prochain médicament à prendre
    """
    print("[MEDICATION] Vérification prochaine dose...")

    medications = state["medications"]
    user_name = state["context"].get("user_profile", {}).get("name", "")

    if not medications:
        state["response"] = f"{user_name}, vous n'avez pas de médicaments enregistrés."
        return state

    # Trouver le prochain médicament
    next_meds = []
    now = datetime.now()

    for med in medications:
        for schedule in med.get('schedules', []):
            time_str = schedule.get('time', '00:00')
            hour, minute = map(int, time_str.split(':'))

            scheduled_time = datetime.combine(now.date(), datetime.min.time().replace(hour=hour, minute=minute))

            # Si l'heure est passée, prendre demain
            if scheduled_time <= now:
                scheduled_time += timedelta(days=1)

            minutes_until = int((scheduled_time - now).total_seconds() / 60)

            next_meds.append({
                'name': med['name'],
                'dosage': med['dosage'],
                'time': time_str,
                'instructions': med.get('instructions', ''),
                'minutes_until': minutes_until,
                'scheduled_time': scheduled_time
            })

    # Trier par temps
    next_meds.sort(key=lambda x: x['minutes_until'])

    if next_meds:
        next_med = next_meds[0]
        minutes = next_med['minutes_until']
        hours = minutes // 60
        mins = minutes % 60

        if hours > 24:
            days = hours // 24
            time_str = f"dans {days} jour{'s' if days > 1 else ''}"
        elif hours > 0:
            time_str = f"dans {hours}h{mins:02d}"
        else:
            time_str = f"dans {mins} minute{'s' if mins > 1 else ''}"

        response = f"""
⏰ Votre prochain médicament:

💊 {next_med['name']}
📏 Dose: {next_med['dosage']}
🕐 Heure: {next_med['time']}
⏱️ {time_str}

{next_med['instructions']}

Je vous rappellerai quand ce sera l'heure! 😊
"""

        # Ajouter les 2 prochains si disponibles
        if len(next_meds) > 1:
            response += "\n\n📋 Ensuite:\n"
            for med in next_meds[1:3]:
                response += f"• {med['name']} à {med['time']}\n"

    else:
        response = f"Bravo {user_name}! Vous avez pris tous vos médicaments pour aujourd'hui! 🎉"

    state["response"] = response
    print("[MEDICATION] Prochain médicament calculé")

    return state


def check_interactions(state: MedicationState) -> MedicationState:
    """
    Nœud 5: Vérifie les interactions médicamenteuses
    """
    print("[MEDICATION] Vérification des interactions...")

    medications = state["medications"]
    user_name = state["context"].get("user_profile", {}).get("name", "")

    if len(medications) < 2:
        state["response"] = f"{user_name}, vous avez moins de 2 médicaments. Les interactions ne sont généralement pas un problème."
        return state

    med_names = [m['name'] for m in medications]
    meds_text = ", ".join(med_names)

    system_prompt = f"""
Tu es un pharmacien expert mais qui parle simplement.

{user_name} prend actuellement ces médicaments:
{meds_text}

Analyse les interactions potentielles entre ces médicaments.

Réponds de manière:
- Très simple et rassurante
- Sans termes techniques
- Si pas d'interaction majeure connue: rassure
- Si interaction possible: explique simplement et recommande de consulter médecin/pharmacien
- Utilise des emojis appropriés

IMPORTANT: Termine toujours en rappelant de consulter un professionnel de santé pour confirmation.
"""

    try:
        response = llm.invoke([SystemMessage(content=system_prompt)])
        state["response"] = response.content
        print("[MEDICATION] Analyse des interactions terminée")

    except Exception as e:
        print(f"[MEDICATION] Erreur analyse interactions: {e}")
        state["response"] = f"""
Je ne peux pas analyser les interactions pour le moment.

Vos médicaments: {meds_text}

Je vous recommande de consulter votre pharmacien ou médecin pour vérifier qu'il n'y a pas d'interactions.
"""
        state["error"] = str(e)

    return state


def check_history(state: MedicationState) -> MedicationState:
    """
    Nœud 6: Affiche l'historique de prise
    """
    print("[MEDICATION] Consultation historique...")

    # Pour MVP, on affiche juste la liste actuelle
    # Dans une vraie app, on trackrait les prises
    medications = state["medications"]

    response = f"""
📋 Historique de vos médicaments:

Médicaments actifs actuellement: {len(medications)}

"""

    for med in medications:
        schedules = ", ".join([s.get('time', '') for s in med.get('schedules', [])])
        response += f"""
💊 {med['name']}
   Dose: {med['dosage']}
   Horaires: {schedules}
   Depuis: {med.get('start_date', 'Date inconnue')}

"""

    response += "\nℹ️ Pour un historique détaillé des prises, consultez votre médecin ou pharmacien."

    state["response"] = response
    return state


# ===== CONSTRUCTION DU GRAPH LANGGRAPH =====

def create_medication_graph():
    """
    Crée le graph LangGraph pour le medication agent
    """
    print("[MEDICATION] Création du graph LangGraph...")

    workflow = StateGraph(MedicationState)

    # Ajouter les nœuds
    workflow.add_node("determine_action", determine_action)
    workflow.add_node("load_meds", load_medications)
    workflow.add_node("info", provide_medication_info)
    workflow.add_node("reminder", check_next_dose)
    workflow.add_node("interaction", check_interactions)
    workflow.add_node("history", check_history)

    # Point d'entrée
    workflow.set_entry_point("determine_action")
    workflow.add_edge("determine_action", "load_meds")

    # Routing conditionnel basé sur l'action
    def route_action(state: MedicationState) -> str:
        return state["action"]

    workflow.add_conditional_edges(
        "load_meds",
        route_action,
        {
            "info": "info",
            "reminder": "reminder",
            "interaction": "interaction",
            "history": "history"
        }
    )

    # Tous mènent à la fin
    workflow.add_edge("info", END)
    workflow.add_edge("reminder", END)
    workflow.add_edge("interaction", END)
    workflow.add_edge("history", END)

    return workflow.compile()


# Créer l'instance du graph (singleton)
medication_agent = create_medication_graph()

print("[MEDICATION] Graph LangGraph créé avec succès!")
