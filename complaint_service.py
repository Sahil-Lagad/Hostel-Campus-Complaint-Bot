import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

ALLOWED_CATEGORIES = [
    "Electrical", "Water", "Mess/Food", "Cleanliness",
    "Internet/Network", "Maintenance", "Security", "Other"
]
ALLOWED_URGENCIES = ["Low", "Medium", "High", "Critical"]

SYSTEM_PROMPT = """
You are a campus complaint classification assistant.
Classify the complaint into exactly one category from:
Electrical, Water, Mess/Food, Cleanliness, Internet/Network,
Maintenance, Security, Other.
Classify urgency as Low, Medium, High, or Critical.
Critical means an immediate danger to life or serious safety risk (for example,
fire, exposed live wires, gas leak, severe violence). High means urgent disruption
or risk requiring prompt attention. Medium means a normal issue needing attention.
Low means minor or non-urgent.
Return ONLY valid JSON with keys: category, urgency, summary.
The summary must be one short sentence. Do not invent facts.
"""

def _fallback_classify(text: str) -> dict:
    t = text.lower()
    category_keywords = {
        "Electrical": ["electric", "light", "fan", "wire", "power", "socket", "switch", "short circuit"],
        "Water": ["water", "tap", "leak", "pipe", "bathroom", "toilet", "drain"],
        "Mess/Food": ["mess", "food", "meal", "canteen", "cook", "rotten", "food poisoning"],
        "Cleanliness": ["clean", "garbage", "dust", "dirty", "pest", "mosquito", "rats"],
        "Internet/Network": ["internet", "wifi", "wi-fi", "network", "router", "connection"],
        "Maintenance": ["broken", "repair", "door", "window", "bed", "furniture", "maintenance"],
        "Security": ["security", "theft", "stolen", "fight", "unsafe", "harassment", "intruder"],
    }
    category = "Other"
    for name, keywords in category_keywords.items():
        if any(word in t for word in keywords):
            category = name
            break

    critical_words = ["fire", "smoke", "gas leak", "live wire", "electrocution", "serious injury"]
    high_words = ["urgent", "flood", "overflow", "theft", "unsafe", "sparking", "short circuit"]
    urgency = "Medium"
    if any(word in t for word in critical_words):
        urgency = "Critical"
    elif any(word in t for word in high_words):
        urgency = "High"
    elif any(word in t for word in ["minor", "small", "occasionally", "not urgent"]):
        urgency = "Low"
    summary = text.strip().replace("\n", " ")
    summary = summary[:160] + ("..." if len(summary) > 160 else "")
    return {"category": category, "urgency": urgency, "summary": summary, "ai_used": False}

def classify_complaint(complaint_text: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not api_key:
        return _fallback_classify(complaint_text)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=250,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": complaint_text}
            ],
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE)
        data = json.loads(content)
        category = data.get("category", "Other")
        urgency = data.get("urgency", "Medium")
        if category not in ALLOWED_CATEGORIES:
            category = "Other"
        if urgency not in ALLOWED_URGENCIES:
            urgency = "Medium"
        summary = str(data.get("summary", complaint_text)).strip()[:240]
        return {"category": category, "urgency": urgency, "summary": summary, "ai_used": True}
    except Exception:
        return _fallback_classify(complaint_text)
