#!/usr/bin/env python3
"""
n8n Integration API for Text-to-Video AI
Receives text from n8n and returns video when ready
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

# Import video generation modules
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n integration

# In-memory storage for job status (in production, use Redis or database)
jobs = {}

def generate_video_async(job_id, input_text):
    """Generate video asynchronously"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 0
        
        # Step 1: Generate script
        jobs[job_id]['progress'] = 10
        jobs[job_id]['current_step'] = 'Generating script...'
        response = generate_script(input_text)
        jobs[job_id]['script'] = response
        
        # Step 2: Generate audio
        jobs[job_id]['progress'] = 25
        jobs[job_id]['current_step'] = 'Generating audio...'
        audio_filename = f"audio_{job_id}.wav"
        asyncio.run(generate_audio(response, audio_filename))
        
        # Step 3: Generate captions
        jobs[job_id]['progress'] = 40
        jobs[job_id]['current_step'] = 'Generating captions...'
        timed_captions = generate_timed_captions(audio_filename)
        
        # Step 4: Generate video search queries
        jobs[job_id]['progress'] = 55
        jobs[job_id]['current_step'] = 'Finding background videos...'
        search_terms = getVideoSearchQueriesTimed(response, timed_captions)
        
        # Step 5: Get background videos
        jobs[job_id]['progress'] = 70
        jobs[job_id]['current_step'] = 'Downloading videos...'
        background_video_urls = None
        if search_terms is not None:
            background_video_urls = generate_video_url(search_terms, "pexel")
            background_video_urls = merge_empty_intervals(background_video_urls)
        
        # Step 6: Render final video
        jobs[job_id]['progress'] = 85
        jobs[job_id]['current_step'] = 'Rendering video...'
        video_filename = f"rendered_video_{job_id}.mp4"
        
        if background_video_urls is not None:
            video = get_output_media(audio_filename, timed_captions, background_video_urls, "pexel")
            if video:
                # Rename the output file to include job ID
                os.rename("rendered_video.mp4", video_filename)
        
        # Complete
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['current_step'] = 'Video ready!'
        jobs[job_id]['video_filename'] = video_filename
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        # Clean up temporary audio file
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
            
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['current_step'] = f'Error: {str(e)}'

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Start video generation from n8n"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        input_text = data['text']
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'progress': 0,
            'current_step': 'Starting video generation...',
            'input_text': input_text,
            'created_at': datetime.now().isoformat(),
            'video_filename': None,
            'error': None
        }
        
        # Start video generation in background thread
        thread = threading.Thread(target=generate_video_async, args=(job_id, input_text))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Video generation started',
            'check_status_url': f'/job-status/{job_id}',
            'download_url': f'/download-video/{job_id}'
        }), 202
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to start video generation: {str(e)}'
        }), 500

@app.route('/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of video generation job"""
    if job_id not in jobs:
        return jsonify({
            'error': 'Job not found'
        }), 404
    
    job = jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'current_step': job['current_step'],
        'created_at': job['created_at']
    }
    
    if job['status'] == 'completed':
        response['completed_at'] = job['completed_at']
        response['download_url'] = f'/download-video/{job_id}'
        response['video_filename'] = job['video_filename']
    elif job['status'] == 'error':
        response['error'] = job['error']
    
    return jsonify(response)

@app.route('/download-video/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download completed video"""
    if job_id not in jobs:
        return jsonify({
            'error': 'Job not found'
        }), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({
            'error': 'Video not ready yet',
            'status': job['status']
        }), 400
    
    video_filename = job['video_filename']
    
    if not os.path.exists(video_filename):
        return jsonify({
            'error': 'Video file not found'
        }), 404
    
    return send_file(
        video_filename,
        as_attachment=True,
        download_name=f'video_{job_id}.mp4',
        mimetype='video/mp4'
    )

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({
        'jobs': list(jobs.values()),
        'total': len(jobs)
    })

@app.route('/cleanup/<job_id>', methods=['DELETE'])
def cleanup_job(job_id):
    """Clean up completed job and video file"""
    if job_id not in jobs:
        return jsonify({
            'error': 'Job not found'
        }), 404
    
    job = jobs[job_id]
    
    # Remove video file if it exists
    if job.get('video_filename') and os.path.exists(job['video_filename']):
        os.remove(job['video_filename'])
    
    # Remove job from memory
    del jobs[job_id]
    
    return jsonify({
        'message': 'Job cleaned up successfully'
    })

if __name__ == '__main__':
    print("🚀 Starting n8n Text-to-Video API...")
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
    
    # Get port from environment (Railway sets PORT)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
