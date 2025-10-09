#!/usr/bin/env python3
"""
Cloud Storage Utility for Text-to-Video AI
Supports AWS S3, Google Cloud Storage, and other cloud providers
"""
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudStorage:
    def __init__(self, provider='s3'):
        """
        Initialize cloud storage client
        
        Args:
            provider (str): Storage provider ('s3', 'gcs', 'cloudinary')
        """
        self.provider = provider
        self.client = None
        self.bucket_name = os.getenv('CLOUD_STORAGE_BUCKET', 'text-to-video-ai')
        
        if provider == 's3':
            self._init_s3()
        elif provider == 'gcs':
            self._init_gcs()
        elif provider == 'cloudinary':
            self._init_cloudinary()
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")
    
    def _init_s3(self):
        """Initialize S3-compatible client (AWS S3 or DigitalOcean Spaces)"""
        try:
            # Check if using DigitalOcean Spaces
            spaces_endpoint = os.getenv('SPACES_ENDPOINT')
            if spaces_endpoint:
                # DigitalOcean Spaces configuration
                self.client = boto3.client(
                    's3',
                    endpoint_url=spaces_endpoint,
                    aws_access_key_id=os.getenv('SPACES_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('SPACES_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('SPACES_REGION', 'nyc3')
                )
                logger.info("DigitalOcean Spaces client initialized successfully")
            else:
                # AWS S3 configuration
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
                logger.info("AWS S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def _init_gcs(self):
        """Initialize Google Cloud Storage client"""
        try:
            from google.cloud import storage
            self.client = storage.Client()
            logger.info("Google Cloud Storage client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    def _init_cloudinary(self):
        """Initialize Cloudinary client"""
        try:
            import cloudinary
            import cloudinary.uploader
            
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
            self.client = cloudinary.uploader
            logger.info("Cloudinary client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudinary client: {e}")
            raise
    
    def upload_file(self, local_file_path, remote_file_name=None, public=True):
        """
        Upload a file to cloud storage
        
        Args:
            local_file_path (str): Path to local file
            remote_file_name (str): Name for remote file (optional)
            public (bool): Whether to make file publicly accessible
            
        Returns:
            dict: Upload result with URL and metadata
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        if not remote_file_name:
            remote_file_name = os.path.basename(local_file_path)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_file_name = f"{timestamp}_{remote_file_name}"
        
        try:
            if self.provider == 's3':
                return self._upload_to_s3(local_file_path, remote_file_name, public)
            elif self.provider == 'gcs':
                return self._upload_to_gcs(local_file_path, remote_file_name, public)
            elif self.provider == 'cloudinary':
                return self._upload_to_cloudinary(local_file_path, remote_file_name, public)
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def _upload_to_s3(self, local_file_path, remote_file_name, public):
        """Upload file to AWS S3"""
        try:
            # Upload file
            extra_args = {}
            if public:
                extra_args['ACL'] = 'public-read'
            
            self.client.upload_file(
                local_file_path, 
                self.bucket_name, 
                remote_file_name,
                ExtraArgs=extra_args
            )
            
            # Generate public URL
            if public:
                # Check if using DigitalOcean Spaces
                spaces_endpoint = os.getenv('SPACES_ENDPOINT')
                if spaces_endpoint:
                    # DigitalOcean Spaces URL format
                    url = f"{spaces_endpoint}/{remote_file_name}"
                else:
                    # AWS S3 URL format
                    url = f"https://{self.bucket_name}.s3.amazonaws.com/{remote_file_name}"
            else:
                # Generate presigned URL for private files
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': remote_file_name},
                    ExpiresIn=3600  # 1 hour
                )
            
            return {
                'success': True,
                'url': url,
                'bucket': self.bucket_name,
                'key': remote_file_name,
                'provider': 's3'
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise
    
    def _upload_to_gcs(self, local_file_path, remote_file_name, public):
        """Upload file to Google Cloud Storage"""
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(remote_file_name)
            
            blob.upload_from_filename(local_file_path)
            
            if public:
                blob.make_public()
                url = blob.public_url
            else:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(hours=1),
                    method="GET"
                )
            
            return {
                'success': True,
                'url': url,
                'bucket': self.bucket_name,
                'key': remote_file_name,
                'provider': 'gcs'
            }
            
        except Exception as e:
            logger.error(f"GCS upload error: {e}")
            raise
    
    def _upload_to_cloudinary(self, local_file_path, remote_file_name, public):
        """Upload file to Cloudinary"""
        try:
            result = self.client.upload(
                local_file_path,
                public_id=remote_file_name,
                resource_type="video" if local_file_path.endswith(('.mp4', '.mov', '.avi')) else "auto"
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'provider': 'cloudinary'
            }
            
        except Exception as e:
            logger.error(f"Cloudinary upload error: {e}")
            raise
    
    def delete_file(self, remote_file_name):
        """
        Delete a file from cloud storage
        
        Args:
            remote_file_name (str): Name of remote file to delete
            
        Returns:
            bool: True if successful
        """
        try:
            if self.provider == 's3':
                self.client.delete_object(Bucket=self.bucket_name, Key=remote_file_name)
            elif self.provider == 'gcs':
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(remote_file_name)
                blob.delete()
            elif self.provider == 'cloudinary':
                self.client.destroy(remote_file_name)
            
            logger.info(f"Successfully deleted {remote_file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

def upload_video_to_cloud(local_video_path, job_id, provider='s3'):
    """
    Convenience function to upload video to cloud storage
    
    Args:
        local_video_path (str): Path to local video file
        job_id (str): Job ID for naming
        provider (str): Cloud storage provider
        
    Returns:
        dict: Upload result
    """
    try:
        storage = CloudStorage(provider=provider)
        remote_name = f"videos/video_{job_id}.mp4"
        result = storage.upload_file(local_video_path, remote_name, public=True)
        
        logger.info(f"Video uploaded successfully: {result['url']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to upload video: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    # Test the cloud storage functionality
    print("Testing Cloud Storage...")
    
    # This would be used in your video generation workflow
    # result = upload_video_to_cloud("test_video.mp4", "test_job_123")
    # print(f"Upload result: {result}")
