import requests

# PUT YOUR NEW API KEY HERE
NEW_API_KEY = "sk-YOUR-NEW-KEY-HERE"

print("Testing your new API key...")
print(f"Key: {NEW_API_KEY[:10]}...{NEW_API_KEY[-4:]}")

url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {NEW_API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Say Hello"}],
    "max_tokens": 10
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅✅✅ SUCCESS! API KEY IS VALID! ✅✅✅")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"\n❌ Still invalid. Status: {response.status_code}")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")