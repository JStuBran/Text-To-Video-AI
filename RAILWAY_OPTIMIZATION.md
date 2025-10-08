# Railway Build Optimization Guide

## ⚡ **Fast Railway Deployment Strategy**

### **Problem:**
Railway builds were taking 10+ minutes due to heavy dependencies:
- **PyTorch**: ~900MB
- **CUDA libraries**: ~2GB total
- **Whisper**: Requires PyTorch + heavy ML libraries
- **SciPy**: ~35MB with compiled binaries

### **Solution:**
Created lightweight Railway deployment with minimal dependencies.

## 🚀 **Two Deployment Options**

### **Option 1: Railway Lightweight (Recommended)**
**Build Time:** ~2-3 minutes
**Dependencies:** Core API only

**Files:**
- `n8n_api_light.py` - Lightweight API
- `requirements-light.txt` - Minimal dependencies
- `railway.json` - Configured for light build

**Features:**
- ✅ Fast deployment
- ✅ Basic video generation
- ✅ Audio generation with ElevenLabs
- ✅ Script generation
- ❌ No advanced video rendering
- ❌ No Whisper captions

### **Option 2: Full Railway (Heavy)**
**Build Time:** ~10-15 minutes
**Dependencies:** All features

**Files:**
- `n8n_api.py` - Full API
- `requirements-railway.txt` - All dependencies
- `railway.json` - Configured for full build

**Features:**
- ✅ Complete video generation
- ✅ Whisper captions
- ✅ Advanced video rendering
- ✅ All features
- ❌ Slow build times
- ❌ High resource usage

## 📊 **Build Time Comparison**

| Version | Build Time | Dependencies | Features |
|---------|------------|--------------|----------|
| **Light** | 2-3 min | ~50MB | Basic |
| **Full** | 10-15 min | ~3GB | Complete |

## 🔧 **Current Configuration**

Railway is now configured for **Lightweight** deployment:

```json
{
  "build": {
    "buildCommand": "pip install -r requirements-light.txt"
  },
  "deploy": {
    "startCommand": "python n8n_api_light.py"
  }
}
```

## 🎯 **For n8n Integration**

Both versions work with n8n, but:

### **Lightweight Version:**
- **Perfect for testing** n8n integration
- **Fast deployment** for development
- **Basic video output** (audio + simple video)

### **Full Version:**
- **Production-ready** video generation
- **Complete features** for final deployment
- **Slower but comprehensive**

## 🚀 **Deployment Steps**

### **Current (Lightweight):**
1. Railway will use `requirements-light.txt`
2. Build time: ~2-3 minutes
3. Basic video generation
4. Perfect for n8n testing

### **Switch to Full (if needed):**
1. Update `railway.json`:
   ```json
   "buildCommand": "pip install -r requirements-railway.txt"
   "startCommand": "python n8n_api.py"
   ```
2. Redeploy
3. Build time: ~10-15 minutes
4. Full video generation

## 💡 **Recommendation**

**Start with Lightweight:**
- Test n8n integration quickly
- Verify API endpoints work
- Confirm environment variables

**Upgrade to Full later:**
- Once n8n integration is working
- When you need complete video features
- For production deployment

## 🔄 **Quick Switch**

To switch between versions, just update `railway.json`:

**Lightweight:**
```json
"buildCommand": "pip install -r requirements-light.txt",
"startCommand": "python n8n_api_light.py"
```

**Full:**
```json
"buildCommand": "pip install -r requirements-railway.txt", 
"startCommand": "python n8n_api.py"
```

The lightweight version will deploy much faster and is perfect for getting your n8n integration working quickly!
