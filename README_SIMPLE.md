# 🏥 SmartDoc Assistant

Assistant médical intelligent avec IA pour accompagner les personnes âgées.

**Par Muhammad Ehab**

---

## 🚀 Démarrage Ultra-Rapide

### 1. Installation (Une seule fois)

```bash
# Créer environnement virtuel
python -m venv env

# Installer dépendances
env\Scripts\pip install -r requirements.txt

# Configurer la clé API
copy .env.example .env
# Puis éditer .env avec votre clé Anthropic
```

### 2. Démarrer l'Application

**Windows:**
```bash
start.bat
```

**Manuel:**
```bash
set ANTHROPIC_API_KEY=
env\Scripts\python.exe demo_server.py 3000
```

### 3. Utiliser l'Interface Web

1. Ouvrir `frontend/index.html` dans votre navigateur
2. Cliquer sur ⚙️ et configurer:
   - URL API: `http://localhost:3000`
   - User ID: `user_muhammad_ehab`
3. Commencer à discuter!

---

## ✨ Fonctionnalités

- 🤖 **IA Claude** - Classification automatique des intentions
- 💊 **Médicaments** - Questions sur traitements et posologie
- 🏥 **Symptômes** - Analyse et conseils médicaux
- 🚨 **Urgences** - Détection et guidance immédiate
- 💬 **Conversation** - Interface naturelle et bienveillante

---

## 📊 Statut du Système

```
✅ Claude AI (claude-3-haiku-20240307)
✅ Classification d'intentions
✅ Réponses contextuelles
✅ API REST (localhost:3000)
✅ Interface web moderne
```

---

## 🧪 Tests Rapides

```bash
# Test API
python test_api_key.py

# Test complet
python test_langgraph.py
```

---

## 📖 Documentation Complète

Voir [GUIDE_DEMARRAGE.md](GUIDE_DEMARRAGE.md) pour:
- Guide détaillé d'installation
- Configuration avancée
- Dépannage
- Architecture du système

---

## 🆘 Problèmes Courants

**Erreur 401 (API Key invalide):**
```bash
# Vérifier que la variable système est désactivée
set ANTHROPIC_API_KEY=
# Puis relancer
```

**Port 3000 occupé:**
```bash
# Utiliser un autre port
python demo_server.py 8080
```

**Module non trouvé:**
```bash
pip install -r requirements.txt
```

---

## 📁 Fichiers Importants

| Fichier | Description |
|---------|-------------|
| `start.bat` | Script de démarrage Windows |
| `demo_server.py` | Serveur API local |
| `frontend/index.html` | Interface web |
| `.env` | Configuration (clé API) |
| `GUIDE_DEMARRAGE.md` | Documentation complète |

---

## 🎯 Exemples de Conversations

**Général:**
- "Bonjour, comment vas-tu?"
- "Merci pour ton aide"

**Médicaments:**
- "Quels médicaments dois-je prendre?"
- "À quelle heure mes médicaments?"

**Symptômes:**
- "J'ai mal à la tête"
- "Je me sens fatigué"

**Urgences:**
- "Aide! C'est urgent"
- "Urgence médicale"

---

**🔗 Technologies:** Python • Claude AI • LangChain • LangGraph • HTML/CSS/JS

**📧 Créé par:** Muhammad Ehab
