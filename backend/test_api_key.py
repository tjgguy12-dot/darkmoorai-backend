import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
print(f"API Key from .env: {api_key[:10]}...{api_key[-4:]}")
print(f"Key length: {len(api_key)}")
print(f"Starts with sk-1c8: {api_key.startswith('sk-1c8ca04')}")

# Test with actual API call
import requests

url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        print("✅ API KEY IS VALID!")
        print(response.json()["choices"][0]["message"]["content"])
    else:
        print(f"❌ Invalid API key: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")