import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key from .env: {api_key[:10] if api_key else 'None'}...{api_key[-4:] if api_key else 'None'}")