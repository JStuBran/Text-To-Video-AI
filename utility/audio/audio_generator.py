import os
from elevenlabs import ElevenLabs
from elevenlabs_config import VOICE_IDS, DEFAULT_VOICE_SETTINGS, DEFAULT_VOICE

async def generate_audio(text, outputFilename, voice_name=None):
    """
    Generate audio using ElevenLabs TTS
    
    Args:
        text (str): Text to convert to speech
        outputFilename (str): Output audio file path
        voice_name (str, optional): Voice to use (defaults to DEFAULT_VOICE)
    """
    # Get API key from environment variable
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable is required")
    
    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=api_key)
    
    # Use provided voice or default
    voice_id = VOICE_IDS.get(voice_name or DEFAULT_VOICE, VOICE_IDS[DEFAULT_VOICE])
    
    # Generate audio using ElevenLabs
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_monolingual_v1",
        voice_settings=DEFAULT_VOICE_SETTINGS
    )
    
    # Save the audio to file
    with open(outputFilename, "wb") as f:
        for chunk in audio:
            f.write(chunk)





