#!/usr/bin/env python3
"""
Test script to verify the setup is working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_environment():
    """Test environment variables"""
    load_dotenv()
    
    print("🔍 Checking environment variables...")
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        print(f"✅ Discord token found (starts with {token[:10]}...)")
    else:
        print("❌ Discord token not found")
        return False
    
    provider = os.getenv('LLM_PROVIDER', 'lmstudio')
    model = os.getenv('LLM_MODEL', 'google/gemma-3n-e4b')
    lm_url = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
    
    print(f"✅ LLM Provider: {provider}")
    print(f"✅ Model: {model}")
    print(f"✅ LM Studio URL: {lm_url}")
    
    return True

def test_imports():
    """Test if all modules can be imported"""
    print("\n🔍 Testing imports...")
    
    try:
        import discord
        print("✅ Discord.py imported")
    except ImportError as e:
        print(f"❌ Failed to import discord: {e}")
        return False
    
    try:
        import interpreter
        print("✅ Open Interpreter imported")
    except ImportError as e:
        print(f"❌ Failed to import interpreter: {e}")
        return False
    
    try:
        from interpreter_bridge import InterpreterBridge
        print("✅ InterpreterBridge imported")
    except ImportError as e:
        print(f"❌ Failed to import InterpreterBridge: {e}")
        return False
    
    try:
        from discord_bot import ProductivityBot
        print("✅ ProductivityBot imported")
    except ImportError as e:
        print(f"❌ Failed to import ProductivityBot: {e}")
        return False
    
    return True

def test_lm_studio_connection():
    """Test LM Studio connection"""
    print("\n🔍 Testing LM Studio connection...")
    
    import requests
    lm_url = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
    
    try:
        # Try to connect to LM Studio
        response = requests.get(f"{lm_url}/models", timeout=5)
        if response.status_code == 200:
            print(f"✅ LM Studio is running at {lm_url}")
            models = response.json()
            if 'data' in models and models['data']:
                print(f"   Available models: {[m['id'] for m in models['data']]}")
            return True
        else:
            print(f"⚠️  LM Studio returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"⚠️  LM Studio not reachable at {lm_url}")
        print("   Make sure LM Studio is running with the server enabled")
    except Exception as e:
        print(f"⚠️  Error connecting to LM Studio: {e}")
    
    return False

def main():
    """Run all tests"""
    print("="*50)
    print("Local AI Productivity Assistant - Setup Test")
    print("="*50)
    
    all_good = True
    
    # Test environment
    if not test_environment():
        all_good = False
    
    # Test imports
    if not test_imports():
        all_good = False
    
    # Test LM Studio
    test_lm_studio_connection()  # Warning only, not critical
    
    print("\n" + "="*50)
    if all_good:
        print("✅ Setup looks good! You can run the bot with:")
        print("   python src/main.py")
    else:
        print("❌ Some issues were found. Please fix them before running.")
    print("="*50)

if __name__ == "__main__":
    main()