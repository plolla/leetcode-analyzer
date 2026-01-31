#!/usr/bin/env python3
"""Test script to verify OpenAI API connection."""

import sys
import requests
from config import config

def test_openai_connection():
    """Test if we can successfully connect to OpenAI API."""
    
    print("Testing OpenAI API connection...")
    print(f"API Key configured: {'Yes' if config.OPENAI_API_KEY else 'No'}")
    
    if not config.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return False
    
    # Show first/last few characters of API key for verification
    key = config.OPENAI_API_KEY
    masked_key = f"{key[:7]}...{key[-4:]}" if len(key) > 11 else "***"
    print(f"API Key (masked): {masked_key}")
    print(f"Model: {config.OPENAI_MODEL}")
    
    try:
        # Make a simple test request using requests library
        print("\nSending test request...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, OpenAI connection successful!' in exactly those words."}
                ],
                "max_completion_tokens": 50
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            print(f"\n✅ SUCCESS! OpenAI responded with:")
            print(f"   {result}")
            print(f"\nConnection test passed!")
            return True
        else:
            print(f"\n❌ ERROR: API returned status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to OpenAI")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_connection()
    sys.exit(0 if success else 1)
