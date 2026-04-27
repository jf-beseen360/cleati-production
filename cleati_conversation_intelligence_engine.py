"""CLEATI - Conversation Intelligence Engine"""
from enum import Enum

class FileType(Enum):
    ACCOUNTING = "accounting"
    LOGISTICS = "logistics"
    PRICING = "pricing"
    UNKNOWN = "unknown"

class ConversationIntelligenceEngine:
    def __init__(self):
        self.file_analysis = None
        self.user_answers = []
        self.messages = []
        self.state = "AWAITING_FILE"
        self.current_question_index = 0
        self.generation_requests = []
        self.guided_questions = {
            FileType.ACCOUNTING: [
                "Que voulez-vous faire avec vos données comptables?",
                "Pour quels pays?",
                "En quelle langue?"
            ],
            FileType.LOGISTICS: [
                "Que voulez-vous optimiser?",
                "Quels types de routes?",
                "Niveau de détail?"
            ],
            FileType.PRICING: [
                "Quelle analyse pour les prix?",
                "Par marché ou global?",
                "Inclure comparatif?"
            ]
        }

    def process_user_input(self, user_input: str):
        self.messages.append({"user": user_input})
        return f"✓ Réponse enregistrée: {user_input}"

    def get_conversation_history(self):
        return self.messages

    def get_conversation_summary(self):
        return {"messages": len(self.messages), "answers": len(self.user_answers)}

    def reset_conversation(self):
        self.__init__()
