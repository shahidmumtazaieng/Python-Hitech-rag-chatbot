#!/usr/bin/env python3
"""Test Gemini API key and model access."""

import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    print("=" * 60)
    print("Gemini API Connection Test")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    print(f"\n📋 Configuration:")
    print(f"   Model: {model}")
    print(f"   API Key: {api_key[:10]}... (hidden)")
    
    if not api_key or api_key.startswith('"') or len(api_key) < 20:
        print(f"\n❌ Invalid API key format!")
        print(f"   Expected format: AIzaSy...")
        print(f"   Current: {api_key}")
        print("\n🔧 How to get a valid API key:")
        print("   1. Go to: https://aistudio.google.com/apikey")
        print("   2. Click 'Create API key'")
        print("   3. Copy the key (starts with 'AIza')")
        print("   4. Update your .env file")
        return False
    
    if not api_key.startswith("AIza"):
        print(f"\n⚠️ Warning: API key doesn't start with 'AIza'")
        print(f"   This might be an OAuth token, not an API key")
        print(f"   Please get a proper API key from Google AI Studio")
    
    try:
        import google.generativeai as genai
        
        print(f"\n🔌 Initializing Gemini client...")
        genai.configure(api_key=api_key)
        
        print(f"📡 Testing model: {model}")
        model_obj = genai.GenerativeModel(model)
        
        print(f"💬 Sending test message...")
        response = model_obj.generate_content(
            "Say 'Hello! Gemini is working!' in one sentence."
        )
        
        print(f"\n✅ Gemini API connection SUCCESS!")
        print(f"   Response: {response.text}")
        print(f"\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini API connection FAILED!")
        print(f"   Error: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Check your API key is correct")
        print(f"   2. Make sure Gemini API is enabled")
        print(f"   3. Visit: https://aistudio.google.com")
        print(f"   4. Try using 'gemini-pro' model instead")
        return False


if __name__ == "__main__":
    test_gemini()
