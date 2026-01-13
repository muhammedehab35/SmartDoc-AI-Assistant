# 🧪 Guide de Test Local - SmartDoc Assistant

Ce guide vous permet de tester le projet **localement** sans déployer sur AWS.

---

## 🎯 Options de Test Local

### Option 1: Test des Agents Individuellement (Recommandé)
### Option 2: Mock AWS avec LocalStack
### Option 3: Frontend avec API Mock

---

## ✅ Option 1: Tester les Agents Individuellement

### Prérequis

```bash
# Installer Python 3.11+
python --version

# Installer les dépendances
cd smartdoc-assistant
pip install -r shared/requirements.txt
pip install -r lambda/orchestrator/requirements.txt
```

### 1. Configurer les variables d'environnement

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-votre-cle"
$env:AWS_REGION="us-east-1"
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="sk-ant-votre-cle"
export AWS_REGION="us-east-1"
```

### 2. Créer un fichier de test

Créez `test_local.py` à la racine:

```python
#!/usr/bin/env python3
"""
Script de test local des agents SmartDoc
"""

import sys
import os
import json

# Ajouter les paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda', 'orchestrator'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda', 'medication-agent'))

# Mock DynamoDB pour tests locaux
class MockDynamoDB:
    def get_user(self, user_id):
        return {
            'user_id': user_id,
            'name': 'Marie Test',
            'age': 72,
            'phone': '+33612345678',
            'emergency_contacts': [
                {'name': 'Sophie', 'relation': 'Fille', 'phone': '+33698765432'}
            ],
            'medical_conditions': ['Hypertension']
        }

    def get_user_medications(self, user_id, active_only=True):
        return [
            {
                'medication_id': 'med_001',
                'user_id': user_id,
                'name': 'Doliprane 500mg',
                'dosage': '1 comprimé',
                'frequency': '2x/jour',
                'schedules': [
                    {'time': '12:00', 'hour': 12},
                    {'time': '20:00', 'hour': 20}
                ],
                'instructions': 'À prendre pendant les repas',
                'active': True
            }
        ]

    def get_user_appointments(self, user_id, limit=10):
        return [
            {
                'appointment_id': 'appt_001',
                'user_id': user_id,
                'title': 'Cardiologue - Dr. Martin',
                'date': '2026-01-10',
                'time': '14:30',
                'location': 'Hôpital Saint-Louis'
            }
        ]

    def save_conversation(self, data):
        print(f"[MOCK] Conversation sauvegardée: {data['conversation_id']}")
        return True

# Remplacer le vrai DB par le mock
import database
database.db = MockDynamoDB()

# Tester Orchestrator
print("="*60)
print("🧪 TEST ORCHESTRATOR AGENT")
print("="*60)

from agent import orchestrator
from langchain_core.messages import HumanMessage

test_messages = [
    "Quels sont mes médicaments?",
    "J'ai mal à la tête",
    "Quand est mon prochain rendez-vous?",
    "Bonjour, comment ça va?"
]

for message in test_messages:
    print(f"\n📨 User: {message}")

    initial_state = {
        "messages": [HumanMessage(content=message)],
        "user_id": "user_test_123",
        "intent": "",
        "context": {},
        "next_agent": "",
        "final_response": "",
        "error": ""
    }

    try:
        result = orchestrator.invoke(initial_state)

        print(f"🎯 Intent: {result['intent']}")
        print(f"🤖 Agent: {result['next_agent']}")
        print(f"💬 Response: {result['final_response'][:200]}...")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

print("\n" + "="*60)
print("✅ Tests terminés!")
print("="*60)
```

### 3. Exécuter le test

```bash
python test_local.py
```

**Résultat attendu:**
```
============================================================
🧪 TEST ORCHESTRATOR AGENT
============================================================

📨 User: Quels sont mes médicaments?
[ORCHESTRATOR] Analyse de l'intention...
[ORCHESTRATOR] Intent détecté: medication
[ORCHESTRATOR] Chargement du contexte utilisateur...
🎯 Intent: medication
🤖 Agent: general-response
💬 Response: Vous prenez actuellement Doliprane 500mg...

📨 User: J'ai mal à la tête
[ORCHESTRATOR] Analyse de l'intention...
[ORCHESTRATOR] Intent détecté: symptom
🎯 Intent: symptom
🤖 Agent: general-response
💬 Response: Je comprends que vous avez mal à la tête...

