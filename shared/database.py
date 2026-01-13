"""
Helpers pour DynamoDB
"""

import boto3
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
import os


class DynamoDBHelper:
    """Helper pour interagir avec DynamoDB"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.region = os.environ.get('AWS_REGION', 'us-east-1')

    def get_table(self, table_name: str):
        """Récupère une table DynamoDB"""
        return self.dynamodb.Table(table_name)

    # ===== USERS =====

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Récupère un utilisateur"""
        table = self.get_table('SmartDoc_Users')
        try:
            response = table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Erreur get_user: {e}")
            return None

    def create_user(self, user_data: Dict) -> bool:
        """Crée un utilisateur"""
        table = self.get_table('SmartDoc_Users')
        try:
            table.put_item(Item=user_data)
            return True
        except ClientError as e:
            print(f"Erreur create_user: {e}")
            return False

    # ===== MEDICATIONS =====

    def get_user_medications(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """Récupère les médicaments d'un utilisateur"""
        table = self.get_table('SmartDoc_Medications')
        try:
            if active_only:
                response = table.query(
                    IndexName='UserIdIndex',
                    KeyConditionExpression='user_id = :uid',
                    FilterExpression='active = :active',
                    ExpressionAttributeValues={
                        ':uid': user_id,
                        ':active': True
                    }
                )
            else:
                response = table.query(
                    IndexName='UserIdIndex',
                    KeyConditionExpression='user_id = :uid',
                    ExpressionAttributeValues={':uid': user_id}
                )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Erreur get_user_medications: {e}")
            return []

    def add_medication(self, medication_data: Dict) -> bool:
        """Ajoute un médicament"""
        table = self.get_table('SmartDoc_Medications')
        try:
            table.put_item(Item=medication_data)
            return True
        except ClientError as e:
            print(f"Erreur add_medication: {e}")
            return False

    # ===== APPOINTMENTS =====

    def get_user_appointments(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Récupère les rendez-vous d'un utilisateur"""
        table = self.get_table('SmartDoc_Appointments')
        try:
            response = table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                Limit=limit,
                ScanIndexForward=True  # Tri ascendant par date
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Erreur get_user_appointments: {e}")
            return []

    def add_appointment(self, appointment_data: Dict) -> bool:
        """Ajoute un rendez-vous"""
        table = self.get_table('SmartDoc_Appointments')
        try:
            table.put_item(Item=appointment_data)
            return True
        except ClientError as e:
            print(f"Erreur add_appointment: {e}")
            return False

    # ===== CONVERSATIONS =====

    def save_conversation(self, conversation_data: Dict) -> bool:
        """Sauvegarde une conversation"""
        table = self.get_table('SmartDoc_Conversations')
        try:
            table.put_item(Item=conversation_data)
            return True
        except ClientError as e:
            print(f"Erreur save_conversation: {e}")
            return False

    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Récupère l'historique des conversations"""
        table = self.get_table('SmartDoc_Conversations')
        try:
            response = table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                Limit=limit,
                ScanIndexForward=False  # Les plus récentes en premier
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Erreur get_user_conversations: {e}")
            return []

    # ===== EMERGENCIES =====

    def save_emergency(self, emergency_data: Dict) -> bool:
        """Sauvegarde une urgence"""
        table = self.get_table('SmartDoc_Emergencies')
        try:
            table.put_item(Item=emergency_data)
            return True
        except ClientError as e:
            print(f"Erreur save_emergency: {e}")
            return False

    def get_user_emergencies(self, user_id: str) -> List[Dict]:
        """Récupère les urgences d'un utilisateur"""
        table = self.get_table('SmartDoc_Emergencies')
        try:
            response = table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                ScanIndexForward=False
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Erreur get_user_emergencies: {e}")
            return []


# Instance globale
db = DynamoDBHelper()
