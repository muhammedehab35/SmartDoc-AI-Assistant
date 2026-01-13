#!/usr/bin/env python3
"""
Test pour trouver quel modèle Claude fonctionne avec votre clé API
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

if not os.environ.get('ANTHROPIC_API_KEY'):
    print("❌ Définissez ANTHROPIC_API_KEY")
    exit(1)

# Liste des modèles à tester
models = [
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-latest",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    "claude-3-haiku-20240307",
]

print("🔍 Test des modèles Claude disponibles...\n")

for model in models:
    print(f"Essai: {model}...", end=" ")
    try:
        llm = ChatAnthropic(model=model, temperature=0)
        response = llm.invoke([HumanMessage(content="Bonjour")])
        print(f"✅ FONCTIONNE!")
        print(f"   Réponse: {response.content[:50]}...\n")
        print(f"🎉 Utilisez ce modèle: {model}")
        break
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not_found" in error_msg:
            print("❌ Modèle non trouvé")
        elif "401" in error_msg or "authentication" in error_msg.lower():
            print("❌ Problème d'authentification - vérifiez votre clé API")
            break
        else:
            print(f"❌ Erreur: {error_msg[:50]}")
