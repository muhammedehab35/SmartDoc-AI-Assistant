"""
Lambda Handler pour le Medication Agent
"""

import json
import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from agent import medication_agent
from utils import create_lambda_response


def lambda_handler(event, context):
    """
    Point d'entrée Lambda pour le medication agent

    Event structure:
    {
        "body": {
            "user_id": "user_123",
            "message": "Quels sont mes médicaments?",
            "context": {...}
        }
    }
    """
    print("[MEDICATION HANDLER] Début du traitement")

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

        print(f"[MEDICATION HANDLER] User: {user_id}, Message: {message}")

        # État initial
        initial_state = {
            "user_id": user_id,
            "message": message,
            "context": context,
            "medications": [],
            "action": "",
            "response": "",
            "error": ""
        }

        # Exécuter le graph LangGraph
        print("[MEDICATION HANDLER] Exécution du graph...")
        result = medication_agent.invoke(initial_state)

        print(f"[MEDICATION HANDLER] Action: {result['action']}, Médicaments: {len(result['medications'])}")

        # Réponse
        response_body = {
            'response': result["response"],
            'action': result["action"],
            'medications_count': len(result["medications"]),
            'success': True
        }

        if result.get("error"):
            response_body['error'] = result["error"]

        return create_lambda_response(200, response_body)

    except Exception as e:
        print(f"[MEDICATION HANDLER] Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

        return create_lambda_response(500, {
            'error': 'Erreur interne',
            'details': str(e),
            'success': False
        })


# Pour tests locaux
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "user_id": "user_test_123",
            "message": "Quand dois-je prendre mon prochain médicament?",
            "context": {
                "user_profile": {
                    "name": "Marie"
                }
            }
        })
    }

    result = lambda_handler(test_event, None)
    print("\n=== RÉSULTAT DU TEST ===")
    print(json.dumps(json.loads(result['body']), indent=2, ensure_ascii=False))
