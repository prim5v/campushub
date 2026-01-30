from google import genai  # ✅ correct for google-genai>=1.0.0


# Direct API key (no .env needed)
GEMINI_API_KEY = "AIzaSyAc-4Oxr-A7sOk72xh7I3RWrVIROqEMwWg"

# AIzaSyAc-4Oxr-A7sOk72xh7I3RWrVIROqEMwWg
# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# create a response function
def respond_to_prompt_only(prompt, username):
    instructions="you are a CampusHub AI assistant helping users with their campus related queries. Provide concise and accurate answers. be personable and friendly."
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # or another Gemini model
        contents = [{"name": username, "content": f"{instructions}\n\n{prompt}"}]
    )
    text_output = ""
    if hasattr(response, "candidates") and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        text_output += part.text

    if not text_output:
            text_output = "Sorry, I couldn’t generate a response."
    return text_output