============================================================
✅ Tests terminés!
============================================================
```

---

## ✅ Option 2: Tester un Agent Spécifique

### Test Medication Agent

Créez `test_medication_agent.py`:

```python
#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda', 'medication-agent'))

# Mock DB (comme ci-dessus)
class MockDynamoDB:
    def get_user_medications(self, user_id, active_only=True):
        return [
            {
                'medication_id': 'med_001',
                'name': 'Doliprane 500mg',
                'dosage': '1 comprimé',
                'schedules': [{'time': '12:00', 'hour': 12}],
                'instructions': 'Avec repas'
            }
        ]

import database
database.db = MockDynamoDB()

from agent import medication_agent

print("🧪 TEST MEDICATION AGENT\n")

test_state = {
    "user_id": "user_test",
    "message": "Quand dois-je prendre mon prochain médicament?",
    "context": {
        "user_profile": {"name": "Marie"}
    },
    "medications": [],
    "action": "",
    "response": "",
    "error": ""
}

result = medication_agent.invoke(test_state)

print(f"Action: {result['action']}")
print(f"Médicaments: {len(result['medications'])}")
print(f"\nRéponse:\n{result['response']}")
```

```bash
python test_medication_agent.py
```

---

## ✅ Option 3: Frontend avec API Mock

### 1. Créer un serveur mock local

Créez `mock_api_server.py`:

```python
#!/usr/bin/env python3
"""
Serveur API Mock pour tester le frontend localement
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

class MockAPIHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST /chat"""
        if self.path == '/chat':
            # Lire le body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))

            user_id = request.get('user_id')
            message = request.get('message', '').lower()

            # Simuler un délai
            time.sleep(1)

            # Réponses mockées basées sur le message
            if 'médicament' in message or 'medication' in message:
                response = {
                    'response': '''💊 Vos médicaments:

• Doliprane 500mg - 2x/jour (12:00 et 20:00)
• Aspégic 100mg - 1x/jour (08:00)

⏰ Prochain: Doliprane à 12:00 (dans 2 heures)

Je vous rappellerai! 😊''',
                    'intent': 'medication',
                    'agent_used': 'medication-agent',
                    'success': True
                }

            elif 'mal' in message or 'symptom' in message or 'tête' in message:
                response = {
                    'response': '''🌡️ Symptômes analysés

Vous mentionnez un mal de tête.

💡 Mes recommandations:
  • Reposez-vous dans un endroit calme
  • Buvez un verre d'eau
  • Vous pouvez prendre du Doliprane
  • Si persiste > 4h, consultez un médecin

💙 Prenez soin de vous!''',
                    'intent': 'symptom',
                    'agent_used': 'symptom-agent',
                    'success': True
                }

            elif 'rendez-vous' in message or 'rdv' in message or 'appointment' in message:
                response = {
                    'response': '''📅 Votre prochain rendez-vous:

🏥 Cardiologue - Dr. Martin
📆 Vendredi 10 janvier 2026
🕐 14:30
📍 Hôpital Saint-Louis, 3ème étage

Je vous rappellerai la veille! 😊''',
                    'intent': 'appointment',
                    'agent_used': 'symptom-agent',
                    'success': True
                }

            elif 'aide' in message or 'urgence' in message or 'tombé' in message:
                response = {
                    'response': '''🚨 URGENCE DÉTECTÉE

📋 CE QUE VOUS DEVEZ FAIRE:
1. Restez calme
2. Ne bougez pas si vous avez mal
3. Appelez le 15 si douleur intense
4. Vos proches sont prévenus

✅ Actions effectuées:
  ✓ SMS envoyé à Sophie (Fille)
  ✓ Urgence enregistrée

💙 Vous n'êtes pas seul(e)
📞 Je suis toujours disponible''',
                    'intent': 'emergency',
                    'agent_used': 'emergency-agent',
                    'success': True
                }

            else:
                response = {
                    'response': f'''Bonjour! 😊

Je suis SmartDoc, votre assistant santé.

Je peux vous aider avec:
💊 Vos médicaments
🌡️ Vos symptômes
📅 Vos rendez-vous
🚨 Les urgences

Comment puis-je vous aider aujourd'hui?''',
                    'intent': 'general',
                    'agent_used': 'general-response',
                    'success': True
                }

            # Envoyer la réponse
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        else:
            self.send_error(404)

