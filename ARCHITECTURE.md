# 🏗️ Architecture SmartDoc Assistant

Ce document explique en détail l'architecture technique du projet.

---

## 📊 Vue d'ensemble

SmartDoc Assistant utilise une architecture **serverless** basée sur:
- **AWS Lambda** pour l'exécution du code
- **LangGraph** pour l'orchestration des agents IA
- **Claude AI** pour l'intelligence artificielle
- **DynamoDB** pour le stockage des données

---

## 🔄 Flow complet d'une requête

```
User Input: "Quels sont mes médicaments?"
    ↓
[1] Frontend (app.js)
    │ sendMessage()
    │ POST /chat
    ↓
[2] API Gateway
    │ Route: POST /chat
    │ Integration: Lambda Proxy
    ↓
[3] Orchestrator Lambda
    │ handler.lambda_handler()
    │ ↓
    │ LangGraph Graph:
    │ ├─ analyze_intent() → "medication"
    │ ├─ load_user_context() → DynamoDB queries
    │ ├─ route_to_agent() → "medication-agent"
    │ ├─ call_specialized_agent()
    │ │   ↓
    │ │   [4] Medication Agent Lambda
    │ │       │ handler.lambda_handler()
    │ │       │ ↓
    │ │       │ LangGraph Graph:
    │ │       │ ├─ determine_action() → "info"
    │ │       │ ├─ load_medications() → DynamoDB
    │ │       │ ├─ provide_medication_info()
    │ │       │ │   ↓
    │ │       │ │   [5] Claude API
    │ │       │ │       Prompt + Context
    │ │       │ │       ↓
    │ │       │ │       Response
    │ │       │ │   ↓
    │ │       │ └─ Returns response
    │ │   ↓
    │ └─ save_conversation() → DynamoDB
    ↓
[6] Response to API Gateway
    ↓
[7] Frontend displays response
```

**Temps total: ~2-4 secondes**

---

## 🤖 Architecture des Agents LangGraph

### 1. Orchestrator Agent

**Responsabilité:** Router intelligent

```python
StateGraph(OrchestratorState):
    ├─ analyze_intent
    │   Input: user_message
    │   Output: intent (medication|symptom|appointment|emergency|general)
    │   LLM: Claude Sonnet 4.5
    │
    ├─ load_user_context
    │   DynamoDB Queries:
    │   ├─ Users table
    │   ├─ Medications table
    │   └─ Appointments table
    │
    ├─ route_to_agent
    │   Logic: intent → agent_name
    │
    ├─ call_specialized_agent
    │   Lambda invoke:
    │   └─ medication-agent | symptom-agent | emergency-agent
    │
    └─ save_conversation
        DynamoDB Write:
        └─ Conversations table
```

### 2. Medication Agent

**Responsabilité:** Gestion des médicaments

```python
StateGraph(MedicationState):
    ├─ determine_action
    │   Keywords analysis:
    │   ├─ "rappel", "quand" → reminder
    │   ├─ "interaction" → interaction_check
    │   └─ default → info
    │
    ├─ load_medications
    │   DynamoDB Query:
    │   └─ Medications table (user_id index)
    │
    ├─ [Conditional Branch]
    │   ├─ provide_medication_info
    │   │   └─ Claude API (list medications)
    │   │
    │   ├─ check_next_dose
    │   │   └─ Calculate next medication time
    │   │
    │   └─ check_interactions
    │       └─ Claude API (analyze interactions)
    │
    └─ Returns response
```

### 3. Symptom Agent

**Responsabilité:** Analyse des symptômes

```python
StateGraph(SymptomState):
    ├─ analyze_symptom
    │   Claude API:
    │   └─ Evaluate severity (mild|moderate|severe|critical)
    │
    ├─ check_medication_side_effects
    │   Claude API:
    │   └─ Check if symptoms = side effects
    │
    ├─ generate_recommendations
    │   Logic based on severity:
    │   ├─ critical → Call 15 (SAMU)
    │   ├─ severe → See doctor today
    │   ├─ moderate → Monitor 24-48h
    │   └─ mild → Rest and hydrate
    │
    ├─ check_appointments
    │   DynamoDB Query:
    │   └─ Next appointments
    │
    └─ create_response
        └─ Format final response
```

### 4. Emergency Agent

**Responsabilité:** Gestion des urgences

```python
StateGraph(EmergencyState):
    ├─ assess_severity
    │   Keywords + Claude API:
    │   └─ Determine severity (critical|high|medium|low)
    │
    ├─ notify_emergency_contacts
    │   SNS Publish:
    │   └─ Send SMS to emergency contacts
    │
    ├─ log_emergency
    │   DynamoDB Write:
    │   └─ Emergencies table
    │
    ├─ provide_immediate_guidance
    │   Claude API:
    │   └─ Generate step-by-step instructions
    │
    └─ create_final_response
        └─ Format response with actions taken
```

---

## 💾 Schéma de Base de Données (DynamoDB)

### Table: SmartDoc_Users

```
Partition Key: user_id (String)

Attributes:
├─ user_id: String (PK)
├─ name: String
├─ age: Number
├─ phone: String
├─ email: String
├─ emergency_contacts: List
│   └─ { name, relation, phone }
├─ medical_conditions: List
└─ created_at: String (ISO 8601)
```

### Table: SmartDoc_Medications

```
Partition Key: medication_id (String)
Global Secondary Index: UserIdIndex (user_id)

Attributes:
├─ medication_id: String (PK)
├─ user_id: String (GSI PK)
├─ name: String
├─ dosage: String
├─ frequency: String
├─ schedules: List
│   └─ { time, hour }
├─ instructions: String
├─ start_date: String
├─ end_date: String
└─ active: Boolean
```

