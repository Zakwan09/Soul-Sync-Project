CRISIS_KEYWORDS = [
    'suicide', 'suicidal', 'kill myself', 'end my life', 'want to die',
    'hurt myself', 'self harm', 'self-harm', 'cutting', 'no reason to live',
    'better off dead', 'can\'t go on', 'ending it all'
]

CRISIS_RESPONSES = {
    'suicide': "It sounds like you're in deep pain. You don’t have to face this alone. Someone is ready to listen and help you right now.",
    
    'suicidal': "I’m really sorry that you’re feeling like this. You matter, and there are people who truly care about you. You deserve help and support.",
    
    'kill myself': "I’m very concerned about your safety. You are not alone, and your life has meaning. Please reach out to a helpline or trusted person now.",
    
    'end my life': "It sounds like things are really hard for you. You deserve care and understanding — please talk to someone who can help you through this moment.",
    
    'want to die': "I hear you. It must be painful to feel this way. You don’t have to go through it alone — support is available 24/7.",
    
    'hurt myself': "It sounds like you’re struggling and thinking about hurting yourself. You matter, and you deserve safety and care. Help is available right now.",
    
    'self harm': "If you’re thinking about self-harm, please reach out for help. You are not alone, and there are people who can support you through this.",
    
    'self-harm': "You’re not alone in feeling this way. Please talk to someone you trust or contact a helpline for immediate support.",
    
    'cutting': "I can tell you’re in distress. You don’t deserve to be in pain. There are people who can help you find safer ways to cope.",
    
    'no reason to live': "I’m really sorry you’re feeling hopeless right now. You matter more than you know, and help is available to get through this.",
    
    'better off dead': "You are valuable, and the world is better with you in it. Please reach out for help — you do not have to go through this alone.",
    
    'can\'t go on': "It sounds like things feel unbearable right now. You don’t have to face this pain alone. Help is here for you.",
    
    'ending it all': "I can hear that you’re in deep pain. Please reach out to someone who can help you — you are not alone, and you deserve care."
}

CRISIS_RESOURCES = """
You are not alone — your family, your friends, your well-wishers, and Soul Sync 🤍 are all here for you. What you’re feeling matters, and you deserve care, support, and understanding. There are people who truly care about you and want to help you stay safe. You don’t have to face this alone — help is always available.

You can also reach out for immediate support using the resources below:

India — AASRA Helpline: 91-9820466726
United States — Suicide & Crisis Lifeline: 988 or 1-800-273-8255
Emergency Services — Call your local emergency number (112 in India, 911 in the United States)
"""

def detect_crisis(message: str) -> str | None:
    """
    Detects crisis-related keywords in a user message and returns a specific supportive message.
    If no keyword is found, returns None.
    """
    message_lower = message.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return CRISIS_RESPONSES.get(keyword, None)
    return None


def get_crisis_response(keyword: str | None = None) -> str:
    """
    Returns a personalized crisis response if keyword detected,
    otherwise returns general crisis resources message.
    """
    if keyword and keyword in CRISIS_RESPONSES:
        return f"{CRISIS_RESPONSES[keyword]}\n\n{CRISIS_RESOURCES}"
    return CRISIS_RESOURCES
