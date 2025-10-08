# Railway Healthcheck Troubleshooting Guide

## 🚨 **Healthcheck Failed - Common Solutions**

### **1. Environment Variables Missing**
**Problem:** Required API keys not set in Railway
**Solution:**
1. Go to Railway Dashboard → Your Project → Variables
2. Add these variables:
   ```
   OPENAI_API_KEY=sk-your-openai-key
   ELEVENLABS_API_KEY=your-elevenlabs-key
   GROQ_API_KEY=gsk_your-groq-key
   PEXELS_API_KEY=your-pexels-key
   ```

### **2. Port Configuration**
**Problem:** App not binding to Railway's PORT
**Solution:** ✅ Fixed - App now uses `os.environ.get('PORT', 5000)`

### **3. Build Dependencies**
**Problem:** Missing system dependencies
**Solution:** ✅ Fixed - Using `requirements-railway.txt` with pinned versions

### **4. Startup Time**
**Problem:** App takes too long to start
**Solution:** ✅ Fixed - Increased healthcheck timeout to 600 seconds

## 🔧 **Debugging Steps**

### **Check Railway Logs:**
1. Go to Railway Dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Click on latest deployment
5. Check "Logs" for errors

### **Test Healthcheck Manually:**
```bash
curl https://your-app-name.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-08T16:51:53.478351",
  "version": "1.0.0",
  "port": "5000",
  "missing_env_vars": null
}
```

### **Common Error Messages:**

#### **"Environment variables missing"**
- Add missing API keys in Railway Variables

#### **"Port already in use"**
- Railway handles this automatically

#### **"Module not found"**
- Check `requirements-railway.txt` is being used

#### **"Permission denied"**
- Startup script has execute permissions

## 🚀 **Quick Fixes**

### **Option 1: Redeploy**
1. Go to Railway Dashboard
2. Click "Redeploy" on your project
3. Wait for build to complete

### **Option 2: Check Variables**
1. Go to Variables tab
2. Ensure all required keys are set
3. Redeploy if needed

### **Option 3: Use Railway CLI**
```bash
railway login
railway link
railway up
```

## 📊 **Healthcheck Status Codes**

- **200**: Healthy - All systems working
- **503**: Degraded - Missing environment variables
- **500**: Unhealthy - Application error

## 🔍 **Advanced Debugging**

### **Check Railway Logs for:**
- Build errors
- Runtime errors
- Environment variable issues
- Port binding problems

### **Test Locally First:**
```bash
# Test with Railway environment
export PORT=5000
export OPENAI_API_KEY=your-key
export ELEVENLABS_API_KEY=your-key
python n8n_api.py
```

## ✅ **Success Indicators**

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Healthcheck returns 200 status
- ✅ App responds to `/health` endpoint
- ✅ All environment variables are set

## 🆘 **Still Having Issues?**

1. **Check Railway Status**: [status.railway.app](https://status.railway.app)
2. **Railway Discord**: Join their community Discord
3. **GitHub Issues**: Check for similar issues in Railway's GitHub

The most common issue is missing environment variables. Make sure all API keys are properly set in Railway's Variables section!
