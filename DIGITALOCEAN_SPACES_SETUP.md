# DigitalOcean Spaces Setup Guide

This guide shows you how to set up DigitalOcean Spaces for your Text-to-Video AI application. DigitalOcean Spaces is S3-compatible, cost-effective, and has excellent performance.

## 🌊 **Why DigitalOcean Spaces?**

- **S3-Compatible:** Works with existing S3 tools and libraries
- **Cost-Effective:** $5/month for 250GB storage + 1TB bandwidth
- **Global CDN:** Fast delivery worldwide
- **Simple Pricing:** No complex tiered pricing
- **Great Performance:** Fast upload and download speeds

## 🚀 **Step-by-Step Setup**

### **Step 1: Create DigitalOcean Account**

1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Sign up for an account
3. Verify your email and add payment method

### **Step 2: Create a Space**

1. Go to [DigitalOcean Control Panel](https://cloud.digitalocean.com/spaces)
2. Click **"Create a Space"**
3. **Choose a datacenter region:**
   - `nyc3` (New York)
   - `sfo3` (San Francisco)
   - `ams3` (Amsterdam)
   - `sgp1` (Singapore)
   - Choose the one closest to your users
4. **Space name:** `text-to-video-ai` (must be globally unique)
5. **File listing:** **Public** (for video access)
6. Click **"Create a Space"**

### **Step 3: Generate Spaces Access Keys**

1. Go to [Spaces Keys](https://cloud.digitalocean.com/account/api/spaces)
2. Click **"Generate New Key"**
3. **Key name:** `text-to-video-ai`
4. Click **"Generate Key"**
5. **Save both keys:**
   - **Access Key** (starts with `DO...`)
   - **Secret Key** (long random string)

### **Step 4: Get Your Space Endpoint**

Your Space endpoint will be:
```
https://text-to-video-ai.nyc3.digitaloceanspaces.com
```

Replace:
- `text-to-video-ai` with your space name
- `nyc3` with your chosen region

### **Step 5: Set Railway Environment Variables**

Add these to your **Railway project environment variables**:

```bash
# DigitalOcean Spaces Configuration
SPACES_ENDPOINT=https://text-to-video-ai.nyc3.digitaloceanspaces.com
SPACES_ACCESS_KEY_ID=DO00ABCDEFGHIJKLMNOP
SPACES_SECRET_ACCESS_KEY=your-secret-key-here
SPACES_REGION=nyc3
CLOUD_STORAGE_BUCKET=text-to-video-ai
CLOUD_STORAGE_PROVIDER=s3
```

## 📋 **Environment Variables Reference**

| Variable | Description | Example |
|----------|-------------|---------|
| `SPACES_ENDPOINT` | Your Space URL | `https://text-to-video-ai.nyc3.digitaloceanspaces.com` |
| `SPACES_ACCESS_KEY_ID` | Your Access Key | `DO00ABCDEFGHIJKLMNOP` |
| `SPACES_SECRET_ACCESS_KEY` | Your Secret Key | `abc123def456...` |
| `SPACES_REGION` | Your Space region | `nyc3` |
| `CLOUD_STORAGE_BUCKET` | Your Space name | `text-to-video-ai` |
| `CLOUD_STORAGE_PROVIDER` | Storage provider | `s3` |

## 🌍 **Available Regions**

| Region | Endpoint Format |
|--------|----------------|
| New York | `https://space-name.nyc3.digitaloceanspaces.com` |
| San Francisco | `https://space-name.sfo3.digitaloceanspaces.com` |
| Amsterdam | `https://space-name.ams3.digitaloceanspaces.com` |
| Singapore | `https://space-name.sgp1.digitaloceanspaces.com` |
| Frankfurt | `https://space-name.fra1.digitaloceanspaces.com` |

## 🔧 **Testing Your Setup**

### **Test with AWS CLI (if installed):**

```bash
# Configure AWS CLI for DigitalOcean Spaces
aws configure set aws_access_key_id DO00ABCDEFGHIJKLMNOP
aws configure set aws_secret_access_key your-secret-key
aws configure set default.region nyc3

# Test upload
aws s3 cp test.mp4 s3://text-to-video-ai/ --endpoint-url https://nyc3.digitaloceanspaces.com

# List files
aws s3 ls s3://text-to-video-ai/ --endpoint-url https://nyc3.digitaloceanspaces.com
```

### **Test with curl:**

```bash
# Upload a test file
curl -X PUT \
  -H "Content-Type: video/mp4" \
  --data-binary @test.mp4 \
  "https://text-to-video-ai.nyc3.digitaloceanspaces.com/test.mp4"
```

## 💰 **Pricing**

### **DigitalOcean Spaces Pricing:**
- **Storage:** $5/month for 250GB
- **Bandwidth:** $5/month for 1TB
- **Requests:** $0.01 per 1,000 requests
- **Total:** ~$10/month for 250GB + 1TB bandwidth

### **Cost Comparison:**
- **AWS S3:** ~$6/month for 250GB + $90/TB bandwidth
- **Google Cloud:** ~$5/month for 250GB + $120/TB bandwidth
- **DigitalOcean:** $10/month for 250GB + 1TB bandwidth

**DigitalOcean is often cheaper for bandwidth-heavy applications!**

## 🔄 **How It Works**

1. **Video Generation:** Railway generates video locally
2. **Upload to Spaces:** Video uploaded to your DigitalOcean Space
3. **Public URL:** Video accessible via public URL
4. **CDN Delivery:** Fast global delivery via DigitalOcean's CDN
5. **Cleanup:** Local files deleted to save space

## 📊 **API Response Format**

Your API will return:

```json
{
  "job_id": "abc123",
  "status": "completed",
  "video_url": "https://text-to-video-ai.nyc3.digitaloceanspaces.com/videos/video_abc123.mp4",
  "message": "Video uploaded to cloud storage!"
}
```

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **"Access Denied" Error:**
   - Check your Access Key and Secret Key
   - Verify the Space name is correct
   - Ensure the Space is set to "Public"

2. **"NoSuchBucket" Error:**
   - Verify the Space name in `CLOUD_STORAGE_BUCKET`
   - Check the endpoint URL format
   - Ensure the Space exists in the correct region

3. **"Invalid Endpoint" Error:**
   - Check the `SPACES_ENDPOINT` format
   - Verify the region code (nyc3, sfo3, etc.)
   - Ensure HTTPS is used

### **Debug Commands:**

```bash
# Test connection
curl -I https://text-to-video-ai.nyc3.digitaloceanspaces.com/

# List files (if public)
curl https://text-to-video-ai.nyc3.digitaloceanspaces.com/
```

## 🎯 **Next Steps**

1. **Create your DigitalOcean Space**
2. **Generate access keys**
3. **Add environment variables to Railway**
4. **Deploy and test**
5. **Monitor usage in DigitalOcean dashboard**

## 📈 **Monitoring**

- **DigitalOcean Dashboard:** Monitor storage usage and bandwidth
- **Space Settings:** Configure CORS, CDN, and access policies
- **Billing:** Track costs and usage patterns

Your videos will now be stored in DigitalOcean Spaces with fast global CDN delivery! 🎬🌊
