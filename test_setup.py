from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Cek file .env kamu.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Balas dengan satu kalimat pendek: siapa Lee Kuan Yew?"
)

print("Berhasil! Response dari Gemini:")
print(response.text)