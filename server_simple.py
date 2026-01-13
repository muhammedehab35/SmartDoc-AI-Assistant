#!/usr/bin/env python3
"""
Serveur API simple pour tester le frontend
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Configuration paths
sys.path.insert(0, 'shared')
sys.path.insert(0, 'lambda/orchestrator')

# Mock AWS avant imports
os.environ['AWS_REGION'] = 'us-east-1'
import unittest.mock as mock
mock_dynamodb = mock.MagicMock()
with mock.patch('boto3.resource', return_value=mock_dynamodb):
    import database

# Mock Database
class MockDB:
    def get_user(self, user_id):
        return {
            'user_id': user_id,
            'name': 'Muhammad Ehab',
            'age': 25,
            'phone': '+33123456789',
            'medical_conditions': [],
            'emergency_contacts': ['+33987654321']
        }

    def get_user_medications(self, user_id, active_only=True):
        return []

    def get_user_appointments(self, user_id, limit=10):
        return []

    def save_conversation(self, data):
        return True

class MockLambda:
    def invoke_agent(self, name, payload):
        return {'body': '{"response": "Mock agent response"}'}

# Appliquer mocks
import database
import utils
database.db = MockDB()
utils.lambda_helper = MockLambda()

# Importer orchestrator
from agent import orchestrator
from langchain_core.messages import HumanMessage

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Reduire les logs
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            user_message = data.get('message', '')
            user_id = data.get('userId', 'user_test')

            print(f"\nUser: {user_message}")

            # Appeler orchestrator
            try:
                initial_state = {
                    "messages": [HumanMessage(content=user_message)],
                    "user_id": user_id,
                    "intent": "",
                    "context": {},
                    "next_agent": "",
                    "final_response": "",
                    "error": ""
                }

                result = orchestrator.invoke(initial_state)

                response_data = {
                    'response': result['final_response'],
                    'intent': result['intent'],
                    'agent': result['next_agent'],
                    'success': True
                }

                print(f"Intent: {result['intent']}")
                print(f"Agent: {result['next_agent']}")
                print(f"Response: {result['final_response'][:100]}...")

            except Exception as e:
                print(f"Erreur: {str(e)}")
                response_data = {
                    'response': f"Erreur: {str(e)}",
                    'success': False
                }

            # Envoyer reponse
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=3000):
    server = HTTPServer(('localhost', port), APIHandler)
    print("="*70)
    print("SERVEUR API SMARTDOC ASSISTANT")
    print("="*70)
    print(f"\nServeur demarre sur: http://localhost:{port}")
    print(f"Endpoint: POST http://localhost:{port}/chat")
    print("\nPour tester le frontend:")
    print(f"  1. Ouvrir: frontend/index.html")
    print(f"  2. Configurer URL API: http://localhost:{port}")
    print(f"  3. User ID: user_muhammad_ehab")
    print("\nCtrl+C pour arreter")
    print("="*70 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServeur arrete.")
        server.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
