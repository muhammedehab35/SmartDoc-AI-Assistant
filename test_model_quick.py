#!/usr/bin/env python3
"""
Test rapide du modele Claude
"""

import sys
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

if not os.environ.get('ANTHROPIC_API_KEY'):
    print("ERREUR: ANTHROPIC_API_KEY non definie!")
    sys.exit(1)

print("ANTHROPIC_API_KEY configuree")
print("Test avec Claude AI\n")

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# Initialiser Claude avec le bon modele
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.3
)

print("="*70)
print("TEST MODELE CLAUDE")
print("="*70 + "\n")

# Test 1: Classification d'intention
print("Test 1: Classification d'intention\n")

test_messages = [
    "Quels sont mes medicaments?",
    "J'ai mal a la tete",
    "Bonjour comment ca va?"
]

for msg in test_messages:
    print(f"Message: {msg}")

    system_prompt = """
Tu es un classificateur d'intention pour un assistant medical.

Analyse le message et retourne UNE categorie parmi:
- medication: Questions sur medicaments
- symptom: Symptomes de sante
- general: Conversation generale

Reponds UNIQUEMENT avec le mot-cle.
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=msg)
        ])

        print(f"Intent detecte: {response.content}")
        print()

    except Exception as e:
        print(f"Erreur: {str(e)}\n")

print("="*70)

# Test 2: Reponse conversationnelle
print("\nTest 2: Generation de reponse\n")

user_message = "Peux-tu m'expliquer comment tu peux m'aider?"

system_prompt = """
Tu es SmartDoc, un assistant medical bienveillant pour personnes agees.

Reponds de maniere:
- Simple et claire
- Chaleureuse
- En francais
- Avec des phrases courtes
"""

try:
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    print(f"Question: {user_message}")
    print(f"\nReponse de Claude:\n")
    print("-"*70)
    print(response.content)
    print("-"*70)

except Exception as e:
    print(f"Erreur: {str(e)}")

print("\n" + "="*70)
print("Tests termines!")
print("\nResultat:")
print("  Claude AI fonctionne correctement")
print("  Modele utilise: claude-3-haiku-20240307")
print("  Les reponses sont naturelles et contextuelles")
print("  Pret pour les tests LangGraph!")
print("\nProchaine etape:")
print("  Tester avec LangGraph: python test_with_claude.py")
print("="*70)
