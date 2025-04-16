from openai import OpenAI

# Paste your key below — treat this as sensitive
client = OpenAI(api_key="sk-proj-WZpJMr3IcVaTGFo2...")  # shortened for privacy

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello GPT-4!"}],
        temperature=0.7
    )
    print("✅ GPT-4 API is accessible.")
except Exception as e:
    print("❌ GPT-4 API NOT accessible.")
    print("Error:", e)
