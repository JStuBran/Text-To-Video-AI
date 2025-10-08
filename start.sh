#!/bin/bash
# Railway startup script
echo "🚀 Starting Text-to-Video AI API on Railway..."

# Check if environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is not set"
    exit 1
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "❌ ELEVENLABS_API_KEY is not set"
    exit 1
fi

echo "✅ Environment variables are set"
echo "🌐 Starting Flask app on port $PORT"

# Start the application
python n8n_api.py
