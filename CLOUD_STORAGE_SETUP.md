# Cloud Storage Setup Guide

This guide shows you how to set up cloud storage for your Text-to-Video AI application, allowing you to store videos in the cloud while using Railway for hosting.

## 🎯 **Why Use Cloud Storage?**

- **Persistent Storage:** Videos are stored permanently in the cloud
- **Scalability:** Handle unlimited video storage
- **Performance:** Fast global CDN delivery
- **Cost-Effective:** Pay only for what you use
- **Railway Compatible:** Works perfectly with Railway's ephemeral storage

## ☁️ **Supported Cloud Providers**

### 1. **DigitalOcean Spaces (Recommended)**
- S3-compatible and cost-effective
- $5/month for 250GB + 1TB bandwidth
- Excellent performance and global CDN
- Simple pricing, no complex tiers

### 2. **AWS S3**
- Most popular and reliable
- Excellent performance and pricing
- Easy integration

### 3. **Google Cloud Storage**
- Great alternative to S3
- Competitive pricing
- Good performance

### 4. **Cloudinary**
- Video-focused platform
- Built-in video processing
- CDN included

## 🚀 **Quick Setup: DigitalOcean Spaces**

### **Step 1: Create DigitalOcean Space**

1. Go to [DigitalOcean Spaces](https://cloud.digitalocean.com/spaces)
2. Click **"Create a Space"**
3. **Space name:** `text-to-video-ai`
4. **Region:** Choose closest to your users
5. **File listing:** Public
6. Click **"Create a Space"**

### **Step 2: Generate Access Keys**

1. Go to [Spaces Keys](https://cloud.digitalocean.com/account/api/spaces)
2. Click **"Generate New Key"**
3. **Key name:** `text-to-video-ai`
4. **Save both Access Key and Secret Key**

### **Step 3: Set Environment Variables**

Add these to your **Railway environment variables**:

```bash
# DigitalOcean Spaces Configuration
SPACES_ENDPOINT=https://text-to-video-ai.nyc3.digitaloceanspaces.com
SPACES_ACCESS_KEY_ID=DO00ABCDEFGHIJKLMNOP
SPACES_SECRET_ACCESS_KEY=your-secret-key-here
SPACES_REGION=nyc3
CLOUD_STORAGE_BUCKET=text-to-video-ai
CLOUD_STORAGE_PROVIDER=s3
```

## 🚀 **Alternative: AWS S3**

### **Step 1: Create AWS S3 Bucket**

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click **"Create bucket"**
3. **Bucket name:** `text-to-video-ai` (or your preferred name)
4. **Region:** Choose closest to your users
5. **Public access:** Enable for public video access
6. Click **"Create bucket"**

### **Step 2: Create IAM User**

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **"Users"** → **"Create user"**
3. **Username:** `text-to-video-ai-user`
4. **Access type:** Programmatic access
5. **Permissions:** Attach policy `AmazonS3FullAccess`
6. **Save the Access Key ID and Secret Access Key**

### **Step 3: Set Environment Variables**

Add these to your **Railway environment variables**:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1
CLOUD_STORAGE_BUCKET=text-to-video-ai
CLOUD_STORAGE_PROVIDER=s3
```

### **Step 4: Test the Setup**

Your Railway deployment will now:
1. Generate videos locally
2. Upload them to S3
3. Return the S3 URL
4. Clean up local files

## 🔧 **Alternative: Google Cloud Storage**

### **Step 1: Create GCS Bucket**

1. Go to [Google Cloud Console](https://console.cloud.google.com/storage)
2. Click **"Create bucket"**
3. **Name:** `text-to-video-ai`
4. **Location:** Choose closest region
5. **Storage class:** Standard
6. **Access control:** Uniform

### **Step 2: Create Service Account**

1. Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click **"Create Service Account"**
3. **Name:** `text-to-video-ai-service`
4. **Role:** Storage Admin
5. **Create and download JSON key**

### **Step 3: Set Environment Variables**

```bash
# Google Cloud Storage Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
CLOUD_STORAGE_BUCKET=text-to-video-ai
CLOUD_STORAGE_PROVIDER=gcs
```

## 🎬 **Alternative: Cloudinary**

### **Step 1: Create Cloudinary Account**

1. Go to [Cloudinary](https://cloudinary.com/)
2. Sign up for free account
3. Get your credentials from dashboard

### **Step 2: Set Environment Variables**

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUD_STORAGE_PROVIDER=cloudinary
```

## 📋 **Environment Variables Summary**

Add these to your **Railway project**:

### **For AWS S3:**
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
CLOUD_STORAGE_BUCKET=text-to-video-ai
CLOUD_STORAGE_PROVIDER=s3
```

### **For Google Cloud:**
```bash
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json
CLOUD_STORAGE_BUCKET=text-to-video-ai
CLOUD_STORAGE_PROVIDER=gcs
```

### **For Cloudinary:**
```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-secret
CLOUD_STORAGE_PROVIDER=cloudinary
```

## 🔄 **How It Works**

1. **Video Generation:** Railway generates video locally
2. **Cloud Upload:** Video is uploaded to your chosen cloud provider
3. **URL Return:** API returns the cloud URL instead of local file
4. **Cleanup:** Local files are deleted to save space
5. **Access:** Videos are accessible via cloud URLs

## 📊 **Response Format**

Your API will now return:

```json
{
  "job_id": "abc123",
  "status": "completed",
  "video_url": "https://your-bucket.s3.amazonaws.com/videos/video_abc123.mp4",
  "message": "Video uploaded to cloud storage!"
}
```

## 💰 **Cost Estimates**

### **AWS S3:**
- **Storage:** $0.023/GB/month
- **Requests:** $0.0004/1000 requests
- **Transfer:** First 1GB free, then $0.09/GB

### **Google Cloud:**
- **Storage:** $0.020/GB/month
- **Requests:** $0.0005/1000 requests
- **Transfer:** First 1GB free, then $0.12/GB

### **Cloudinary:**
- **Free tier:** 25GB storage, 25GB bandwidth
- **Paid:** $89/month for 100GB storage, 100GB bandwidth

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **Permission Denied:**
   - Check AWS credentials
   - Verify bucket permissions
   - Ensure IAM user has S3 access

2. **Upload Fails:**
   - Check internet connection
   - Verify bucket exists
   - Check file size limits

3. **URL Not Accessible:**
   - Enable public read access on bucket
   - Check CORS settings
   - Verify bucket policy

### **Debug Commands:**

```bash
# Test AWS credentials
aws s3 ls s3://your-bucket-name

# Test upload
aws s3 cp test.mp4 s3://your-bucket-name/
```

## 🎯 **Next Steps**

1. **Choose your cloud provider** (AWS S3 recommended)
2. **Set up the bucket and credentials**
3. **Add environment variables to Railway**
4. **Deploy and test**
5. **Monitor usage and costs**

Your videos will now be stored permanently in the cloud and accessible via public URLs!
