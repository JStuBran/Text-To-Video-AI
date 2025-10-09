# Railway Deployment Guide

## 🚀 Deploying Text-to-Video AI to Railway

This guide will help you deploy your Text-to-Video AI application to Railway for n8n integration.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **API Keys**: You'll need your API keys ready to configure

## 🔧 Step 1: Prepare Your Repository

### Files Already Created:
- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Process definition
- ✅ `requirements.txt` - Python dependencies
- ✅ `n8n_api_light.py` - Railway-optimized API (uses PORT environment variable)

### Required Files:
- ✅ `.env` - Environment variables (will be configured in Railway)
- ✅ All utility modules in `utility/` directory

## 🚀 Step 2: Deploy to Railway

### Option A: GitHub Integration (Recommended)

1. **Connect GitHub**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables**:
   ```
   OPENAI_API_KEY=your-openai-key
   PEXELS_API_KEY=your-pexels-key
   ELEVENLABS_API_KEY=your-elevenlabs-key
   ```

3. **Deploy**:
   - Railway will automatically detect Python and install dependencies
   - The app will start using the `Procfile`

### Option B: Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

## 🔑 Step 3: Configure Environment Variables

In Railway Dashboard:

1. Go to your project
2. Click on "Variables" tab
3. Add these environment variables:

```
OPENAI_API_KEY=sk-your-openai-key
PEXELS_API_KEY=your-pexels-key
ELEVENLABS_API_KEY=your-elevenlabs-key
```

## 🌐 Step 4: Get Your Public URL

After deployment, Railway will provide:
- **Public URL**: `https://your-app-name.railway.app`
- **Health Check**: `https://your-app-name.railway.app/health`

## 🔗 Step 5: Update n8n Configuration

### HTTP Request Node Settings:

**Method:** `POST`
**URL:** `https://your-app-name.railway.app/generate-video`
**Headers:**
```json
{
  "Content-Type": "application/json"
}
```
**Body (JSON):**
```json
{
  "text": "{{ $json.topic }}"
}
```

## 📊 Step 6: Monitor Your Deployment

### Railway Dashboard:
- View logs in real-time
- Monitor resource usage
- Check deployment status

### Health Check:
```bash
curl https://your-app-name.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-08T14:45:54.687564",
  "version": "1.0.0"
}
```

## 🧪 Step 7: Test the API

### Test Video Generation:
```bash
curl -X POST https://your-app-name.railway.app/generate-video \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing facts about dolphins"}'
```

### Check Job Status:
```bash
curl https://your-app-name.railway.app/job-status/{job_id}
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check `requirements.txt` for version conflicts
   - Ensure all dependencies are listed

2. **Environment Variables**:
   - Verify all API keys are set correctly
   - Check variable names match exactly

3. **Port Issues**:
   - Railway automatically sets `PORT` environment variable
   - App uses `os.environ.get('PORT', 5000)`

4. **File Permissions**:
   - Railway handles file system permissions automatically
   - Temporary files are created in `/tmp` directory

### Logs:
```bash
railway logs
```

## 💰 Railway Pricing

- **Free Tier**: $5 credit monthly
- **Pro Plan**: $20/month for unlimited usage
- **Pay-as-you-go**: Only pay for what you use

## 🎯 Benefits of Railway vs Local

### Railway Advantages:
- ✅ **Public URL**: Accessible from anywhere
- ✅ **Always Online**: 24/7 availability
- ✅ **Auto-scaling**: Handles traffic spikes
- ✅ **Easy Deployment**: Git-based deployments
- ✅ **Environment Management**: Secure variable storage
- ✅ **Monitoring**: Built-in logging and metrics

### Local Limitations:
- ❌ **No Public Access**: Only accessible locally
- ❌ **Manual Management**: Need to keep running
- ❌ **Network Issues**: Dependent on local network
- ❌ **No Persistence**: Stops when computer shuts down

## 🚀 Next Steps

1. Deploy to Railway using GitHub integration
2. Configure environment variables
3. Test the public URL
4. Update your n8n workflow to use the Railway URL
5. Monitor usage and scale as needed

Your Text-to-Video AI will now be accessible from anywhere and perfect for n8n integration!
