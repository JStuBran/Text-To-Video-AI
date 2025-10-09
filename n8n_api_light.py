#!/usr/bin/env python3
"""
Railway-optimized n8n Integration API for Text-to-Video AI  
Lightweight version without heavy dependencies
"""
print("🚀 Starting Text-to-Video AI application...")
import os
import json
import asyncio
import threading
import uuid
import logging
from datetime import datetime
print("✅ Core imports successful")

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
print("✅ Flask imports successful")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("✅ Logging configured")

# Load environment variables
load_dotenv()
print("✅ Environment variables loaded")

# Import lightweight modules with error handling
print("📦 Loading utility modules...")
try:
    print("  • Importing script generator...")
    from utility.script.script_generator import generate_script
    SCRIPT_AVAILABLE = True
    print("  ✅ Script generator loaded")
except ImportError as e:
    print(f"  ❌ Script generator failed: {e}")
    logger.error(f"Script generator import failed: {e}")
    SCRIPT_AVAILABLE = False
    def generate_script(*args): raise ImportError("Script generator not available")

try:
    print("  • Importing audio generator...")
    from utility.audio.audio_generator import generate_audio
    AUDIO_AVAILABLE = True
    print("  ✅ Audio generator loaded")
except ImportError as e:
    print(f"  ❌ Audio generator failed: {e}")
    logger.error(f"Audio generator import failed: {e}")
    AUDIO_AVAILABLE = False
    def generate_audio(*args): raise ImportError("Audio generator not available")

# Full pipeline imports - required for proper text-to-video functionality
print("🎬 Loading full text-to-video pipeline...")
try:
    print("  • Importing timed captions generator...")
    from utility.captions.timed_captions_generator import generate_timed_captions
    print("  • Importing video background generator...")
    from utility.video.background_video_generator import generate_video_url
    print("  • Importing render engine...")
    from utility.render.render_engine import get_output_media
    print("  • Importing video search query generator...")
    from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
    PIPELINE_AVAILABLE = True
    print("  ✅ Full text-to-video pipeline loaded successfully")
    logger.info("Full text-to-video pipeline loaded successfully")
except ImportError as e:
    print(f"  ❌ Pipeline import failed: {e}")
    logger.error(f"CRITICAL: Pipeline import failed - {e}")
    PIPELINE_AVAILABLE = False
    
    # Define dummy functions to prevent crashes
    def generate_timed_captions(*args): raise ImportError("Pipeline not available")
    def generate_video_url(*args): raise ImportError("Pipeline not available") 
    def get_output_media(*args): raise ImportError("Pipeline not available")
    def getVideoSearchQueriesTimed(*args): raise ImportError("Pipeline not available")
    def merge_empty_intervals(*args): raise ImportError("Pipeline not available")

print("🌐 Creating Flask application...")
app = Flask(__name__)
CORS(app)  # Enable CORS for n8n integration
print("✅ Flask application created successfully")

# In-memory storage for job status (in production, use Redis or database)
jobs = {}

def generate_video_async(job_id, input_text):
    """Generate video asynchronously - Railway lightweight version"""
    try:
        # Check if pipeline is available before starting
        if not PIPELINE_AVAILABLE:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = 'Full pipeline not available - MoviePy import failed'
            jobs[job_id]['current_step'] = 'Error: Pipeline dependencies not available'
            logger.error(f"Pipeline unavailable for job {job_id}")
            return
            
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
        
        # Step 3: Create professional video with Pexels clips
        jobs[job_id]['progress'] = 60
        jobs[job_id]['current_step'] = 'Creating professional video...'
        video_filename = f"video_{job_id}.mp4"
        
        # Execute full text-to-video pipeline (no fallbacks)
        logger.info("Using full text-to-video pipeline")
        
        # Generate timed captions from audio
        jobs[job_id]['progress'] = 65
        jobs[job_id]['current_step'] = 'Generating timed captions...'
        timed_captions = generate_timed_captions(audio_filename)
        logger.info(f"Generated {len(timed_captions)} timed captions")
        
        # Generate video search queries based on script + captions
        jobs[job_id]['progress'] = 70
        jobs[job_id]['current_step'] = 'Generating video search queries...'
        timed_video_searches = getVideoSearchQueriesTimed(response, timed_captions)
        logger.info(f"Generated {len(timed_video_searches)} video search queries")
        
        # Search and download Pexels videos
        jobs[job_id]['progress'] = 75
        jobs[job_id]['current_step'] = 'Searching Pexels for video clips...'
        background_video_data = generate_video_url(timed_video_searches, "pexel")
        background_video_data = merge_empty_intervals(background_video_data)
        logger.info(f"Found {len(background_video_data)} video clips from Pexels")
        
        # Render final video with clips + audio + captions
        jobs[job_id]['progress'] = 85
        jobs[job_id]['current_step'] = 'Rendering final video...'
        video_filename = get_output_media(audio_filename, timed_captions, background_video_data, "pexel")
        logger.info("Professional video rendered successfully with Pexels clips")
        
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
        logger.error(f"Text-to-video pipeline failed for job {job_id}: {str(e)}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Check if required environment variables are set
        required_vars = ['OPENAI_API_KEY', 'ELEVENLABS_API_KEY', 'PEXELS_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        # Check if all pipeline dependencies are available
        pipeline_issues = []
        if not PIPELINE_AVAILABLE:
            pipeline_issues.append("Full pipeline not available - check MoviePy installation")
        
        try:
            import whisper_timestamped
        except ImportError:
            pipeline_issues.append("whisper-timestamped not available")
        
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            pipeline_issues.append("moviepy not available")
        
        status = 'healthy' if not missing_vars and not pipeline_issues and PIPELINE_AVAILABLE else 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-full-pipeline',
            'port': os.environ.get('PORT', '5000'),
            'missing_env_vars': missing_vars if missing_vars else None,
            'pipeline_issues': pipeline_issues if pipeline_issues else None,
            'deployment': 'railway-full-pipeline'
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
    print("🚀 Starting Railway Pro n8n Text-to-Video API...")
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
