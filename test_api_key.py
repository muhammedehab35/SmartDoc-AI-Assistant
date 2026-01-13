#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('ANTHROPIC_API_KEY')

print("="*70)
print("Test de la cle API Anthropic")
print("="*70 + "\n")

if not api_key:
    print("ERREUR: ANTHROPIC_API_KEY non trouvee dans .env")
    exit(1)

print(f"Cle API trouvee: {api_key[:20]}...{api_key[-10:]}")
print(f"Longueur: {len(api_key)} caracteres\n")

# Test avec anthropic SDK direct
try:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)

    print("Tentative d'appel API...\n")

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Dis juste 'Bonjour' en francais"}
        ]
    )

    print("SUCCES!")
    print(f"Reponse de Claude: {message.content[0].text}")
    print("\n" + "="*70)
    print("La cle API fonctionne correctement!")
    print("Modele: claude-3-haiku-20240307")
    print("="*70)

except Exception as e:
    print(f"ERREUR: {str(e)}")
    print("\nLa cle API ne fonctionne pas.")
    print("Verifiez que:")
    print("1. La cle est correctement copiee dans .env")
    print("2. La cle commence par 'sk-ant-api03-'")
    print("3. Il n'y a pas d'espaces ou caracteres speciaux")
