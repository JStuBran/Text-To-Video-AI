#!/usr/bin/env python3
"""
Test script for n8n API integration
"""
import requests
import time
import json

API_BASE = "http://localhost:5000"

def test_api():
    """Test the n8n API integration"""
    print("🧪 Testing n8n API Integration...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Start video generation
    print("\n2. Starting video generation...")
    test_text = "Amazing facts about dolphins"
    
    try:
        response = requests.post(
            f"{API_BASE}/generate-video",
            json={"text": test_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['job_id']
            print(f"✅ Video generation started")
            print(f"   Job ID: {job_id}")
            print(f"   Status URL: {data['check_status_url']}")
        else:
            print(f"❌ Failed to start video generation: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error starting video generation: {e}")
        return
    
    # Test 3: Poll job status
    print("\n3. Polling job status...")
    max_attempts = 60  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE}/job-status/{job_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                progress = data['progress']
                current_step = data['current_step']
                
                print(f"   Status: {status} | Progress: {progress}% | Step: {current_step}")
                
                if status == 'completed':
                    print("✅ Video generation completed!")
                    print(f"   Download URL: {data['download_url']}")
                    break
                elif status == 'error':
                    print(f"❌ Video generation failed: {data.get('error', 'Unknown error')}")
                    return
                else:
                    time.sleep(5)  # Wait 5 seconds before next check
                    attempt += 1
            else:
                print(f"❌ Failed to get job status: {response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Error checking job status: {e}")
            return
    
    if attempt >= max_attempts:
        print("⏰ Timeout waiting for video generation")
        return
    
    # Test 4: Download video
    print("\n4. Testing video download...")
    try:
        response = requests.get(f"{API_BASE}/download-video/{job_id}")
        
        if response.status_code == 200:
            filename = f"test_video_{job_id}.mp4"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Video downloaded successfully: {filename}")
            print(f"   File size: {len(response.content)} bytes")
        else:
            print(f"❌ Failed to download video: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
    
    print("\n🎉 n8n API integration test completed!")

if __name__ == "__main__":
    test_api()
