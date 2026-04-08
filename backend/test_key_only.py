import requests

# Your new API key from .env
API_KEY = "sk-1c8ca044ee6d48eaa6452023f7fa6688"

print(f"Testing API Key: {API_KEY[:10]}...{API_KEY[-4:]}")

url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Say 'Hello from DarkmoorAI'"}],
    "max_tokens": 20
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅✅✅ SUCCESS! API KEY IS VALID! ✅✅✅")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"\n❌ Failed: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")