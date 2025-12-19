#!/usr/bin/env python3
"""
Railway Deployment Helper Script

This script helps prepare your project for Railway deployment.
"""

import os
import json
import subprocess

def create_railway_config():
    """Create Railway configuration files."""

    print("🚂 Setting up Railway deployment...")

    # Create railway.toml
    railway_config = """[build]
builder = "python"

[deploy]
startCommand = "uvicorn api:app --host 0.0.0.0 --port $PORT"
"""

    with open('railway.toml', 'w') as f:
        f.write(railway_config)
    print("✅ Created railway.toml")

    # Create runtime.txt
    runtime_config = "python-3.11\n"
    with open('runtime.txt', 'w') as f:
        f.write(runtime_config)
    print("✅ Created runtime.txt")

    # Create .env.example
    env_example = """# Railway Environment Variables
# These are automatically set by Railway

PORT=8000
PYTHON_VERSION=3.11
"""
    with open('.env.example', 'w') as f:
        f.write(env_example)
    print("✅ Created .env.example")

def create_docker_option():
    """Create optional Dockerfile for more control."""

    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    print("✅ Created Dockerfile (optional, for advanced deployments)")

def check_requirements():
    """Check if all required files exist."""

    required_files = [
        'api.py',
        'requirements.txt',
        'measure_person.py',
        'measure_person_sam2.py'
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False

    print("✅ All required files present")
    return True

def create_deployment_guide():
    """Create a quick deployment guide."""

    guide = """# 🚀 Quick Railway Deployment

## Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

## Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Railway auto-detects Python app and deploys

## Step 3: Get Your API URL
Railway provides: `https://your-app-name.up.railway.app`

## Step 4: Test Your API
```bash
curl -X POST "https://your-app.up.railway.app/measure_person" \\
  -F "file=@person.jpg" \\
  -F "height_cm=183"
```

## 📊 Expected Performance
- Cold start: ~10-15 seconds (model loading)
- Warm requests: ~2-5 seconds
- SAM2 method: ~15-30 seconds

## 🎯 API Endpoints
- `POST /measure_person` - Direct MediaPipe measurement
- `POST /measure_person_sam2` - SAM2 segmentation + MediaPipe
- `GET /docs` - Interactive API documentation

Happy deploying! 🎉
"""

    with open('DEPLOYMENT_QUICKSTART.md', 'w') as f:
        f.write(guide)
    print("✅ Created DEPLOYMENT_QUICKSTART.md")

def main():
    """Main deployment setup function."""

    print("🔧 Railway Deployment Setup")
    print("=" * 40)

    # Check requirements
    if not check_requirements():
        return

    # Create configuration files
    create_railway_config()
    create_docker_option()
    create_deployment_guide()

    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    print("=" * 40)
    print("Next steps:")
    print("1. Commit and push to GitHub")
    print("2. Go to railway.app and connect your repo")
    print("3. Deploy automatically!")
    print("\n📖 See DEPLOYMENT_QUICKSTART.md for detailed instructions")

if __name__ == "__main__":
    main()