#!/usr/bin/env python3
"""
Debug script to test imports in Railway environment
"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

print("\n🧪 Testing basic imports...")

try:
    import os
    print("✅ os")
except Exception as e:
    print(f"❌ os: {e}")

try:
    import json
    print("✅ json")
except Exception as e:
    print(f"❌ json: {e}")

try:
    from flask import Flask
    print("✅ Flask")
except Exception as e:
    print(f"❌ Flask: {e}")

try:
    from dotenv import load_dotenv
    print("✅ dotenv")
except Exception as e:
    print(f"❌ dotenv: {e}")

try:
    from openai import OpenAI
    print("✅ OpenAI")
except Exception as e:
    print(f"❌ OpenAI: {e}")

try:
    from elevenlabs import ElevenLabs
    print("✅ ElevenLabs")
except Exception as e:
    print(f"❌ ElevenLabs: {e}")

try:
    import moviepy
    print(f"✅ MoviePy: {moviepy.__version__}")
except Exception as e:
    print(f"❌ MoviePy: {e}")

try:
    from moviepy.editor import VideoFileClip
    print("✅ MoviePy.editor")
except Exception as e:
    print(f"❌ MoviePy.editor: {e}")

try:
    import whisper_timestamped
    print("✅ whisper_timestamped")
except Exception as e:
    print(f"❌ whisper_timestamped: {e}")

print("\n🏃 Basic imports test complete")

if __name__ == "__main__":
    app = Flask(__name__)
    
    @app.route('/debug')
    def debug():
        return {"message": "Debug script running successfully!"}
    
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Starting debug Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)