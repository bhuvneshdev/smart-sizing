# Railway Deployment Guide

## 🚂 **Railway - Recommended Free Option**

Railway offers the most generous free tier for ML applications.

### **Free Tier Limits:**
- ✅ 512MB RAM (enough for SAM2)
- ✅ 1GB disk space
- ✅ Unlimited bandwidth
- ✅ Custom domains
- ❌ No GPU (but SAM2 works on CPU)

### **Deployment Steps:**

1. **Create Railway Account:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Connect Repository:**
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your `smart-sizing` repository

3. **Auto-Deployment:**
   - Railway detects `requirements.txt` and `api.py`
   - Automatically builds and deploys
   - Takes ~5-10 minutes

4. **Environment Variables (if needed):**
   - No special config needed for basic deployment

5. **Get Your API URL:**
   - Railway provides `https://your-app-name.up.railway.app`
   - API endpoints: `https://your-app-name.up.railway.app/measure_person`

### **Railway vs Other Options:**

| Service | Free RAM | Free Hours | GPU | Ease of Use |
|---------|----------|------------|-----|-------------|
| Railway | 512MB | Unlimited | ❌ | ⭐⭐⭐⭐⭐ |
| Render | 750MB | 750hrs/month | ❌ | ⭐⭐⭐⭐ |
| Fly.io | 256MB | 3GB/month | ❌ | ⭐⭐⭐ |
| Vercel | 1008MB | 100GB/month | ❌ | ⭐⭐ (API only) |

## 🔧 **Railway Configuration Files**

Railway auto-detects Python apps, but you can add these for optimization:

### `railway.toml` (Optional)
```toml
[build]
builder = "python"

[deploy]
startCommand = "uvicorn api:app --host 0.0.0.0 --port $PORT"
```

### `runtime.txt` (Optional)
```
python-3.11
```

## 📊 **Performance Expectations**

- **Cold Start:** ~10-15 seconds (model loading)
- **Warm Requests:** ~2-5 seconds per measurement
- **SAM2 Method:** ~15-30 seconds (due to segmentation)
- **Direct Method:** ~3-5 seconds

## 💰 **Upgrade Path**

When you need more power:
- **Railway Pro:** $5/month (4GB RAM, 32GB storage)
- **Railway Teams:** Custom pricing

## 🧪 **Testing Your Deployed API**

Once deployed, test with:
```bash
curl -X POST "https://your-app.up.railway.app/measure_person" \
  -F "file=@person.jpg" \
  -F "height_cm=183"
```

## 🎯 **Why Railway?**

✅ **Easiest deployment** - Just connect GitHub repo  
✅ **Enough RAM** for SAM2 on CPU  
✅ **No complex config** required  
✅ **Auto-scaling** and **auto-deploy** from git  
✅ **Custom domains** available  
✅ **Great for ML apps** - Many users deploy similar projects  

Railway is perfect for your use case!