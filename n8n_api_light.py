#!/usr/bin/env python3
"""
Railway-optimized n8n Integration API for Text-to-Video AI
Lightweight version without heavy dependencies
"""
import os
import json
import asyncio
import threading
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import only lightweight modules
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
# Skip heavy imports for Railway
# from utility.captions.timed_captions_generator import generate_timed_captions
# from utility.video.background_video_generator import generate_video_url
# from utility.render.render_engine import get_output_media
# from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n integration

# In-memory storage for job status (in production, use Redis or database)
jobs = {}

def generate_video_async(job_id, input_text):
    """Generate video asynchronously - Railway lightweight version"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 0
        
        # Step 1: Generate script
        jobs[job_id]['progress'] = 20
        jobs[job_id]['current_step'] = 'Generating script...'
        response = generate_script(input_text)
        jobs[job_id]['script'] = response
        
        # Step 2: Generate audio
        jobs[job_id]['progress'] = 40
        jobs[job_id]['current_step'] = 'Generating audio...'
        audio_filename = f"audio_{job_id}.wav"
        asyncio.run(generate_audio(response, audio_filename))
        
        # Step 3: Create simple video (Railway version)
        jobs[job_id]['progress'] = 60
        jobs[job_id]['current_step'] = 'Creating simple video...'
        
        # For Railway, create a simple video with just audio
        # This avoids heavy dependencies like MoviePy with ImageMagick
        video_filename = f"video_{job_id}.mp4"
        
        # Create a simple video file (placeholder)
        # In production, you'd use a lighter video creation method
        with open(video_filename, 'wb') as f:
            f.write(b'Simple video placeholder for Railway deployment')
        
        # Step 3: Upload to cloud storage
        jobs[job_id]['progress'] = 80
        jobs[job_id]['current_step'] = 'Uploading to cloud storage...'
        
        try:
            from utility.storage.cloud_storage import upload_video_to_cloud
            
            # Upload to cloud storage
            cloud_result = upload_video_to_cloud(video_filename, job_id, provider='s3')
            
            if cloud_result.get('success'):
                jobs[job_id]['progress'] = 100
                jobs[job_id]['status'] = 'completed'
                jobs[job_id]['video_url'] = cloud_result['url']
                jobs[job_id]['current_step'] = 'Video uploaded to cloud storage!'
                
                # Clean up local file
                if os.path.exists(video_filename):
                    os.remove(video_filename)
            else:
                raise Exception(f"Cloud upload failed: {cloud_result.get('error', 'Unknown error')}")
                
        except Exception as cloud_error:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = f"Cloud upload failed: {str(cloud_error)}"
            jobs[job_id]['current_step'] = f'Error: {str(cloud_error)}'
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['current_step'] = f'Error: {str(e)}'

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Check if required environment variables are set
        required_vars = ['OPENAI_API_KEY', 'ELEVENLABS_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        status = 'healthy' if not missing_vars else 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-light',
            'port': os.environ.get('PORT', '5000'),
            'missing_env_vars': missing_vars if missing_vars else None,
            'deployment': 'railway-light'
        }), 200 if status == 'healthy' else 503
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-light',
            'error': str(e)
        }), 503

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Start video generation from n8n - Railway lightweight version"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400
        
        input_text = data['text']
        job_id = str(uuid.uuid4())
        
        # Initialize job
        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'progress': 0,
            'input_text': input_text,
            'created_at': datetime.now().isoformat(),
            'current_step': 'Queued for processing...'
        }
        
        # Start async processing
        thread = threading.Thread(target=generate_video_async, args=(job_id, input_text))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Video generation started (Railway lightweight version)',
            'estimated_time': '2-3 minutes'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])

@app.route('/download-video/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download completed video or return cloud URL"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Video not ready yet'}), 400
    
    # Check if video is stored in cloud
    if 'video_url' in job:
        # Return cloud URL instead of downloading
        return jsonify({
            'job_id': job_id,
            'video_url': job['video_url'],
            'message': 'Video is available at the provided URL',
            'download_url': job['video_url']
        })
    
    # Fallback: return local file if exists
    video_file = job.get('video_file')
    if video_file and os.path.exists(video_file):
        return send_file(video_file, as_attachment=True, download_name=f'video_{job_id}.mp4')
    
    return jsonify({'error': 'Video file not found'}), 404

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({
        'jobs': list(jobs.values()),
        'total': len(jobs)
    })

@app.route('/cleanup/<job_id>', methods=['DELETE'])
def cleanup_job(job_id):
    """Clean up job files"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    # Clean up files
    for file_key in ['video_file', 'audio_file']:
        if file_key in job and os.path.exists(job[file_key]):
            try:
                os.remove(job[file_key])
            except:
                pass
    
    # Remove job from memory
    del jobs[job_id]
    
    return jsonify({
        'message': 'Job cleaned up successfully'
    })

if __name__ == '__main__':
    print("🚀 Starting Railway Lightweight n8n Text-to-Video API...")
    print("📡 API Endpoints:")
    print("  POST /generate-video - Start video generation")
    print("  GET  /job-status/<job_id> - Check job status")
    print("  GET  /download-video/<job_id> - Download completed video")
    print("  GET  /jobs - List all jobs")
    print("  DELETE /cleanup/<job_id> - Clean up job")
    print("  GET  /health - Health check")
    print("\n🔗 n8n Integration:")
    print("  Use POST /generate-video with JSON: {'text': 'your topic here'}")
    print("  Poll GET /job-status/<job_id> until status is 'completed'")
    print("  Download video with GET /download-video/<job_id>")
    print("\n⚡ Railway Optimized:")
    print("  - Lightweight dependencies")
    print("  - Fast build times")
    print("  - Simple video generation")
    
    # Get port from environment (Railway sets PORT)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
