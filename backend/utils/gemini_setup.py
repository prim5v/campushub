from google import genai

GEMINI_API_KEY = "AIzaSyAtkaFIx3xH8uOqLapwUEU6pn4ptVvHpDI"
client = genai.Client(api_key=GEMINI_API_KEY)

def respond_to_prompt_only(prompt, username):
    instructions = (
        "You are a CampusHub AI assistant helping users with campus-related queries. "
        "Provide concise and accurate answers. Be personable and friendly."
    )

    full_prompt = f"{instructions}\n\nUser ({username}): {prompt}"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt  # ✅ STRING, not dict/list
        )

        text_output = ""
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        text_output += part.text

        return text_output or "Sorry, I couldn’t generate a response. There is posibly an error"

    except Exception as e:
        print("❌ Gemini API error:", str(e))
        return "Sorry, there was an error processing your request.", str(e)
