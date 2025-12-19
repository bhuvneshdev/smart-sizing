# 🚀 Render Deployment Guide (FREE Alternative)

## 🎯 **Why Render?**
- ✅ **750MB RAM** (vs Railway's discontinued 512MB free)
- ✅ **750 hours/month** free
- ✅ **No sleeping** - always awake
- ✅ **Perfect for ML APIs** with SAM2
- ✅ **Easy deployment** from GitHub

## 📋 **Pre-Deployment Checklist**

### ✅ **Repository Ready:**
- [x] Code committed to GitHub
- [x] `requirements.txt` complete
- [x] `api.py` working locally
- [x] Repository size: 1.5GB (under Render's limits)
- [x] Images moved to external folder

## 🚀 **Render Deployment Steps**

### **Step 1: Create Render Account**
1. Go to **[render.com](https://render.com)**
2. Click **"Get Started"** → **"Sign up with GitHub"**
3. Authorize Render to access your repositories

### **Step 2: Create New Web Service**
1. Click **"New"** → **"Web Service"**
2. Select **"Connect GitHub"**
3. Find and select your `smart-sizing` repository
4. Click **"Connect"**

### **Step 3: Configure Deployment**
Fill in the settings:

**Basic Settings:**
- **Name:** `smart-sizing-api` (or your choice)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Instance Type:** `Free` (750MB RAM)
- **Region:** Choose closest to your users
- **Health Check Path:** `/` (optional)

### **Step 4: Deploy**
1. Click **"Create Web Service"**
2. Wait 10-15 minutes for deployment
3. Monitor logs in the **"Logs"** tab

### **Step 5: Get Your API URL**
Render will provide a URL like:
```
https://smart-sizing-api.onrender.com
```

## 🧪 **Testing Your Deployed API**

### **Test 1: API Root**
Visit: `https://your-app.onrender.com/`

### **Test 2: API Documentation**
Visit: `https://your-app.onrender.com/docs`

### **Test 3: Test Endpoints**
```bash
# Test direct measurement
curl -X POST "https://your-app.onrender.com/measure_person" \
  -F "file=@/Users/bhuvneshsingh/work/test_images/person.jpg" \
  -F "height_cm=183"

# Test SAM2 measurement
curl -X POST "https://your-app.onrender.com/measure_person_sam2" \
  -F "file=@/Users/bhuvneshsingh/work/test_images/person.jpg" \
  -F "height_cm=183"
```

## 📊 **Expected Performance**

| Metric | Local | Render Free |
|--------|-------|-------------|
| **RAM** | Variable | 750MB |
| **Cold Start** | Instant | ~10-15s |
| **Direct Method** | ~2-3s | ~3-5s |
| **SAM2 Method** | ~10-20s | ~15-30s |
| **Uptime** | When running | 24/7 |

## 💰 **Render Free Tier Limits**

- ✅ **750 hours/month** (plenty for development)
- ✅ **750MB RAM** (enough for SAM2)
- ✅ **Unlimited bandwidth**
- ✅ **Custom domains**
- ✅ **Free SSL certificates**
- ❌ **Sleeps after 15 minutes** of inactivity (but wakes on request)

## 🔧 **Troubleshooting**

### **If Deployment Fails:**
1. **Check Logs:** Click "Logs" tab in Render dashboard
2. **Common Issues:**
   - Missing dependencies in `requirements.txt`
   - SAM2 model loading issues
   - Port configuration problems

### **If API Returns Errors:**
1. **Check Render Logs:** Real-time logs available
2. **Test Locally:** Ensure it works on your machine
3. **Memory Issues:** Monitor RAM usage in dashboard

## 🎯 **Render vs Railway Comparison**

| Feature | Render Free | Railway Hobby ($5/mo) |
|---------|-------------|----------------------|
| **RAM** | 750MB | 4GB |
| **Storage** | Unlimited* | 32GB |
| **Hours/Month** | 750 | Unlimited |
| **Cold Starts** | Yes | Minimal |
| **Uptime** | 24/7 | 24/7 |
| **Cost** | FREE | $5/month |
| **Best For** | Development/Testing | Production |

*Storage is shared across all services

## 🚀 **Next Steps**

1. **Push to GitHub** (if not already)
2. **Go to [render.com](https://render.com)**
3. **Connect your repository**
4. **Deploy automatically**
5. **Test your free API!**

## 🎉 **Success Checklist**

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service created
- [ ] Deployment successful (green status)
- [ ] API URL generated
- [ ] `/docs` endpoint working
- [ ] Measurement endpoints responding

**Your person measurement API is now live on Render for FREE! 🌐**

Need help with any step? Just let me know! 🚀