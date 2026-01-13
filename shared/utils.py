"""
Utilitaires partagés
"""

import os
import json
from typing import Dict, Any
from datetime import datetime, timedelta
import boto3


class SNSHelper:
    """Helper pour envoyer des SMS via SNS"""

    def __init__(self):
        self.sns_client = boto3.client('sns')

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Envoie un SMS"""
        try:
            self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            print(f"SMS envoyé à {phone_number}")
            return True
        except Exception as e:
            print(f"Erreur envoi SMS: {e}")
            return False

    def send_emergency_sms(self, contacts: list, user_name: str, message: str, severity: str) -> list:
        """Envoie des SMS d'urgence à plusieurs contacts"""
        results = []

        emergency_message = f"""
🚨 ALERTE SMARTDOC

{user_name} a besoin d'aide!

Message: "{message}"

Gravité: {severity.upper()}
Heure: {datetime.now().strftime('%H:%M')}

Veuillez contacter immédiatement.
        """.strip()

        for contact in contacts:
            success = self.send_sms(contact['phone'], emergency_message)
            results.append({
                'contact': contact['name'],
                'phone': contact['phone'],
                'success': success
            })

        return results


class LambdaHelper:
    """Helper pour invoquer d'autres Lambdas"""

    def __init__(self):
        self.lambda_client = boto3.client('lambda')

    def invoke_agent(self, agent_name: str, payload: Dict) -> Dict[str, Any]:
        """Invoque un agent Lambda"""
        try:
            response = self.lambda_client.invoke(
                FunctionName=f'smartdoc-{agent_name}',
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            result = json.loads(response['Payload'].read())
            return result
        except Exception as e:
            print(f"Erreur invocation Lambda {agent_name}: {e}")
            return {'error': str(e)}


def generate_id(prefix: str) -> str:
    """Génère un ID unique avec préfixe"""
    timestamp = datetime.now().timestamp()
    return f"{prefix}_{int(timestamp * 1000)}"


def format_datetime(dt: datetime) -> str:
    """Formate une date en français"""
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
              'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

    day_name = days[dt.weekday()]
    month_name = months[dt.month - 1]

    return f"{day_name} {dt.day} {month_name} {dt.year} à {dt.hour:02d}h{dt.minute:02d}"


def parse_time(time_str: str) -> datetime:
    """Parse une heure au format HH:MM"""
    return datetime.strptime(time_str, '%H:%M')


def get_next_medication_time(schedules: list) -> Dict[str, Any]:
    """Calcule le prochain horaire de médicament"""
    now = datetime.now()
    next_times = []

    for schedule in schedules:
        scheduled_time = datetime.combine(
            now.date(),
            parse_time(schedule['time']).time()
        )

        # Si l'heure est passée, prendre demain
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)

        minutes_until = int((scheduled_time - now).total_seconds() / 60)

        next_times.append({
            'time': schedule['time'],
            'datetime': scheduled_time,
            'minutes_until': minutes_until
        })

    # Retourner le plus proche
    if next_times:
        return min(next_times, key=lambda x: x['minutes_until'])
    return None


def create_lambda_response(status_code: int, body: Dict, cors: bool = True) -> Dict:
    """Crée une réponse Lambda formatée"""
    response = {
        'statusCode': status_code,
        'body': json.dumps(body, ensure_ascii=False)
    }

    if cors:
        response['headers'] = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }

    return response


# Instances globales
sns_helper = SNSHelper()
lambda_helper = LambdaHelper()
