# 🚀 Railway Deployment Step-by-Step Guide

## 📋 **Pre-Deployment Checklist**

### ✅ **Step 0: Prepare Your Code**
- [ ] **GitHub Repository**: Create a public repo at github.com
- [ ] **Push Code**: Commit and push all files
- [ ] **Test Locally**: Run `python api.py` to ensure it works
- [ ] **Dependencies**: Verify `requirements.txt` includes all packages

**Required Files:**
```
smart-sizing/
├── api.py                 ✅ Main FastAPI application
├── requirements.txt       ✅ Python dependencies
├── measure_person.py      ✅ Direct measurement function
├── measure_person_sam2.py ✅ SAM2 measurement function
├── sam2.1_hiera_small.pt  ✅ SAM2 model weights
├── configs/               ✅ SAM2 configuration
└── README.md             ✅ Documentation
```

## 🚀 **Deployment Steps**

### **Step 1: Create Railway Account**
1. Go to **[railway.app](https://railway.app)**
2. Click **"Sign Up"** → **"Continue with GitHub"**
3. Authorize Railway to access your GitHub account

### **Step 2: Create New Project**
1. Click **"New Project"** (blue button)
2. Select **"Deploy from GitHub repo"**
3. Click **"Configure GitHub App"** if prompted
4. Grant access to your repositories

### **Step 3: Select Repository**
1. Find your `smart-sizing` repository in the list
2. Click **"Deploy from GitHub"** next to it
3. Railway will automatically detect it's a Python project

### **Step 4: Auto-Deployment**
Wait 5-10 minutes while Railway:
- 📦 Downloads your code from GitHub
- 🐍 Sets up Python 3.11 environment
- 📚 Installs dependencies from `requirements.txt`
- 🔧 Configures the web service
- 🌐 Assigns a public URL

**You'll see logs like:**
```
Building...
Installing dependencies...
Starting server...
Deployment successful!
```

### **Step 5: Get Your API URL**
Railway will provide a URL like:
```
https://smart-sizing-production.up.railway.app
```

**Your API endpoints will be:**
- `https://your-app.up.railway.app/measure_person`
- `https://your-app.up.railway.app/measure_person_sam2`
- `https://your-app.up.railway.app/docs` (Interactive docs)

## 🧪 **Testing Your Deployed API**

### **Test 1: API Documentation**
Visit: `https://your-app.up.railway.app/docs`
- Should show FastAPI interactive documentation
- Test endpoints directly in browser

### **Test 2: Simple API Call**
```bash
curl -X POST "https://your-app.up.railway.app/measure_person" \
  -F "file=@person.jpg" \
  -F "height_cm=183"
```

### **Test 3: Browser Test**
Use the `api_tester.html` file I created:
1. Open `api_tester.html` in your browser
2. Change the fetch URLs to your Railway URL
3. Upload an image and test both endpoints

## 📊 **Expected Performance**

| Metric | Local | Railway Free |
|--------|-------|--------------|
| **Cold Start** | Instant | 10-15 seconds |
| **Direct Method** | ~2-3s | ~3-5s |
| **SAM2 Method** | ~10-20s | ~15-30s |
| **RAM Usage** | Variable | 512MB limit |

## 🔧 **Troubleshooting**

### **If Deployment Fails:**
1. **Check Logs**: Click on your deployment in Railway dashboard
2. **Common Issues**:
   - Missing dependencies in `requirements.txt`
   - SAM2 model files not accessible
   - Python version compatibility

### **If API Returns Errors:**
1. **Check Railway Logs**: View real-time logs in dashboard
2. **Test Locally**: Ensure it works on your machine first
3. **Memory Issues**: SAM2 might need more RAM (upgrade to Hobby plan)

## 💰 **Cost Analysis**

| Plan | Cost | RAM | Use Case |
|------|------|-----|----------|
| **Free** | $0 | 512MB | Development, testing, light usage |
| **Hobby** | $5/month | 4GB | Production, more traffic |
| **Pro** | $10/month | 8GB | Heavy usage, faster response |

## 🎯 **Next Steps After Deployment**

1. **Share Your API**: Give the URL to users
2. **Monitor Usage**: Check Railway dashboard for metrics
3. **Set Up Monitoring**: Add error logging if needed
4. **Scale Up**: Upgrade plan if you get more users

## 🚨 **Important Notes**

- **Free Tier Sleeps**: After 24h inactivity, service sleeps
- **Cold Starts**: First request after sleep takes longer
- **File Uploads**: Limited to Railway's file size limits
- **No GPU**: SAM2 runs on CPU (slower but works)

## 🎉 **Success Checklist**

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] Deployment successful (green checkmark)
- [ ] API URL generated
- [ ] `/docs` endpoint working
- [ ] `/measure_person` endpoint responding
- [ ] `/measure_person_sam2` endpoint working

**Your person measurement API is now live on the internet! 🌐**

Need help with any step? Just let me know! 🚀