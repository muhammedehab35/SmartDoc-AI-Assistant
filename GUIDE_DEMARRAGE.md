# 🚀 Guide de Démarrage - SmartDoc Assistant

Par **Muhammad Ehab** - Assistant médical intelligent avec IA

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Démarrage Rapide](#démarrage-rapide)
5. [Utilisation](#utilisation)
6. [Tests](#tests)
7. [Dépannage](#dépannage)

---

## ✅ Prérequis

- **Python 3.9+** installé
- **Clé API Anthropic** (Claude AI)
- **Navigateur web** moderne (Chrome, Firefox, Edge)
- **Windows, macOS ou Linux**

---

## 📦 Installation

### Étape 1: Créer l'environnement virtuel

```bash
# Windows
python -m venv env

# macOS/Linux
python3 -m venv env
```

### Étape 2: Activer l'environnement

```bash
# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

### Étape 3: Installer les dépendances

```bash
pip install -r requirements.txt
```

**Dépendances principales:**
- `anthropic` - SDK Claude AI
- `langchain-anthropic` - Intégration LangChain
- `langgraph` - Orchestration multi-agents
- `python-dotenv` - Gestion variables d'environnement
- `boto3` - SDK AWS (pour déploiement futur)

---

## ⚙️ Configuration

### Étape 1: Copier le fichier de configuration

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### Étape 2: Configurer la clé API

Ouvrez `.env` et modifiez:

```env
# ===== ANTHROPIC (OBLIGATOIRE) =====
ANTHROPIC_API_KEY=sk-ant-api03-VOTRE_VRAIE_CLE_ICI

# ===== POUR TESTS LOCAUX =====
TEST_USER_ID=user_muhammad_ehab
```

**⚠️ IMPORTANT:**
- Ne partagez JAMAIS votre clé API
- Le fichier `.env` est dans `.gitignore` (ne sera pas commité)
- Obtenez votre clé sur: https://console.anthropic.com/

---

## 🚀 Démarrage Rapide

### Méthode 1: Script automatique (Windows)

```bash
start.bat
```

### Méthode 2: Manuel (Windows)

```bash
# Désactiver variable système si elle existe
set ANTHROPIC_API_KEY=

# Démarrer le serveur
env\Scripts\python.exe demo_server.py 3000
```

### Méthode 3: Manuel (macOS/Linux)

```bash
# Désactiver variable système
unset ANTHROPIC_API_KEY

# Démarrer le serveur
./env/bin/python demo_server.py 3000
```

---

## 🎯 Utilisation

### 1. Démarrer le Serveur

Le serveur démarre sur `http://localhost:3000`

Vous verrez:
```
======================================================================
SERVEUR SMARTDOC ASSISTANT - DEMO
======================================================================

Serveur demarre: http://localhost:3000
Endpoint chat: POST http://localhost:3000/chat
Health check: GET http://localhost:3000/health
```

### 2. Ouvrir le Frontend

**Option A: Double-cliquer**
- Ouvrez `frontend/index.html` dans votre navigateur

**Option B: Ligne de commande**
```bash
# Windows
start frontend\index.html

# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html
```

### 3. Configurer l'Application

1. Cliquez sur l'icône **⚙️** (engrenage) en haut à droite
2. Remplissez:
   - **URL API:** `http://localhost:3000`
   - **User ID:** `user_muhammad_ehab`
3. Cliquez sur **Sauvegarder**

### 4. Commencer à Discuter!

Exemples de messages à tester:

**Conversation générale:**
- "Bonjour, comment vas-tu?"
- "Qui es-tu?"
- "Merci pour ton aide"

**Questions médicaments:**
- "Quels médicaments dois-je prendre?"
- "À quelle heure prendre mes médicaments?"
- "Y a-t-il des interactions?"

**Symptômes:**
- "J'ai mal à la tête"
- "Je me sens fatigué depuis ce matin"
- "J'ai de la fièvre"

**Urgences:**
- "Aide! C'est urgent"
- "Urgence médicale"
- "J'ai besoin d'aide immédiatement"

---

## 🧪 Tests

### Test 1: Vérifier la clé API

```bash
# Windows
env\Scripts\python.exe test_api_key.py

# macOS/Linux
unset ANTHROPIC_API_KEY && ./env/bin/python test_api_key.py
```

**Résultat attendu:**
```
SUCCES!
Reponse de Claude: Bonjour
La cle API fonctionne correctement!
```

### Test 2: Test rapide Claude

```bash
# Windows
set ANTHROPIC_API_KEY= && env\Scripts\python.exe test_model_quick.py

# macOS/Linux
unset ANTHROPIC_API_KEY && ./env/bin/python test_model_quick.py
```

**Résultat attendu:**
- Classification d'intentions ✅
- Réponses naturelles ✅

### Test 3: Test LangGraph complet

```bash
# Windows
set ANTHROPIC_API_KEY= && env\Scripts\python.exe test_langgraph.py

# macOS/Linux
unset ANTHROPIC_API_KEY && ./env/bin/python test_langgraph.py
```

**Résultat attendu:**
- Orchestrator fonctionne ✅
- Routing correct ✅
- 3 tests réussis ✅

### Test 4: Test API avec curl

```bash
curl http://localhost:3000/health
```

**Résultat:**
```json
{"status": "ok", "service": "SmartDoc Assistant"}
```

```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour", "userId": "user_test"}'
```

---

## 🐛 Dépannage

### Problème 1: "ANTHROPIC_API_KEY non définie"

**Solution:**
1. Vérifiez que `.env` existe
2. Vérifiez que la clé est correcte dans `.env`
3. Désactivez la variable système:
   ```bash
   # Windows
   set ANTHROPIC_API_KEY=

   # macOS/Linux
   unset ANTHROPIC_API_KEY
   ```

### Problème 2: "Error 401 - invalid x-api-key"

**Solution:**
- Votre clé API est invalide ou expirée
- Obtenez une nouvelle clé sur https://console.anthropic.com/
- Vérifiez qu'il n'y a pas d'espaces avant/après la clé

### Problème 3: "Error 404 - model not found"

**Solution:**
- Le modèle a été mis à jour vers `claude-3-haiku-20240307`
- Ce modèle est compatible avec toutes les clés API

### Problème 4: "Port 3000 already in use"

**Solution:**
1. Tuez le processus existant:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F

   # macOS/Linux
   lsof -ti:3000 | xargs kill
   ```

2. Ou utilisez un autre port:
   ```bash
   python demo_server.py 8080
   ```

### Problème 5: "ModuleNotFoundError"

**Solution:**
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

### Problème 6: Problèmes d'encodage (emojis)

**Solution:**
- Utilisez `demo_server.py` au lieu de `mock_api_server.py`
- `demo_server.py` n'utilise pas d'emojis dans la console

---

## 📊 Architecture du Système

```
SmartDoc Assistant
│
├── Frontend (HTML/CSS/JS)
│   └── Interface utilisateur web
│
├── API Server (Python)
│   └── demo_server.py (serveur local)
│
├── Claude AI (Anthropic)
│   ├── Classification d'intentions
│   └── Génération de réponses
│
└── Future: LangGraph Multi-Agents
    ├── Orchestrator Agent
    ├── Medication Agent
    ├── Symptom Agent
    └── Emergency Agent
```

---

## 📁 Structure du Projet

```
smartdoc-assistant/
├── frontend/              # Interface web
│   ├── index.html        # Page principale
│   ├── app.js            # Logique JavaScript
│   └── styles.css        # Styles
│
├── lambda/               # Agents Lambda (pour AWS)
│   ├── orchestrator/     # Agent routeur
│   ├── medication-agent/ # Agent médicaments
│   ├── symptom-agent/    # Agent symptômes
│   └── emergency-agent/  # Agent urgences
│
├── shared/               # Code partagé
│   ├── database.py       # Helpers DynamoDB
│   ├── utils.py          # Utilitaires
│   └── models.py         # Modèles de données
│
├── tests/                # Tests
│   ├── test_api_key.py
│   ├── test_model_quick.py
│   └── test_langgraph.py
│
├── demo_server.py        # Serveur de démo ⭐
├── start.bat             # Script de démarrage Windows
├── .env                  # Configuration (à créer)
├── .env.example          # Template de config
└── requirements.txt      # Dépendances Python
```

---

## 🎓 Fonctionnalités

### ✅ Actuellement Implémenté

- ✅ Classification automatique des intentions (general, medication, symptom, emergency)
- ✅ Réponses contextuelles adaptées à chaque type de demande
- ✅ Interface web moderne et responsive
- ✅ API REST avec CORS
- ✅ Système de conversation en temps réel

### 🚧 En Développement

- 🚧 Multi-agents avec LangGraph (orchestration complète)
- 🚧 Base de données DynamoDB
- 🚧 Notifications SMS d'urgence
- 🚧 Rappels de médicaments automatiques
- 🚧 Gestion des rendez-vous médicaux

### 🔮 Futur (Déploiement AWS)

- 🔮 Déploiement sur AWS Lambda
- 🔮 API Gateway
- 🔮 DynamoDB pour persistance
- 🔮 SNS pour notifications
- 🔮 EventBridge pour rappels automatiques

---

## 📝 Commandes Utiles

### Gestion de l'environnement

```bash
# Activer l'environnement
env\Scripts\activate          # Windows
source env/bin/activate       # macOS/Linux

# Désactiver l'environnement
deactivate

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Voir les packages installés
pip list
```

### Tests

```bash
# Test complet
python test_langgraph.py

# Test rapide
python test_model_quick.py

# Test API
python test_api_key.py

# Démarrer serveur
python demo_server.py 3000
```

### Nettoyage

```bash
# Supprimer __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +

# Supprimer fichiers .pyc
find . -name "*.pyc" -delete
```

---

## 🆘 Support

### Problèmes courants

1. **Le serveur ne démarre pas**
   - Vérifiez que l'environnement virtuel est activé
   - Vérifiez que `.env` existe et contient la bonne clé

2. **Les réponses sont lentes**
   - Normal avec Claude Haiku (2-5 secondes)
   - Pour plus de rapidité, gardez les messages courts

3. **Frontend ne se connecte pas**
   - Vérifiez que le serveur tourne sur port 3000
   - Vérifiez l'URL dans les paramètres: `http://localhost:3000`

### Documentation

- **Claude AI:** https://docs.anthropic.com/
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **LangChain:** https://python.langchain.com/

---

## 🎉 Félicitations!

Vous avez maintenant un assistant médical intelligent fonctionnel!

**Prochaines étapes:**
1. ✅ Tester toutes les fonctionnalités
2. 📊 Personnaliser les réponses dans `demo_server.py`
3. 🎨 Customiser le frontend dans `frontend/`
4. 🚀 Déployer sur AWS (optionnel)

---

**Créé avec ❤️ par Muhammad Ehab**
**Propulsé par Claude AI (Anthropic)**
