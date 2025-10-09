#!/usr/bin/env python3
print("=== ULTRA SIMPLE TEST STARTING ===")
print("Python version:")
import sys
print(sys.version)

print("Environment:")
import os
print(f"PORT: {os.environ.get('PORT', 'NOT_SET')}")
print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'NOT_SET')}")

print("Testing Flask import...")
try:
    from flask import Flask, jsonify
    print("✅ Flask imported successfully")
    
    app = Flask(__name__)
    print("✅ Flask app created")
    
    @app.route('/')
    def home():
        return {"message": "Ultra simple test working"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "test": "ultra_simple"}
    
    print("✅ Routes defined")
    
    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 5000))
        print(f"🚀 Starting Flask server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("=== ULTRA SIMPLE TEST FAILED ===")
    sys.exit(1)