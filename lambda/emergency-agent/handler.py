"""
Lambda Handler pour l'Emergency Agent
"""

import json
import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from agent import emergency_agent
from utils import create_lambda_response


def lambda_handler(event, context):
    """
    Point d'entrée Lambda pour l'emergency agent

    Event structure:
    {
        "body": {
            "user_id": "user_123",
            "message": "Aide! Je suis tombé!",
            "context": {...}
        }
    }
    """
    print("[EMERGENCY HANDLER] ⚠️ URGENCE DÉTECTÉE")

    try:
        # Parser la requête
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        user_id = body.get('user_id')
        message = body.get('message')
        context = body.get('context', {})

        # Validation
        if not user_id or not message:
            return create_lambda_response(400, {'error': 'user_id et message requis'})

        print(f"[EMERGENCY HANDLER] User: {user_id}")
        print(f"[EMERGENCY HANDLER] Message: {message}")

        # État initial
        initial_state = {
            "user_id": user_id,
            "message": message,
            "context": context,
            "severity": "",
            "emergency_type": "",
            "actions_taken": [],
            "contacts_notified": [],
            "guidance": "",
            "response": "",
            "error": ""
        }

        # Exécuter le graph LangGraph
        print("[EMERGENCY HANDLER] Exécution du graph d'urgence...")
        result = emergency_agent.invoke(initial_state)

        print(f"[EMERGENCY HANDLER] Gravité: {result['severity']}")
        print(f"[EMERGENCY HANDLER] Type: {result['emergency_type']}")
        print(f"[EMERGENCY HANDLER] Actions: {len(result['actions_taken'])}")
        print(f"[EMERGENCY HANDLER] Contacts notifiés: {len(result['contacts_notified'])}")

        # Réponse
        response_body = {
            'response': result["response"],
            'severity': result["severity"],
            'emergency_type': result["emergency_type"],
            'actions_taken': result["actions_taken"],
            'contacts_notified_count': len(result["contacts_notified"]),
            'success': True
        }

        if result.get("error"):
            response_body['error'] = result["error"]

        # Log important pour urgences
        print("[EMERGENCY HANDLER] ✅ Urgence traitée avec succès")

        return create_lambda_response(200, response_body)

    except Exception as e:
        print(f"[EMERGENCY HANDLER] ❌ ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()

        # En cas d'erreur, retourner quand même une réponse d'urgence
        emergency_response = {
            'response': """
🚨 URGENCE DÉTECTÉE

Appelez immédiatement le 15 (SAMU) si vous êtes en danger.

Je rencontre une difficulté technique mais votre sécurité est primordiale.

📞 Numéros d'urgence:
• SAMU: 15
• Pompiers: 18
• Urgences: 112
            """,
            'severity': 'critical',
            'error': str(e),
            'success': False
        }

        return create_lambda_response(500, emergency_response)


# Pour tests locaux
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "user_id": "user_test_123",
            "message": "Aide! Je suis tombé dans la salle de bain!",
            "context": {
                "user_profile": {
                    "name": "Jean",
                    "phone": "+33612345678",
                    "emergency_contacts": [
                        {
                            "name": "Sophie",
                            "relation": "Fille",
                            "phone": "+33698765432"
                        }
                    ]
                }
            }
        })
    }

    result = lambda_handler(test_event, None)
    print("\n=== RÉSULTAT DU TEST ===")
    print(json.dumps(json.loads(result['body']), indent=2, ensure_ascii=False))
