#!/usr/bin/env python3
print("🧪 MINIMAL TEST STARTING")

import os
import sys
print(f"Python: {sys.version}")
print(f"PORT: {os.environ.get('PORT', 'NOT_SET')}")

from flask import Flask
print("Flask imported")

app = Flask(__name__)
print("Flask app created")

@app.route('/')
def root():
    return {"message": "Minimal test working", "python_version": sys.version}

@app.route('/health')
def health():
    return {"status": "ok", "test": "minimal"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)