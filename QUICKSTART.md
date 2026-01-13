# 🚀 Guide de démarrage rapide - SmartDoc Assistant

Ce guide vous permettra de déployer SmartDoc Assistant en **moins de 10 minutes**.

---

## ⚡ Démarrage ultra-rapide

### 1️⃣ Prérequis (5 min)

```bash
# Vérifier que vous avez Python 3.11+
python --version

# Vérifier AWS CLI
aws --version

# Si manquant, installer AWS CLI:
# https://aws.amazon.com/cli/
```

### 2️⃣ Obtenir votre clé API Anthropic (2 min)

1. Aller sur: https://console.anthropic.com
2. Créer un compte (gratuit)
3. Aller dans "API Keys"
4. Créer une nouvelle clé
5. Copier la clé (commence par `sk-ant-...`)

### 3️⃣ Configuration AWS (2 min)

```bash
# Configurer AWS CLI
aws configure
# Entrez:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Region: us-east-1
# - Output format: json
```

### 4️⃣ Déployer! (5 min)

**Sur Windows:**
```cmd
# Définir la clé API
set ANTHROPIC_API_KEY=sk-ant-votre-cle-ici

# Déployer
cd smartdoc-assistant
scripts\deploy.bat dev
```

**Sur Linux/Mac:**
```bash
# Définir la clé API
export ANTHROPIC_API_KEY=sk-ant-votre-cle-ici

# Déployer
cd smartdoc-assistant
chmod +x scripts/deploy.sh
./scripts/deploy.sh dev
```

### 5️⃣ Créer des données de test (1 min)

```bash
python scripts/setup-test-data.py dev
```

### 6️⃣ Tester! (1 min)

1. Ouvrir `frontend/index.html` dans votre navigateur
2. Cliquer sur ⚙️ (configuration)
3. Entrer:
   - **URL API**: L'URL affichée après le déploiement
   - **User ID**: `user_marie_123`
4. Cliquer "Sauvegarder"
5. Taper: "Quels sont mes médicaments?"

**🎉 Félicitations! Votre assistant IA est en ligne!**

---

## 🧪 Exemples de questions à tester

### Médicaments
- "Quels sont mes médicaments?"
- "Quand dois-je prendre mon prochain médicament?"
- "Y a-t-il des interactions entre mes médicaments?"

### Symptômes
- "J'ai mal à la tête depuis ce matin"
- "Je me sens fatigué"
- "J'ai de la fièvre"

### Rendez-vous
- "Quand est mon prochain rendez-vous?"
- "Avec quel médecin j'ai rendez-vous?"

### Urgence (ne testez qu'UNE FOIS)
- "Aide! Je suis tombé"
- "J'ai une douleur à la poitrine"

---

## 📊 Vérifier le déploiement

### Vérifier les Lambdas
```bash
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `smartdoc`)].FunctionName'
```

Vous devriez voir:
- `smartdoc-orchestrator-dev`
- `smartdoc-medication-agent-dev`
- `smartdoc-symptom-agent-dev`
- `smartdoc-emergency-agent-dev`

### Vérifier les tables DynamoDB
```bash
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `SmartDoc`)]'
```

Vous devriez voir:
- `SmartDoc_Users_dev`
- `SmartDoc_Medications_dev`
- `SmartDoc_Appointments_dev`
- `SmartDoc_Conversations_dev`
- `SmartDoc_Emergencies_dev`

### Vérifier l'API
```bash
# Remplacer YOUR-API-URL par votre URL
curl -X POST https://YOUR-API-URL/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_marie_123","message":"Bonjour"}'
```

---

## 🐛 Problèmes courants

### "ANTHROPIC_API_KEY non définie"
```bash
# Windows
set ANTHROPIC_API_KEY=votre-cle

# Linux/Mac
export ANTHROPIC_API_KEY=votre-cle
```

### "AWS credentials not found"
```bash
aws configure
```

### "Permission denied: deploy.sh"
```bash
chmod +x scripts/deploy.sh
```

### L'API ne répond pas
1. Vérifier l'URL (doit commencer par `https://`)
2. Vérifier dans AWS Console que les Lambdas existent
3. Regarder les logs CloudWatch

---

## 🎓 Prochaines étapes

1. **Personnaliser l'app**
   - Modifier les prompts dans `lambda/*/agent.py`
   - Changer les couleurs dans `frontend/styles.css`

2. **Ajouter vos propres utilisateurs**
   - Modifier `scripts/setup-test-data.py`
   - Ajouter vos données

3. **Déployer en production**
   ```bash
   ./scripts/deploy.sh prod
   ```

4. **Surveiller les coûts**
   - Aller dans AWS Cost Explorer
   - Activer des alarmes de budget

---

## 💰 Coûts estimés

**Pour 100 requêtes/jour:**
- AWS: ~0.50$/mois
- Claude API: ~15$/mois
- **Total: ~15.50$/mois**

**Le Free Tier AWS couvre les premiers mois!**

---

## 📚 Documentation complète

Voir [README.md](README.md) pour la documentation complète.

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/votre-username/smartdoc-assistant/issues)
- **Email**: votre-email@example.com

---

**Bon développement! 🚀**
