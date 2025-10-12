from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
api_key = os.getenv("TNSYSTEM1")
print("API Key読み込み:", "成功" if api_key else "失敗")

client = OpenAI(api_key=api_key)