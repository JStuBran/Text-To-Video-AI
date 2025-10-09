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
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Create a real video file using MoviePy
        try:
            # Import MoviePy with error handling
            try:
                from moviepy.editor import ColorClip, AudioFileClip, CompositeVideoClip
                import tempfile
                moviepy_available = True
            except ImportError as import_error:
                logger.error(f"MoviePy import failed: {import_error}")
                logger.error(f"Import error details: {str(import_error)}")
                moviepy_available = False
            except Exception as import_error:
                logger.error(f"MoviePy import failed with unexpected error: {import_error}")
                logger.error(f"Error type: {type(import_error)}")
                moviepy_available = False
            
            if moviepy_available:
                # Create a simple video with the generated audio
                audio_clip = AudioFileClip(audio_filename)
                duration = audio_clip.duration
                
                # Create a colored background video
                video_clip = ColorClip(size=(1920, 1080), color=(0, 100, 200), duration=duration)
                
                # Combine video and audio
                final_video = CompositeVideoClip([video_clip.set_audio(audio_clip)])
                
                # Write the video file
                final_video.write_videofile(
                    video_filename,
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                # Clean up
                final_video.close()
                audio_clip.close()
            else:
                raise ImportError("MoviePy not available")
            
        except Exception as video_error:
            # Fallback: create audio-only MP4 using ffmpeg if available
            logger.warning(f"Video creation failed: {video_error}")
            try:
                import subprocess
                
                # Get audio duration first
                duration_result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', 
                    audio_filename
                ], capture_output=True, text=True, timeout=10)
                
                duration = 30  # default fallback duration
                if duration_result.returncode == 0:
                    try:
                        import json
                        probe_data = json.loads(duration_result.stdout)
                        duration = float(probe_data['format']['duration'])
                    except:
                        pass
                
                # Create MP4 with colored background video + audio using system ffmpeg
                result = subprocess.run([
                    'ffmpeg', 
                    '-f', 'lavfi', '-i', f'color=c=blue:size=1920x1080:duration={duration}:rate=24',
                    '-i', audio_filename,
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-b:v', '1000k', '-b:a', '128k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    video_filename, '-y'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info("Created video with blue background using system ffmpeg")
                else:
                    logger.warning(f"ffmpeg video creation failed: {result.stderr}")
                    # Fallback to audio-only MP4
                    result = subprocess.run([
                        'ffmpeg', '-i', audio_filename, '-c:a', 'aac', 
                        '-b:a', '128k', video_filename, '-y'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        logger.info("Created audio-only MP4 using system ffmpeg")
                    else:
                        raise Exception(f"ffmpeg failed: {result.stderr}")
                        
            except Exception as ffmpeg_error:
                logger.warning(f"ffmpeg fallback failed: {ffmpeg_error}")
                # Final fallback: just copy the audio file as the "video"
                import shutil
                shutil.copy2(audio_filename, video_filename)
        
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
