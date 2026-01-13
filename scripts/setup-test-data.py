#!/usr/bin/env python3
"""
Script pour créer des données de test dans DynamoDB
"""

import boto3
import sys
from datetime import datetime, timedelta
import json

# Configuration
ENVIRONMENT = sys.argv[1] if len(sys.argv) > 1 else 'dev'
REGION = 'us-east-1'

dynamodb = boto3.resource('dynamodb', region_name=REGION)

print(f"🔧 Configuration des données de test pour l'environnement: {ENVIRONMENT}")
print()

# Tables
users_table = dynamodb.Table(f'SmartDoc_Users_{ENVIRONMENT}')
medications_table = dynamodb.Table(f'SmartDoc_Medications_{ENVIRONMENT}')
appointments_table = dynamodb.Table(f'SmartDoc_Appointments_{ENVIRONMENT}')

# ===== UTILISATEUR TEST =====

print("👤 Création d'utilisateurs test...")

test_users = [
    {
        'user_id': 'user_marie_123',
        'name': 'Marie Dupont',
        'age': 72,
        'phone': '+33612345678',
        'email': 'marie.dupont@example.com',
        'emergency_contacts': [
            {
                'name': 'Sophie Dupont',
                'relation': 'Fille',
                'phone': '+33698765432'
            },
            {
                'name': 'Pierre Dupont',
                'relation': 'Fils',
                'phone': '+33687654321'
            }
        ],
        'medical_conditions': ['Hypertension', 'Diabète type 2'],
        'created_at': datetime.utcnow().isoformat()
    },
    {
        'user_id': 'user_jean_456',
        'name': 'Jean Martin',
        'age': 68,
        'phone': '+33623456789',
        'email': 'jean.martin@example.com',
        'emergency_contacts': [
            {
                'name': 'Claire Martin',
                'relation': 'Épouse',
                'phone': '+33634567890'
            }
        ],
        'medical_conditions': ['Arthrose'],
        'created_at': datetime.utcnow().isoformat()
    }
]

for user in test_users:
    users_table.put_item(Item=user)
    print(f"  ✅ Utilisateur créé: {user['name']} ({user['user_id']})")

print()

# ===== MÉDICAMENTS TEST =====

print("💊 Création de médicaments test...")

test_medications = [
    {
        'medication_id': 'med_marie_001',
        'user_id': 'user_marie_123',
        'name': 'Aspégic 100mg',
        'dosage': '1 sachet',
        'frequency': '1x/jour',
        'schedules': [
            {'time': '08:00', 'hour': 8}
        ],
        'instructions': 'À prendre avec un grand verre d\'eau le matin',
        'start_date': '2025-01-01',
        'active': True
    },
    {
        'medication_id': 'med_marie_002',
        'user_id': 'user_marie_123',
        'name': 'Doliprane 500mg',
        'dosage': '1 comprimé',
        'frequency': '2x/jour',
        'schedules': [
            {'time': '12:00', 'hour': 12},
            {'time': '20:00', 'hour': 20}
        ],
        'instructions': 'À prendre pendant les repas',
        'start_date': '2025-01-01',
        'active': True
    },
    {
        'medication_id': 'med_marie_003',
        'user_id': 'user_marie_123',
        'name': 'Glucophage 850mg',
        'dosage': '1 comprimé',
        'frequency': '2x/jour',
        'schedules': [
            {'time': '08:00', 'hour': 8},
            {'time': '20:00', 'hour': 20}
        ],
        'instructions': 'Pour le diabète, à prendre pendant les repas',
        'start_date': '2024-06-01',
        'active': True
    },
    {
        'medication_id': 'med_jean_001',
        'user_id': 'user_jean_456',
        'name': 'Voltarène 50mg',
        'dosage': '1 comprimé',
        'frequency': '2x/jour',
        'schedules': [
            {'time': '09:00', 'hour': 9},
            {'time': '21:00', 'hour': 21}
        ],
        'instructions': 'Pour les douleurs articulaires',
        'start_date': '2025-01-01',
        'active': True
    }
]

for med in test_medications:
    medications_table.put_item(Item=med)
    print(f"  ✅ Médicament créé: {med['name']} pour {med['user_id']}")

print()

# ===== RENDEZ-VOUS TEST =====

print("📅 Création de rendez-vous test...")

tomorrow = datetime.now() + timedelta(days=1)
next_week = datetime.now() + timedelta(days=7)

test_appointments = [
    {
        'appointment_id': 'appt_marie_001',
        'user_id': 'user_marie_123',
        'title': 'Cardiologue - Dr. Martin',
        'date': tomorrow.strftime('%Y-%m-%d'),
        'time': '14:30',
        'location': 'Hôpital Saint-Louis, 3ème étage',
        'doctor_name': 'Dr. Martin',
        'notes': 'Consultation de suivi pour l\'hypertension',
        'reminder_sent': False
    },
    {
        'appointment_id': 'appt_marie_002',
        'user_id': 'user_marie_123',
        'title': 'Diabétologue - Dr. Rousseau',
        'date': next_week.strftime('%Y-%m-%d'),
        'time': '10:00',
        'location': 'Cabinet Dr. Rousseau, 15 rue de la Paix',
        'doctor_name': 'Dr. Rousseau',
        'notes': 'Bilan diabète trimestriel',
        'reminder_sent': False
    },
    {
        'appointment_id': 'appt_jean_001',
        'user_id': 'user_jean_456',
        'title': 'Rhumatologue - Dr. Leroux',
        'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        'time': '15:00',
        'location': 'Clinique des Lilas',
        'doctor_name': 'Dr. Leroux',
        'notes': 'Suivi arthrose',
        'reminder_sent': False
    }
]

for appt in test_appointments:
    appointments_table.put_item(Item=appt)
    print(f"  ✅ RDV créé: {appt['title']} le {appt['date']} pour {appt['user_id']}")

print()
print("=" * 60)
print("✅ Données de test créées avec succès!")
print("=" * 60)
print()
print("�� Utilisateurs de test:")
print("  • Marie Dupont (user_marie_123) - 3 médicaments, 2 RDV")
print("  • Jean Martin (user_jean_456) - 1 médicament, 1 RDV")
print()
print("🧪 Vous pouvez maintenant tester l'API avec ces utilisateurs!")
print()
print("Exemple de requête:")
print("""
curl -X POST https://your-api-url/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": "user_marie_123",
    "message": "Quels sont mes médicaments?"
  }'
""")
