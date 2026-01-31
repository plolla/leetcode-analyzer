#!/usr/bin/env python3
"""Test script to verify Claude API connection."""

import sys
import asyncio
from anthropic import Anthropic
from config import config

async def test_claude_connection():
    """Test if we can successfully connect to Claude API."""
    
    print("Testing Claude API connection...")
    print(f"API Key configured: {'Yes' if config.CLAUDE_API_KEY else 'No'}")
    
    if not config.CLAUDE_API_KEY:
        print("❌ ERROR: CLAUDE_API_KEY not found in environment")
        return False
    
    # Show first/last few characters of API key for verification
    key = config.CLAUDE_API_KEY
    masked_key = f"{key[:7]}...{key[-4:]}" if len(key) > 11 else "***"
    print(f"API Key (masked): {masked_key}")
    print(f"Model: {config.CLAUDE_MODEL}")
    
    try:
        # Create client
        print("\nCreating Claude client...")
        client = Anthropic(api_key=config.CLAUDE_API_KEY)
        
        # Make a simple test request
        print("Sending test request...")
        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Hello, Claude connection successful!' in exactly those words."}
            ]
        )
        
        result = response.content[0].text
        print(f"\n✅ SUCCESS! Claude responded with:")
        print(f"   {result}")
        print(f"\nConnection test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to Claude")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_claude_connection())
    sys.exit(0 if success else 1)