### Table: SmartDoc_Appointments

```
Partition Key: appointment_id (String)
Global Secondary Index: UserIdIndex (user_id)

Attributes:
├─ appointment_id: String (PK)
├─ user_id: String (GSI PK)
├─ title: String
├─ date: String (YYYY-MM-DD)
├─ time: String (HH:MM)
├─ location: String
├─ doctor_name: String
├─ notes: String
└─ reminder_sent: Boolean
```

### Table: SmartDoc_Conversations

```
Partition Key: conversation_id (String)
Global Secondary Index: UserIdIndex (user_id)

Attributes:
├─ conversation_id: String (PK)
├─ user_id: String (GSI PK)
├─ timestamp: String (ISO 8601)
├─ user_message: String
├─ assistant_response: String
├─ intent: String
└─ agent_used: String
```

### Table: SmartDoc_Emergencies

```
Partition Key: emergency_id (String)
Global Secondary Index: UserIdIndex (user_id)

Attributes:
├─ emergency_id: String (PK)
├─ user_id: String (GSI PK)
├─ timestamp: String (ISO 8601)
├─ severity: String (critical|high|medium|low)
├─ emergency_type: String (fall|pain|breathing|other)
├─ message: String
├─ actions_taken: List
├─ contacts_notified: List
└─ resolved: Boolean
```

---

## 🔐 Sécurité et Permissions IAM

### Lambda Execution Role

```yaml
Permissions:
  - CloudWatch Logs: Write
  - DynamoDB:
      - GetItem
      - PutItem
      - Query
      - Scan
      - UpdateItem
  - SNS: Publish
  - Lambda: InvokeFunction (for inter-agent calls)
```

### API Gateway

```
- CORS enabled: Allow all origins (*)
- HTTPS only (enforced by AWS)
- No authentication (demo)
  → Production: Use Cognito or API Keys
```

---

## 📈 Scalabilité

### Auto-scaling

**Lambda:**
- Concurrent executions: 1000 (default)
- Auto-scales automatically
- Cold start: ~500ms first time

**DynamoDB:**
- On-demand billing mode
- Auto-scales read/write capacity
- No provisioning needed

### Performance Optimizations

1. **Connection pooling**: Réutiliser les connexions DynamoDB
2. **Caching**: Mettre en cache les réponses fréquentes
3. **Batch operations**: Regrouper les écritures DynamoDB
4. **CloudFront**: CDN pour le frontend (optionnel)

---

## 🔄 CI/CD (Future)

```
GitHub Actions Workflow:
├─ on: push to main
├─ Run tests
│   ├─ Unit tests (pytest)
│   ├─ Integration tests
│   └─ Security scan
├─ Build Lambda packages
│   └─ pip install + zip
├─ Deploy to staging
│   └─ CloudFormation update
├─ Run E2E tests
│   └─ Test API endpoints
└─ Deploy to production
    └─ CloudFormation update (manual approval)
```

---

## 🔍 Monitoring et Observabilité

### CloudWatch Metrics

```
Custom Metrics:
├─ Request count per agent
├─ Average response time
├─ Error rate
├─ Claude API tokens used
└─ DynamoDB consumed capacity
```

### CloudWatch Logs

```
Log Groups:
├─ /aws/lambda/smartdoc-orchestrator-{env}
├─ /aws/lambda/smartdoc-medication-agent-{env}
├─ /aws/lambda/smartdoc-symptom-agent-{env}
└─ /aws/lambda/smartdoc-emergency-agent-{env}

Log Format:
[AGENT_NAME] Log level: Message
Example: [MEDICATION] Chargement des médicaments...
```

### X-Ray Tracing (Future)

```
Trace:
User Request
  └─ API Gateway
      └─ Orchestrator Lambda
          ├─ DynamoDB: Get User
          ├─ DynamoDB: Get Medications
          └─ Medication Agent Lambda
              ├─ Claude API
              └─ DynamoDB: Save Conversation
```

---

## 🛡️ Disaster Recovery

### Backup Strategy

```
DynamoDB:
├─ Point-in-time recovery: Enabled
├─ Backup retention: 7 days
└─ Cross-region replication: Optional

Lambda:
├─ Code in S3 bucket
└─ Version control in Git
```

### Rollback Strategy

```bash
# Rollback CloudFormation
aws cloudformation update-stack \
  --stack-name smartdoc-prod \
  --use-previous-template

# Or delete and redeploy previous version
aws cloudformation delete-stack --stack-name smartdoc-prod
./scripts/deploy.sh prod
```

---

## 💡 Design Patterns utilisés

### 1. **Orchestrator Pattern**
L'Orchestrator Agent coordonne les agents spécialisés.

### 2. **State Machine Pattern**
LangGraph implémente des graphes à états pour chaque agent.

### 3. **Repository Pattern**
`database.py` encapsule l'accès à DynamoDB.

### 4. **Strategy Pattern**
Différents agents pour différentes stratégies de traitement.

### 5. **Chain of Responsibility**
Les requêtes passent par plusieurs nœuds du graph.

---

## 🔮 Évolutions futures

### Phase 2: Améliorations
- [ ] Caching Redis/ElastiCache
- [ ] Multi-tenancy support
- [ ] Real-time updates (WebSockets)
- [ ] Voice interface (Polly/Transcribe)

### Phase 3: Production
- [ ] Authentication (Cognito)
- [ ] Rate limiting
- [ ] WAF pour API Gateway
- [ ] Encryption at rest/in transit
- [ ] Compliance HIPAA

---

**Documentation technique complète pour SmartDoc Assistant**