if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('localhost', PORT), MockAPIHandler)

    print(f'''
╔══════════════════════════════════════════════════════════╗
║  🏥 SmartDoc Mock API Server                            ║
╚══════════════════════════════════════════════════════════╝

✅ Serveur démarré sur: http://localhost:{PORT}

📝 Configuration Frontend:
   URL API: http://localhost:{PORT}
   User ID: user_test_123

🧪 Testez avec:
   curl -X POST http://localhost:{PORT}/chat \\
     -H "Content-Type: application/json" \\
     -d '{{"user_id":"test","message":"Bonjour"}}'

Appuyez sur Ctrl+C pour arrêter
''')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Serveur arrêté')
        server.shutdown()
```

### 2. Lancer le serveur mock

```bash
python mock_api_server.py
```

### 3. Configurer le frontend

1. Ouvrir `frontend/index.html` dans un navigateur
2. Cliquer sur ⚙️ (configuration)
3. Entrer:
   - **URL API**: `http://localhost:8080`
   - **User ID**: `user_test_123`
4. Sauvegarder

### 4. Tester!

Tapez dans le chat:
- "Quels sont mes médicaments?"
- "J'ai mal à la tête"
- "Quand est mon rendez-vous?"
- "Aide! Je suis tombé"

---

## ✅ Option 4: Test avec AWS SAM Local (Avancé)

### Installer AWS SAM CLI

```bash
# Windows (avec Chocolatey)
choco install aws-sam-cli

# Mac
brew install aws-sam-cli

# Linux
pip install aws-sam-cli
```

### Créer template.yaml pour SAM

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 60
    Runtime: python3.11
    Environment:
      Variables:
        ANTHROPIC_API_KEY: !Ref AnthropicApiKey

Parameters:
  AnthropicApiKey:
    Type: String
    NoEcho: true

Resources:
  OrchestratorFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda/orchestrator/
      Handler: handler.lambda_handler
      Events:
        ChatApi:
          Type: Api
          Properties:
            Path: /chat
            Method: post
```

### Lancer localement avec SAM

```bash
# Démarrer l'API locale
sam local start-api --parameter-overrides "AnthropicApiKey=sk-ant-your-key"

# L'API sera disponible sur http://localhost:3000
```

---

## 🐛 Dépannage Tests Locaux

### Erreur: "Module langgraph not found"

```bash
pip install langgraph langchain langchain-anthropic
```

### Erreur: "ANTHROPIC_API_KEY not set"

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-your-key

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-your-key
```

### Le mock server ne démarre pas

Vérifier que le port 8080 est libre:
```bash
# Windows
netstat -ano | findstr :8080

# Linux/Mac
lsof -i :8080
```

### CORS errors dans le navigateur

Le mock server inclut déjà les headers CORS. Si problème:
1. Ouvrir Chrome avec: `chrome.exe --disable-web-security --user-data-dir=C:\temp`
2. Ou utiliser une extension CORS

---

## 📊 Résumé des Options

| Option | Difficulté | Besoin AWS | Besoin API Key | Recommandé pour |
|--------|------------|------------|----------------|-----------------|
| **Agents individuels** | ⭐ Facile | ❌ Non | ✅ Oui | Tester la logique |
| **Frontend Mock** | ⭐⭐ Moyen | ❌ Non | ❌ Non | Tester l'UI |
| **SAM Local** | ⭐⭐⭐ Avancé | ✅ Oui | ✅ Oui | Test complet |

---

## ✅ Checklist Tests Locaux

Avant de déployer:

- [ ] Tests agents individuels passent
- [ ] Frontend fonctionne avec mock API
- [ ] Clé API Anthropic valide
- [ ] Pas d'erreurs dans la console
- [ ] Réponses cohérentes et correctes
- [ ] Temps de réponse < 5 secondes
- [ ] Gestion d'erreurs fonctionne

---

## 🚀 Prochaine Étape

Une fois les tests locaux OK, déployez sur AWS:

```bash
scripts\deploy.bat dev
```

---

**Bon test! 🧪**
