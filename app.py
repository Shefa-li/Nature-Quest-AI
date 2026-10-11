
import os
from dotenv import load_dotenv
import base64
import random
from io import BytesIO
from flask import Flask, request, jsonify, render_template
from google import genai
from PIL import Image



load_dotenv() # Load variables from .env file

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

app = Flask(__name__)

# List of fun nature quests for kids
QUESTS = [
    "Find a yellow flower with 5 petals! 🌼",
    "Find a uniquely shaped leaf (like a star, heart, or jagged edge)! 🍃",
    "Find a patch of dark, rich forest soil and capture its color! 🟤",
    "Find a flower with multiple bright colors! 🌺",
    "Find a smooth, rounded pebble or textured rock! 🪨"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/get-quest", methods=["GET"])
def get_quest():
    # Pick a random quest for the kid
    quest = random.choice(QUESTS)
    return jsonify({"quest": quest})

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        image_data = data.get('image')
        current_quest = data.get('quest', 'Find something cool in nature!')
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400

        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        # Kid-friendly prompt that evaluates their find against the quest
        # Kid-friendly prompt with strict instruction to avoid markdown asterisks
        prompt = (
            f"The kid's active nature quest was: '{current_quest}'. "
            "Look at the uploaded photo. Act like an enthusiastic, magical forest guide talking to a child: "
            "1. Cheerfully check if they matched the quest or found something awesome. "
            "2. Identify what plant, flower, or object is in the picture. "
            "3. Share a super cool, simple 1-sentence science fact about it. "
            "CRITICAL FORMATTING RULE: Do not use any markdown bold symbols like asterisks (**). Write entirely in plain text using emojis for excitement."
        )
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[prompt, image]
        )

        return jsonify({"text": response.text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)