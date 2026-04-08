import openai
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv('DEEPSEEK_API_KEY')
print(f"API Key found: {api_key[:10]}...{api_key[-4:] if api_key else 'NOT SET'}")

if not api_key:
    print("❌ No API key found in .env")
    exit(1)

# Create client
client = openai.OpenAI(
    api_key=api_key,
    base_url='https://api.deepseek.com/v1'
)

print("\n📡 Testing DeepSeek API...")

try:
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Say Hello from DarkmoorAI'}
        ],
        max_tokens=50
    )
    
    print("\n✅ SUCCESS! DeepSeek API is WORKING!")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("1. API key is invalid")
    print("2. No internet connection")
    print("3. DeepSeek service is down")