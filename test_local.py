#!/usr/bin/env python3
import sys, os
sys.path.insert(0, 'shared')
sys.path.insert(0, 'lambda/orchestrator')

if not os.environ.get('ANTHROPIC_API_KEY'):
    print("Set ANTHROPIC_API_KEY first!")
    sys.exit(1)

class MockDB:
    def get_user(self, id): return {'user_id': id, 'name': 'Test'}
    def get_user_medications(self, id, active=True): return []
    def get_user_appointments(self, id, limit=10): return []
    def save_conversation(self, data): return True

import database
database.db = MockDB()

from agent import orchestrator
from langchain_core.messages import HumanMessage

for msg in ["Quels sont mes médicaments?", "Bonjour"]:
    print(f"\nTest: {msg}")
    result = orchestrator.invoke({"messages": [HumanMessage(content=msg)], "user_id": "test", "intent": "", "context": {}, "next_agent": "", "final_response": "", "error": ""})
    print(f"Intent: {result['intent']}")
    print(f"Response: {result['final_response'][:100]}...")
