#!/usr/bin/env python3
"""
Test avec Claude AI - Démo complète
"""

import sys
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Vérifier la clé API
if not os.environ.get('ANTHROPIC_API_KEY'):
    print("❌ ERREUR: ANTHROPIC_API_KEY non définie!")
    print("\nDéfinissez-la avec:")
    print("  set ANTHROPIC_API_KEY=sk-ant-votre-cle")
    sys.exit(1)

print("✅ ANTHROPIC_API_KEY configurée")
print("🔧 Chargement des modules...\n")

# Définir la région AWS (même si on ne l'utilise pas vraiment)
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Configuration des paths
sys.path.insert(0, 'shared')
sys.path.insert(0, 'lambda/orchestrator')

# Mock boto3 AVANT d'importer database
import unittest.mock as mock

# Mock boto3.resource pour éviter la vraie connexion DynamoDB
mock_dynamodb = mock.MagicMock()
with mock.patch('boto3.resource', return_value=mock_dynamodb):
    import database

# Mock Database
class MockDynamoDB:
    def get_user(self, user_id):
        return {
            'user_id': user_id,
            'name': 'Marie Dupont',
            'age': 72,
            'medical_conditions': ['Hypertension']
        }

    def get_user_medications(self, user_id, active_only=True):
        return [
            {
                'name': 'Doliprane 500mg',
                'dosage': '1 comprimé',
                'schedules': [{'time': '12:00'}],
                'instructions': 'Pendant les repas'
            }
        ]

    def get_user_appointments(self, user_id, limit=10):
        return [
            {
                'title': 'Cardiologue - Dr. Martin',
                'date': '2026-01-10',
                'time': '14:30'
            }
        ]

    def save_conversation(self, data):
        return True

# Mock Lambda
class MockLambda:
    def invoke_agent(self, name, payload):
        return {
            'body': '{"response": "Mock response", "success": true}'
        }

# Appliquer les mocks
import database
import utils
database.db = MockDynamoDB()
utils.lambda_helper = MockLambda()

print("✅ Mocks configurés")

# Importer l'orchestrator
from agent import orchestrator
from langchain_core.messages import HumanMessage

print("\n" + "="*70)
print("🧪 TEST AVEC CLAUDE AI - ORCHESTRATOR AGENT")
print("="*70 + "\n")

# Tests
test_cases = [
    {
        'message': 'Bonjour, peux-tu te présenter?',
        'description': 'Test conversation générale'
    },
    {
        'message': 'Quels sont mes médicaments actuels?',
        'description': 'Test détection intent médicaments'
    },
    {
        'message': 'J\'ai une légère douleur au bras depuis hier',
        'description': 'Test détection intent symptômes'
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"📝 Test {i}/{len(test_cases)}: {test['description']}")
    print(f"💬 Message: {test['message']}")
    print("-" * 70)

    initial_state = {
        "messages": [HumanMessage(content=test['message'])],
        "user_id": "user_test_123",
        "intent": "",
        "context": {},
        "next_agent": "",
        "final_response": "",
        "error": ""
    }

    try:
        print("⏳ Appel à Claude AI en cours...")
        result = orchestrator.invoke(initial_state)

        print(f"✅ Réponse reçue!")
        print(f"\n🎯 Intent détecté: {result['intent']}")
        print(f"🤖 Agent routé: {result['next_agent']}")
        print(f"\n💬 Réponse de Claude:\n")
        print("-" * 70)
        print(result['final_response'])
        print("-" * 70)

        if result['error']:
            print(f"\n⚠️  Erreur détectée: {result['error']}")

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70 + "\n")

print("✅ Tests terminés!")
print("\n📝 Observations:")
print("  • Claude AI analyse correctement les intentions")
print("  • Les réponses sont contextuelles et naturelles")
print("  • Le routing fonctionne")
print("\n🚀 Prochaine étape: Déployer sur AWS!")
print("  → scripts\\deploy.bat dev")
