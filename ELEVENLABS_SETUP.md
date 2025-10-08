# ElevenLabs TTS Integration Guide

## Overview
This project now uses ElevenLabs for high-quality text-to-speech generation instead of edge-tts. ElevenLabs provides more natural-sounding voices with better control over voice characteristics.

## Setup Instructions

### 1. Get ElevenLabs API Key
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for an account
3. Navigate to your profile settings
4. Copy your API key

### 2. Set Environment Variable
```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test the Integration
```bash
python test_elevenlabs.py
```

## Available Voices

The following voices are pre-configured in `elevenlabs_config.py`:

- **adam**: Deep, authoritative voice
- **antoni**: Warm, conversational voice  
- **arnold**: Deep, powerful voice
- **bella**: Soft, friendly voice
- **domi**: Confident, clear voice
- **elli**: Warm, natural voice
- **josh**: Deep, smooth voice
- **rachel**: Clear, professional voice
- **sam**: Warm, friendly voice

## Customizing Voice Settings

You can modify voice characteristics in `elevenlabs_config.py`:

```python
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.5,           # Voice stability (0.0 to 1.0)
    "similarity_boost": 0.5,   # Voice similarity boost (0.0 to 1.0)
    "style": 0.0,              # Voice style exaggeration (0.0 to 1.0)
    "use_speaker_boost": True  # Enable speaker boost for clarity
}
```

## Usage Examples

### Basic Usage
```python
import asyncio
from utility.audio.audio_generator import generate_audio

async def main():
    await generate_audio("Hello world!", "output.wav")

asyncio.run(main())
```

### Using Different Voices
```python
# Use a specific voice
await generate_audio("Hello world!", "output.wav", voice_name="rachel")
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure `ELEVENLABS_API_KEY` is set correctly
2. **Voice Not Found**: Check that the voice name exists in `VOICE_IDS`
3. **Audio Quality**: Adjust `stability` and `similarity_boost` settings

### Getting More Voices

1. Visit [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
2. Find voice IDs for voices you like
3. Add them to `VOICE_IDS` in `elevenlabs_config.py`

## Migration from edge-tts

The main changes from edge-tts:
- ✅ Better voice quality and naturalness
- ✅ More voice options
- ✅ Better control over voice characteristics
- ✅ Professional-grade TTS
- ❌ Requires API key (edge-tts was free)
- ❌ Usage limits based on ElevenLabs plan
