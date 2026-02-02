import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"Testing key: {key[:5]}... (Length: {len(key)})")

genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-2.5-flash')

for i in range(10):
    try:
        print(f"Attempt {i+1}...")
        response = model.generate_content("Say test")
        print(f"Success: {response.text.strip()}")
        time.sleep(5) # 12 requests per minute
    except Exception as e:
        print(f"Error at attempt {i+1}: {e}")
        if "400" in str(e) or "403" in str(e):
             break
