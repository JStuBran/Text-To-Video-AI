# ElevenLabs Configuration
# You can customize these settings for different voice characteristics

# Voice IDs (you can find more at https://elevenlabs.io/voice-library)
VOICE_IDS = {
    "adam": "pNInz6obpgDQGcFmaJgB",      # Adam - Deep, authoritative
    "antoni": "ErXwobaYiN019PkySvjV",     # Antoni - Warm, conversational
    "arnold": "VR6AewLTigWG4xSOukaG",     # Arnold - Deep, powerful
    "bella": "EXAVITQu4vr4xnSDxMaL",      # Bella - Soft, friendly
    "domi": "AZnzlk1XvdvUeBnXmlld",       # Domi - Confident, clear
    "elli": "MF3mGyEYCl7XYWbV9V6O",       # Elli - Warm, natural
    "josh": "TxGEqnHWrfWFTfGW9XjX",       # Josh - Deep, smooth
    "rachel": "21m00Tcm4TlvDq8ikWAM",     # Rachel - Clear, professional
    "sam": "yoZ06aMxZJJ28mfd3POQ",        # Sam - Warm, friendly
}

# Default voice settings
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.5,           # Voice stability (0.0 to 1.0)
    "similarity_boost": 0.5,   # Voice similarity boost (0.0 to 1.0)
    "style": 0.0,              # Voice style exaggeration (0.0 to 1.0)
    "use_speaker_boost": True  # Enable speaker boost for clarity
}

# Default voice to use
DEFAULT_VOICE = "adam"
