"""
Data models pour SmartDoc Assistant
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class User(BaseModel):
    """Modèle utilisateur"""
    user_id: str
    name: str
    age: int
    phone: str
    email: Optional[str] = None
    emergency_contacts: List[Dict[str, str]] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class EmergencyContact(BaseModel):
    """Contact d'urgence"""
    name: str
    relation: str
    phone: str


class Medication(BaseModel):
    """Modèle médicament"""
    medication_id: str
    user_id: str
    name: str
    dosage: str
    frequency: str
    schedules: List[Dict[str, Any]] = Field(default_factory=list)
    instructions: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    active: bool = True


class Appointment(BaseModel):
    """Modèle rendez-vous"""
    appointment_id: str
    user_id: str
    title: str
    date: str
    time: str
    location: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    reminder_sent: bool = False


class Conversation(BaseModel):
    """Modèle conversation"""
    conversation_id: str
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user_message: str
    assistant_response: str
    intent: str
    agent_used: str


class Emergency(BaseModel):
    """Modèle urgence"""
    emergency_id: str
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    severity: str  # critical, high, medium, low
    message: str
    actions_taken: List[str] = Field(default_factory=list)
    resolved: bool = False
