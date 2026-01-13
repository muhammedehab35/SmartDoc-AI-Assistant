"""
Lambda Handler pour l'Orchestrator Agent
"""

import json
import sys
import os

# Ajouter le dossier shared au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from langchain_core.messages import HumanMessage
from agent import orchestrator
from utils import create_lambda_response


def lambda_handler(event, context):
    """
    Point d'entrée Lambda pour l'orchestrator

    Event structure:
    {
        "body": {
            "user_id": "user_123",
            "message": "Quels sont mes médicaments?"
        }
    }
    """
    print("[HANDLER] Début du traitement de la requête")
    print(f"[HANDLER] Event: {json.dumps(event)}")

    try:
        # Parser la requête
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        user_id = body.get('user_id')
        message = body.get('message')

        # Validation
        if not user_id:
            print("[HANDLER] Erreur: user_id manquant")
            return create_lambda_response(400, {'error': 'user_id requis'})

        if not message:
            print("[HANDLER] Erreur: message manquant")
            return create_lambda_response(400, {'error': 'message requis'})

        print(f"[HANDLER] User: {user_id}, Message: {message}")

        # État initial pour LangGraph
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "intent": "",
            "context": {},
            "next_agent": "",
            "final_response": "",
            "error": ""
        }

        # Exécuter l'orchestrator LangGraph
        print("[HANDLER] Exécution du graph LangGraph...")
        result = orchestrator.invoke(initial_state)

        print(f"[HANDLER] Graph terminé. Intent: {result['intent']}, Agent: {result['next_agent']}")

        # Préparer la réponse
        response_body = {
            'response': result["final_response"],
            'intent': result["intent"],
            'agent_used': result["next_agent"],
            'success': True
        }

        if result.get("error"):
            response_body['error'] = result["error"]

        print(f"[HANDLER] Réponse: {response_body['response'][:100]}...")

        return create_lambda_response(200, response_body)

    except Exception as e:
        print(f"[HANDLER] Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()

        return create_lambda_response(500, {
            'error': 'Erreur interne du serveur',
            'details': str(e),
            'success': False
        })


# Pour tests locaux
if __name__ == "__main__":
    # Test event
    test_event = {
        "body": json.dumps({
            "user_id": "user_test_123",
            "message": "Bonjour, quels sont mes médicaments?"
        })
    }

    result = lambda_handler(test_event, None)
    print("\n=== RÉSULTAT DU TEST ===")
    print(json.dumps(json.loads(result['body']), indent=2, ensure_ascii=False))
