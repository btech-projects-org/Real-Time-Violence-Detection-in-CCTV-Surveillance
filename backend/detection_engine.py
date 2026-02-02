import google.generativeai as genai
import os
from dotenv import load_dotenv
import cv2
import base64
import json

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
# Enable real AI detection
DEMO_MODE = False
if api_key:
    genai.configure(api_key=api_key)
    print("✅ Gemini AI enabled - Real-time detection active")
else:
    DEMO_MODE = True
    print("⚠️ No API key found - Running in DEMO MODE")

class DetectionEngine:
    def __init__(self):
        if not DEMO_MODE:
            # Use gemini-2.0-flash-001 for image analysis (stable version)
            self.model = genai.GenerativeModel('models/gemini-2.0-flash-001')

    async def analyze_frame(self, frame):
        if DEMO_MODE:
            import random
            # Simulate threats with angry face and weapon detection
            rand_val = random.random()
            
            # Simulate angry face + weapon (highest threat)
            if rand_val < 0.03:
                return {
                    "detected": True,
                    "type": "angry_face_with_weapon",
                    "confidence": round(random.uniform(0.85, 0.98), 2),
                    "description": "DEMO: Angry person holding a weapon detected - High threat!",
                    "angry_face": True,
                    "weapon": True
                }
            # Simulate angry face only
            elif rand_val < 0.06:
                return {
                    "detected": True,
                    "type": "angry_face",
                    "confidence": round(random.uniform(0.75, 0.90), 2),
                    "description": "DEMO: Angry facial expression detected",
                    "angry_face": True,
                    "weapon": False
                }
            # Simulate other violence types
            elif rand_val < 0.08:
                threat_types = ["fighting", "assault", "vandalism", "weapon"]
                t_type = random.choice(threat_types)
                return {
                    "detected": True,
                    "type": t_type,
                    "confidence": round(random.uniform(0.75, 0.95), 2),
                    "description": f"DEMO: Simulated {t_type} detected in surveillance feed.",
                    "angry_face": False,
                    "weapon": (t_type == "weapon")
                }
            
            return {"detected": False, "type": "none", "confidence": 0.0, "description": "Normal activity", "angry_face": False, "weapon": False}

        # Convert frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        base64_image = base64.b64encode(buffer).decode('utf-8')

        prompt = """
        Analyze this CCTV frame for:
        1. Violence or threatening behavior
        2. Angry or aggressive facial expressions
        3. Weapons (guns, knives, bats, etc.)
        
        Pay special attention to: If a person shows an angry facial expression AND is holding a weapon, 
        this is a HIGH PRIORITY threat.
        
        Respond in JSON format with the following fields:
        - "detected": boolean (true if any threat detected)
        - "type": string (e.g., "angry_face_with_weapon", "angry_face", "fighting", "assault", "weapon", "none")
        - "confidence": float (0.0 to 1.0)
        - "description": string (detailed explanation of what was detected)
        - "angry_face": boolean (true if angry/aggressive expression detected)
        - "weapon": boolean (true if weapon detected)
        """

        try:
            print("🔍 Analyzing frame with Gemini AI...")
            response = await self.model.generate_content_async(
                [prompt, {"mime_type": "image/jpeg", "data": base64_image}]
            )
            
            # Parse JSON from response text
            response_text = response.text.strip()
            print(f"🤖 Raw AI response: {response_text}")
            
            # Try to extract JSON if it's wrapped in markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            print(f"📊 Analysis result: {result}")
            return result
        except Exception as e:
            print(f"❌ Error in Gemini detection: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"detected": False, "type": "none", "confidence": 0.0, "description": f"Error: {str(e)}", "angry_face": False, "weapon": False}

detection_engine = DetectionEngine()
