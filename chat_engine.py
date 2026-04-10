import os
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False


class ChatEngine:
    def __init__(self):
        self.use_gemini = False
        self.model: Any = None

        self.sessions: Dict[str, List[Dict[str, str]]] = {}

        if GEMINI_AVAILABLE and genai:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                self.use_gemini = True

    def get_response(self, user_message: str, username: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Generate response, optionally maintaining session context"""
        if session_id and session_id not in self.sessions:
            self.sessions[session_id] = []

        
        if session_id:
            self.sessions[session_id].append({"user": user_message})

        if self.use_gemini:
            try:
                
                history_text = ""
                if session_id:
                    for pair in self.sessions[session_id]:
                        history_text += f"User: {pair.get('user')}\nBot: {pair.get('bot', '')}\n"

                prompt = f"""
You are a compassionate mental health support chatbot.

Conversation so far:
{history_text}
The user {username if username else 'someone'} says: "{user_message}"

Provide a calm, empathetic, and supportive response.
Be gentle, kind, emotionally intelligent, and understanding.
Validate the user’s feelings and offer simple, practical coping strategies.
Focus on emotional comfort AND problem-solving guidance in a warm and friendly tone.
Keep your response concise (2-5 sentences).
"""

                response = self.model.generate_content(prompt)

                if hasattr(response, "candidates") and response.candidates:
                    bot_response = response.candidates[0].content.parts[0].text.strip()
                else:
                    bot_response = "I'm here for you. Could you tell me a bit more about what you're feeling?"

            except Exception as e:
                print(f"Gemini API error: {e}")
                bot_response = self._get_mock_response(user_message)
        else:
            bot_response = self._get_mock_response(user_message)

        
        if session_id:
            self.sessions[session_id][-1]["bot"] = bot_response

        return bot_response

    def _get_mock_response(self, user_message: str) -> str:
        """Fallback responses when Gemini is not available"""
        user_message_lower = user_message.lower()
        if any(word in user_message_lower for word in ['sad', 'depressed', 'down', 'unhappy']):
            return "I hear that you're feeling down. It's completely normal to have difficult emotions. Would you like to share more about what's been happening?"
        elif any(word in user_message_lower for word in ['anxious', 'worried', 'scared', 'nervous', 'anxiety']):
            return "Anxiety can feel overwhelming. Remember that these feelings are temporary. Taking slow, deep breaths can help. What's making you feel anxious right now?"
        elif any(word in user_message_lower for word in ['stressed', 'overwhelmed', 'pressure']):
            return "It sounds like you're dealing with a lot right now. It's important to take things one step at a time. What's the main source of your stress?"
        elif any(word in user_message_lower for word in ['lonely', 'alone', 'isolated']):
            return "Feeling lonely is tough, and I'm glad you're reaching out. Connection is important. Have you thought about reaching out to someone you trust?"
        elif any(word in user_message_lower for word in ['happy', 'good', 'great', 'better']):
            return "I'm so glad to hear that! It's wonderful when things are going well. What's been contributing to these positive feelings?"
        elif any(word in user_message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're very welcome! I'm here to support you whenever you need. How else can I help you today?"
        elif any(word in user_message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm here to listen and support you. How are you feeling today?"
        else:
            return "I understand. Thank you for sharing that with me. Can you tell me more about how you're feeling?"


chat_engine = ChatEngine()
