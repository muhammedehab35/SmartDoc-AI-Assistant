#!/usr/bin/env python3
"""
Serveur de demonstration - Simple et fonctionnel
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Verifier API key
if not os.environ.get('ANTHROPIC_API_KEY'):
    print("ERREUR: ANTHROPIC_API_KEY non definie dans .env")
    sys.exit(1)

print("Initialisation du serveur...")

# Import Claude
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

# Initialiser Claude
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3
)

print("Claude AI initialise avec succes!\n")

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Afficher seulement les requetes importantes
        if self.path == '/chat':
            print(f"[{self.command}] {self.path}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'ok', 'service': 'SmartDoc Assistant'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            try:
                # Lire requete
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))

                user_message = data.get('message', '')
                user_id = data.get('userId', 'user_test')

                print(f"\n[USER] {user_message}")

                # Classifier intention
                system_prompt_intent = """
Tu es un classificateur d'intention pour un assistant medical.

Analyse le message et retourne UNE categorie parmi:
- medication: Questions sur medicaments
- symptom: Symptomes de sante, douleurs
- emergency: Urgence, aide, chute
- general: Conversation generale, salutations

Reponds UNIQUEMENT avec le mot-cle.
"""

                intent_response = llm.invoke([
                    SystemMessage(content=system_prompt_intent),
                    HumanMessage(content=user_message)
                ])

                intent = intent_response.content.strip().lower()
                if intent not in ['medication', 'symptom', 'emergency', 'general']:
                    intent = 'general'

                print(f"[INTENT] {intent}")

                # Generer reponse
                system_prompt_response = f"""
Tu es SmartDoc, un assistant medical bienveillant pour Muhammad Ehab.

Intention detectee: {intent}

Reponds de maniere:
- Simple et claire (phrases courtes)
- Chaleureuse et rassurante
- En francais
- Adaptee a l'intention

Si urgence: demande d'appeler le 15
Si symptome: demande de consulter un medecin
Si medication: donne des conseils generaux
Si general: sois chaleureux et disponible
"""

                response_obj = llm.invoke([
                    SystemMessage(content=system_prompt_response),
                    HumanMessage(content=user_message)
                ])

                assistant_response = response_obj.content

                print(f"[CLAUDE] {assistant_response[:100]}...")

                # Envoyer reponse
                response_data = {
                    'response': assistant_response,
                    'intent': intent,
                    'userId': user_id,
                    'success': True
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))

            except Exception as e:
                print(f"[ERREUR] {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    'response': f"Erreur: {str(e)}",
                    'success': False
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=3000):
    server = HTTPServer(('localhost', port), APIHandler)

    print("="*70)
    print("SERVEUR SMARTDOC ASSISTANT - DEMO")
    print("="*70)
    print(f"\nServeur demarre: http://localhost:{port}")
    print(f"Endpoint chat: POST http://localhost:{port}/chat")
    print(f"Health check: GET http://localhost:{port}/health")
    print("\nPOUR TESTER LE FRONTEND:")
    print("  1. Ouvrir: frontend/index.html dans le navigateur")
    print(f"  2. Cliquer sur l'icone parametres (engrenage)")
    print(f"  3. Configurer:")
    print(f"      - URL API: http://localhost:{port}")
    print(f"      - User ID: user_muhammad_ehab")
    print("  4. Sauvegarder et commencer a chatter!")
    print("\nEXEMPLES DE MESSAGES:")
    print("  - Bonjour, comment vas-tu?")
    print("  - Quels medicaments dois-je prendre?")
    print("  - J'ai mal a la tete")
    print("  - Aide! J'ai besoin d'urgence")
    print("\nCtrl+C pour arreter le serveur")
    print("="*70 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServeur arrete. Au revoir!")
        server.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
