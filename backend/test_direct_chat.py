#!/usr/bin/env python3
"""
Direct DeepSeek API Test
"""

import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

print(f"Testing DeepSeek API")
print(f"API Key: {api_key[:10] if api_key else 'None'}...{api_key[-4:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found in .env")
    exit(1)

# Test with a simple request
url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Say 'Hello'"}],
    "max_tokens": 10
}

print("\n📡 Sending request...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")