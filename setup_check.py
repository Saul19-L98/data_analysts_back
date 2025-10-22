#!/usr/bin/env python
"""Quick setup script to verify the project is ready to run."""
import os
import sys


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("📝 Please create .env file from .env.example:")
        print("   cp .env.example .env")
        print("   Then edit .env with your AWS credentials")
        return False
    
    print("✅ .env file exists")
    
    # Check required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required = ["AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing = []
    
    for var in required:
        value = os.getenv(var)
        if not value or value.startswith("YOUR_") or value.startswith("test-"):
            missing.append(var)
    
    if missing:
        print(f"⚠️  Missing or placeholder values: {', '.join(missing)}")
        print("   Please update these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True


def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import fastapi
        import pandas
        import boto3
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Run: uv sync")
        return False


def main():
    """Run all checks."""
    print("🔍 Checking project setup...\n")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "="*50)
    
    if all(results):
        print("✅ Project is ready!")
        print("\n🚀 To start the server, run:")
        print("   uv run uvicorn app.main:app --reload")
        print("\n📚 Then visit:")
        print("   http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("❌ Please fix the issues above before running")
        sys.exit(1)


if __name__ == "__main__":
    main()
