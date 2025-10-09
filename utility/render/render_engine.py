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
                                TextClip, VideoFileClip)
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
    with open(filename, 'wb') as f:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

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
        # Download the video file
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        downloaded_files.append(video_filename)
        
        # Create VideoFileClip from the downloaded file
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.set_start(t1)
        video_clip = video_clip.set_end(t2)
        visual_clips.append(video_clip)
    
    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)

    for (t1, t2), text in timed_captions:
        text_clip = TextClip(txt=text, fontsize=100, color="white", stroke_width=3, stroke_color="black", method="label")
        text_clip = text_clip.set_start(t1)
        text_clip = text_clip.set_end(t2)
        text_clip = text_clip.set_position(["center", 800])
        visual_clips.append(text_clip)

    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')
    
    # Clean up downloaded files
    for video_filename in downloaded_files:
        try:
            os.remove(video_filename)
        except OSError:
            pass  # File may have already been cleaned up

    return OUTPUT_FILE_NAME
