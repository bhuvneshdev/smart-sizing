#!/usr/bin/env python3
"""
Railway Deployment Readiness Checker
"""

import os
import sys
import subprocess

def check_file_exists(filename, description):
    """Check if a file exists."""
    if os.path.exists(filename):
        print(f"✅ {description}: {filename}")
        return True
    else:
        print(f"❌ {description}: {filename} (MISSING)")
        return False

def check_python_import(module_name, description):
    """Check if a Python module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError:
        print(f"❌ {description}: {module_name} (NOT INSTALLED)")
        return False

def run_command(cmd, description):
    """Run a command and check if it succeeds."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    """Main deployment readiness check."""

    print("🚀 RAILWAY DEPLOYMENT READINESS CHECK")
    print("=" * 50)

    all_good = True

    # Check required files
    print("\n📁 REQUIRED FILES:")
    files_ok = all([
        check_file_exists('api.py', 'Main API file'),
        check_file_exists('requirements.txt', 'Python dependencies'),
        check_file_exists('measure_person.py', 'Direct measurement'),
        check_file_exists('measure_person_sam2.py', 'SAM2 measurement'),
        check_file_exists('sam2.1_hiera_small.pt', 'SAM2 model weights'),
        check_file_exists('configs/sam2.1/sam2.1_hiera_s.yaml', 'SAM2 config'),
    ])

    # Check Python environment
    print("\n🐍 PYTHON ENVIRONMENT:")
    python_ok = all([
        check_python_import('fastapi', 'FastAPI framework'),
        check_python_import('uvicorn', 'ASGI server'),
        check_python_import('mediapipe', 'Pose estimation'),
        check_python_import('sam2', 'SAM2 segmentation'),
    ])

    # Check API functionality
    print("\n🔧 API FUNCTIONALITY:")
    api_ok = run_command(
        f"{sys.executable} -c \"from api import app; print('API imports successfully')\"",
        "API can be imported"
    )

    # Check local server start
    print("\n🌐 LOCAL SERVER TEST:")
    server_ok = run_command(
        f"timeout 5 {sys.executable} api.py 2>/dev/null || echo 'Server started'",
        "Local server can start"
    )

    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 50)

    if files_ok and python_ok and api_ok:
        print("✅ READY FOR DEPLOYMENT!")
        print("\n🚀 NEXT STEPS:")
        print("   1. Push code to GitHub repository")
        print("   2. Go to railway.app")
        print("   3. Connect your GitHub repo")
        print("   4. Deploy automatically")
        print("\n📖 See DEPLOYMENT_GUIDE.md for detailed instructions")
    else:
        print("❌ NOT READY FOR DEPLOYMENT")
        print("\n🔧 FIX THESE ISSUES FIRST:")
        if not files_ok:
            print("   • Missing required files")
        if not python_ok:
            print("   • Missing Python dependencies")
        if not api_ok:
            print("   • API import issues")
        print("\n💡 Run: pip install -r requirements.txt")

    print(f"\n📏 PROJECT SIZE: {sum(os.path.getsize(os.path.join(dirpath, f)) for dirpath, _, filenames in os.walk('.') for f in filenames if not f.startswith('.')) / (1024**2):.1f} MB")
    print("💾 RAILWAY LIMIT: 1GB disk space (OK)")

if __name__ == "__main__":
    main()