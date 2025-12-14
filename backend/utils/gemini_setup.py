from google import genai  # ✅ correct for google-genai>=1.0.0


# Direct API key (no .env needed)
GEMINI_API_KEY = "AIzaSyDShxLGo0KTe6I-ty8_vJ3CIOItTKN0AcQ"

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

