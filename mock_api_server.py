#!/usr/bin/env python3
"""
Serveur API Mock pour tester le frontend localement
Lance un serveur HTTP sur localhost:8080 qui simule l'API SmartDoc
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
from datetime import datetime

class MockAPIHandler(BaseHTTPRequestHandler):
    """Handler pour les requêtes HTTP"""

    def log_message(self, format, *args):
        """Override pour un meilleur logging"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/chat':
            try:
                # Lire le body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request = json.loads(post_data.decode('utf-8'))

                user_id = request.get('user_id', 'unknown')
                message = request.get('message', '').lower()

                print(f"\n📨 Requête de {user_id}: {message[:50]}...")

                # Simuler un délai (comme une vraie API)
                time.sleep(1)

                # Générer la réponse selon le message
                response = self.generate_response(message, user_id)

                print(f"✅ Intent: {response['intent']}, Agent: {response['agent_used']}")

                # Envoyer la réponse
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
                self.send_error(500, f"Erreur serveur: {str(e)}")

        else:
            self.send_error(404, "Endpoint non trouvé")

    def generate_response(self, message, user_id):
        """Génère une réponse mockée basée sur le message"""

        # Médicaments
        if any(word in message for word in ['médicament', 'medication', 'traitement', 'pilule']):
            return {
                'response': '''💊 Vos médicaments actuels:

• Doliprane 500mg
  📏 Dose: 1 comprimé
  🕐 Horaires: 12:00 et 20:00
  ℹ️  À prendre pendant les repas

• Aspégic 100mg
  📏 Dose: 1 sachet
  🕐 Horaires: 08:00
  ℹ️  Avec un grand verre d'eau

⏰ Prochain médicament:
Doliprane dans 2 heures (12:00)

Je vous rappellerai quand ce sera l'heure! 😊''',
                'intent': 'medication',
                'agent_used': 'medication-agent',
                'success': True
            }

        # Symptômes
        elif any(word in message for word in ['mal', 'douleur', 'symptom', 'tête', 'fièvre', 'fatigue']):
            return {
                'response': '''🌡️ Analyse de vos symptômes

Vous mentionnez: mal de tête

📊 Gravité évaluée: MODÉRÉ

💡 Mes recommandations:
  • Reposez-vous dans un endroit calme et sombre
  • Buvez un grand verre d'eau
  • Vous pouvez prendre du Doliprane 500mg
  • Surveillez l'évolution

⚠️  Consultez un médecin si:
  • La douleur persiste plus de 4 heures
  • Elle s'aggrave
  • Vous avez de la fièvre

📅 Votre prochain rendez-vous:
Cardiologue - Dr. Martin demain à 14:30

💙 Prenez soin de vous!''',
                'intent': 'symptom',
                'agent_used': 'symptom-agent',
                'success': True
            }

        # Rendez-vous
        elif any(word in message for word in ['rendez-vous', 'rdv', 'appointment', 'docteur', 'médecin']):
            return {
                'response': '''📅 Vos prochains rendez-vous:

🏥 Cardiologue - Dr. Martin
📆 Demain, 10 janvier 2026
🕐 14:30
📍 Hôpital Saint-Louis, 3ème étage

📝 Notes: Consultation de suivi pour l'hypertension

📋 Ensuite:
• Diabétologue - Dr. Rousseau le 17 janvier à 10:00

Je vous rappellerai la veille de chaque rendez-vous! 😊''',
                'intent': 'appointment',
                'agent_used': 'symptom-agent',
                'success': True
            }

        # Urgence
        elif any(word in message for word in ['aide', 'urgence', 'tombé', 'chute', 'danger', 'au secours']):
            return {
                'response': '''🚨 URGENCE DÉTECTÉE

{user_name}, restez calme. Je suis là pour vous aider.

📋 CE QUE VOUS DEVEZ FAIRE IMMÉDIATEMENT:

1. 🛑 Ne bougez pas si vous avez mal
2. 📞 Appelez le 15 (SAMU) si douleur intense
3. 🗣️  Parlez-moi, je reste avec vous
4. 👥 De l'aide arrive

✅ ACTIONS EFFECTUÉES:
  ✓ SMS envoyé à Sophie (Fille) - +33698765432
  ✓ Urgence enregistrée dans le système
  ✓ Localisation notée

⚠️  NUMÉROS D'URGENCE:
  📞 SAMU: 15
  📞 Pompiers: 18
  📞 Urgences: 112

💙 Vous n'êtes pas seul(e)
Je reste en contact avec vous'''.format(user_name=user_id),
                'intent': 'emergency',
                'agent_used': 'emergency-agent',
                'success': True
            }

        # Conversation générale
        else:
            return {
                'response': '''Bonjour! 😊

Je suis SmartDoc, votre assistant santé personnel.

Je peux vous aider avec:

💊 **Médicaments**
   • Liste de vos médicaments
   • Rappels de prise
   • Informations sur les interactions

🌡️  **Symptômes**
   • Analyse de vos symptômes
   • Recommandations
   • Quand consulter un médecin

📅 **Rendez-vous**
   • Prochains rendez-vous
   • Détails des consultations
   • Rappels automatiques

🚨 **Urgences**
   • Aide immédiate
   • Alerte de vos proches
   • Guidance en temps réel

Comment puis-je vous aider aujourd'hui?''',
                'intent': 'general',
                'agent_used': 'general-response',
                'success': True
            }

def run_server(port=8080):
    """Démarre le serveur mock"""
    server = HTTPServer(('localhost', port), MockAPIHandler)

    print('''
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🏥 SmartDoc Assistant - Mock API Server                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

✅ Serveur démarré avec succès!

🌐 URL: http://localhost:{port}

📝 Configuration Frontend:
   1. Ouvrez frontend/index.html dans votre navigateur
   2. Cliquez sur ⚙️ (configuration)
   3. Entrez:
      - URL API: http://localhost:{port}
      - User ID: user_test_123
   4. Sauvegardez

🧪 Testez avec curl:
   curl -X POST http://localhost:{port}/chat \\
     -H "Content-Type: application/json" \\
     -d '{{"user_id":"test","message":"Bonjour"}}'

💬 Exemples de messages à tester:
   • "Quels sont mes médicaments?"
   • "J'ai mal à la tête"
   • "Quand est mon rendez-vous?"
   • "Aide! Je suis tombé"

⌨️  Appuyez sur Ctrl+C pour arrêter le serveur
──────────────────────────────────────────────────────────────
'''.format(port=port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Arrêt du serveur...')
        server.shutdown()
        print('✅ Serveur arrêté proprement\n')

if __name__ == '__main__':
    import sys

    # Port par défaut ou depuis argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    run_server(port)
