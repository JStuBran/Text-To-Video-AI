import time
import os
import tempfile
import zipfile
import platform
import subprocess
import requests

# Import MoviePy with comprehensive error handling
try:
    # Test basic import first
    import moviepy
    print(f"MoviePy package found at: {moviepy.__file__}")
    print(f"MoviePy version: {moviepy.__version__}")
    
    # Import required modules
    from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                                TextClip, VideoFileClip, ColorClip)
    from moviepy.audio.fx.audio_loop import audio_loop
    from moviepy.audio.fx.audio_normalize import audio_normalize
    MOVIEPY_AVAILABLE = True
    print("MoviePy successfully imported")
except ImportError as e:
    print(f"CRITICAL: MoviePy import failed - {e}")
    print(f"Python path: {os.path.dirname(__file__)}")
    import sys
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print("Available packages:")
    try:
        import pkg_resources
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        print(f"Total packages: {len(installed_packages)}")
        moviepy_packages = [p for p in installed_packages if 'moviepy' in p.lower()]
        print(f"MoviePy-related packages: {moviepy_packages}")
    except:
        print("Could not list installed packages")
    MOVIEPY_AVAILABLE = False

def download_file(url, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        print(f"Downloading video from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        
        if len(response.content) == 0:
            raise ValueError(f"Downloaded file is empty: {url}")
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Verify the file was written and has content
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            raise ValueError(f"Failed to write video file or file is empty: {filename}")
            
        print(f"Successfully downloaded {len(response.content)} bytes to {filename}")
        return True
        
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy is required for video rendering but is not available. Please check your deployment configuration.")
    
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    print(magick_path)
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    visual_clips = []
    downloaded_files = []
    for (t1, t2), video_url in background_video_data:
        if video_url is None:
            print(f"Skipping empty video URL for segment {t1}-{t2}")
            continue
            
        # Download the video file
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_success = download_file(video_url, video_filename)
        
        if not download_success:
            print(f"Failed to download video for segment {t1}-{t2}, skipping")
            continue
            
        downloaded_files.append(video_filename)
        
        try:
            # Create VideoFileClip from the downloaded file
            video_clip = VideoFileClip(video_filename)
            
            # Ensure standard dimensions and resize if needed
            if video_clip.w != 1920 or video_clip.h != 1080:
                video_clip = video_clip.resize((1920, 1080))
                
            video_clip = video_clip.set_start(t1)
            video_clip = video_clip.set_end(t2)
            visual_clips.append(video_clip)
            print(f"Successfully processed video clip for segment {t1}-{t2} (size: {video_clip.w}x{video_clip.h})")
        except Exception as e:
            print(f"Failed to process video file {video_filename} for segment {t1}-{t2}: {e}")
            # Remove the corrupted file from the list so it gets cleaned up
            if video_filename in downloaded_files:
                downloaded_files.remove(video_filename)
            continue
    
    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)

    # Skip text overlays to avoid ImageMagick font issues
    # Audio narration provides the content, video clips provide visuals
    print(f"Skipping text overlays for {len(timed_captions)} caption segments")

    # If no video clips were successfully processed, create a simple colored background
    video_clips_count = sum(1 for clip in visual_clips if hasattr(clip, 'filename'))
    if video_clips_count == 0:
        print("No video clips available, creating colored background")
        duration = audio_file_clip.duration
        background = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
        visual_clips.insert(0, background)

    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    # Check if encoder is available with comprehensive fallback
    def get_available_codec():
        try:
            # Check available encoders
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            encoders_output = result.stdout
            print(f"Available encoders check completed. Return code: {result.returncode}")
            
            # Priority order: libx264 > mpeg4 > libxvid > basic fallback
            if 'libx264' in encoders_output:
                print("Using libx264 codec")
                return 'libx264'
            elif 'mpeg4' in encoders_output:
                print("Using mpeg4 codec (libx264 not available)")
                return 'mpeg4'
            elif 'libxvid' in encoders_output:
                print("Using libxvid codec (libx264 and mpeg4 not available)")
                return 'libxvid'
            else:
                print("No preferred codecs found, using basic H.264")
                return 'h264'
                
        except Exception as e:
            print(f"Error checking encoders: {e}")
            print("Falling back to basic codec")
            return 'mpeg4'
    
    # Choose codec based on availability
    video_codec = get_available_codec()

    # Simplified approach: Use first video only and add audio
    if visual_clips:
        # Take the first video clip and extend it for the full duration
        main_video = visual_clips[0]
        if hasattr(main_video, 'filename'):  # It's a video file
            # Loop the video to match audio duration
            audio_duration = audio_file_clip.duration
            video_duration = main_video.duration
            
            if video_duration < audio_duration:
                # Loop the video to fill the audio duration
                loops_needed = int(audio_duration / video_duration) + 1
                main_video = main_video.loop(loops_needed)
            
            # Trim to exact audio length
            main_video = main_video.subclip(0, audio_duration)
            
            # Add audio
            final_video = main_video.set_audio(audio_file_clip)
            
            # Simple encoding with codec detection and error handling
            print(f"Attempting to write video with codec: {video_codec}")
            try:
                final_video.write_videofile(OUTPUT_FILE_NAME, 
                                          codec=video_codec,
                                          audio_codec='aac' if video_codec != 'h264' else None,
                                          verbose=True,
                                          logger='bar')
            except Exception as e:
                print(f"First encoding attempt failed: {e}")
                print("Trying with minimal parameters...")
                final_video.write_videofile(OUTPUT_FILE_NAME, 
                                          codec='mpeg4',
                                          verbose=True)
        else:
            # Fallback to colored background if no real video
            duration = audio_file_clip.duration
            background = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
            final_video = background.set_audio(audio_file_clip)
            print(f"Writing background video with codec: {video_codec}")
            try:
                final_video.write_videofile(OUTPUT_FILE_NAME, 
                                          codec=video_codec,
                                          audio_codec='aac' if video_codec != 'h264' else None,
                                          verbose=True,
                                          logger='bar')
            except Exception as e:
                print(f"Background video encoding failed: {e}")
                final_video.write_videofile(OUTPUT_FILE_NAME, 
                                          codec='mpeg4',
                                          verbose=True)
    else:
        # No video clips, create simple background with audio
        duration = audio_file_clip.duration
        background = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
        final_video = background.set_audio(audio_file_clip)
        print(f"Writing audio-only video with codec: {video_codec}")
        try:
            final_video.write_videofile(OUTPUT_FILE_NAME, 
                                      codec=video_codec,
                                      audio_codec='aac' if video_codec != 'h264' else None,
                                      verbose=True,
                                      logger='bar')
        except Exception as e:
            print(f"Audio-only video encoding failed: {e}")
            final_video.write_videofile(OUTPUT_FILE_NAME, 
                                      codec='mpeg4',
                                      verbose=True)
    
    # Clean up downloaded files
    for video_filename in downloaded_files:
        try:
            os.remove(video_filename)
        except OSError:
            pass  # File may have already been cleaned up

    return OUTPUT_FILE_NAME
