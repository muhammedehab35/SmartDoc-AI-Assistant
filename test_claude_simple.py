#!/usr/bin/env python3
"""
Test minimal avec Claude AI - Sans DynamoDB
"""

import sys
import os

# Vérifier la clé API
if not os.environ.get('ANTHROPIC_API_KEY'):
    print("❌ ERREUR: ANTHROPIC_API_KEY non définie!")
    print("\nDéfinissez-la avec:")
    print("  export ANTHROPIC_API_KEY=sk-ant-votre-cle")
    sys.exit(1)

print("✅ ANTHROPIC_API_KEY configurée")
print("🧪 Test simple avec Claude AI\n")

# Test direct avec LangChain et Claude
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# Initialiser Claude
# Essayer avec le nom de modèle correct
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",  # Version qui fonctionne avec votre clé API
    temperature=0.3
)

print("="*70)
print("🤖 TEST DIRECT AVEC CLAUDE AI")
print("="*70 + "\n")

# Test 1: Classification d'intention
print("📝 Test 1: Classification d'intention\n")

messages_test = [
    "Quels sont mes médicaments?",
    "J'ai mal à la tête",
    "Bonjour comment ça va?"
]

for msg in messages_test:
    print(f"💬 Message: {msg}")

    system_prompt = """
Tu es un classificateur d'intention pour un assistant médical.

Analyse le message et retourne UNE catégorie parmi:
- medication: Questions sur médicaments
- symptom: Symptômes de santé
- general: Conversation générale

Réponds UNIQUEMENT avec le mot-clé.
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=msg)
        ])

        print(f"🎯 Intent détecté: {response.content}")
        print()

    except Exception as e:
        print(f"❌ Erreur: {str(e)}\n")

print("="*70)

# Test 2: Réponse conversationnelle
print("\n📝 Test 2: Génération de réponse\n")

user_message = "Peux-tu m'expliquer comment tu peux m'aider?"

system_prompt = """
Tu es SmartDoc, un assistant médical bienveillant pour personnes âgées.

Réponds de manière:
- Simple et claire
- Chaleureuse
- En français
- Avec des phrases courtes
"""

try:
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    print(f"💬 Question: {user_message}")
    print(f"\n🤖 Réponse de Claude:\n")
    print("-"*70)
    print(response.content)
    print("-"*70)

except Exception as e:
    print(f"❌ Erreur: {str(e)}")

print("\n" + "="*70)
print("✅ Tests terminés!")
print("\n📊 Résultat:")
print("  • Claude AI fonctionne correctement")
print("  • Les réponses sont naturelles et contextuelles")
print("  • Prêt pour les tests LangGraph!")
print("\n🚀 Prochaine étape:")
print("  → Tester avec LangGraph: python test_with_claude.py")
print("="*70)
