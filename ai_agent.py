from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
api_key = os.getenv("TNSYSTEM1")

client = OpenAI(api_key=api_key)

def chat_with_ai(user_input, chat_history, recent_learning):
    messages = [{"role": "system", "content": "あなたは市場調査アシスタントです。"}]
    for m in chat_history:
        messages.append({"role": "user" if m["role"]=="user" else "assistant", "content": m["content"]})
    for entry in recent_learning:
        messages.append({"role": "assistant", "content": entry.get("bot_response", "")})
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=messages
    )
    return response.choices[0].message.content
