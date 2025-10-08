#!/usr/bin/env python3
"""
Test script to verify ElevenLabs TTS integration
"""
import asyncio
import os
from utility.audio.audio_generator import generate_audio

async def test_elevenlabs():
    """Test ElevenLabs TTS functionality"""
    test_text = "Hello! This is a test of the ElevenLabs text-to-speech integration."
    output_file = "test_audio.wav"
    
    try:
        print("Testing ElevenLabs TTS...")
        print(f"Text: {test_text}")
        print(f"Output file: {output_file}")
        
        await generate_audio(test_text, output_file)
        
        if os.path.exists(output_file):
            print(f"✅ Success! Audio file created: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print("❌ Error: Audio file was not created")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nMake sure you have set the ELEVENLABS_API_KEY environment variable:")
        print("export ELEVENLABS_API_KEY='your-api-key-here'")

if __name__ == "__main__":
    asyncio.run(test_elevenlabs())
