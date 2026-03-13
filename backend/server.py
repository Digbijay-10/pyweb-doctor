from flask import Flask, request, jsonify
import requests
import re

API_KEY = "AIzaSyCSVxjIDa18F26xto8DZyedHTqN2LSU6e8"

app = Flask(__name__)

# =========================
# Helper: clean AI output
# =========================

def clean_code(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    if "```" in text:
        parts = text.split("```")
        for p in parts:
            if "\n" in p:
                text = p
                break

    text = text.replace("```", "").strip()

    lines = text.splitlines()

    if len(lines) > 1:
        first = lines[0].strip().lower()

        if first.isalpha() and len(first) < 12:
            text = "\n".join(lines[1:])

    return text.strip()


# =========================
# FIX
# =========================

@app.route("/fix", methods=["POST"])
def fix():

    data = request.json

    code = data.get("code", "")
    error = data.get("error", "")

    prompt = f"""
Explain the code briefly.

Rules:
Keep explanation short
Max 4 lines

Format:
Mistake:
Fix:
Meaning:

Code:
{code}

Error:
{error}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + API_KEY
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 2048
        }
    }

    r = requests.post(url, json=body)
    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = code

    text = clean_code(text)

    return jsonify({"result": text})


# =========================
# REVERSE DEBUG
# =========================

@app.route("/reverse", methods=["POST"])
def reverse():

    data = request.json

    code = data.get("code", "")
    expected = data.get("expected", "")
    time_c = data.get("time", "")
    space_c = data.get("space", "")
    optimize = data.get("optimize", "")

    prompt = f"""
You are an expert Python debugger and optimizer.

Expected output:
{expected}

Required time complexity:
{time_c}

Required space complexity:
{space_c}

Optimization goal:
{optimize}

Task:
Fix the code
Optimize the code
Match expected output
Improve performance if possible
Keep code clean

Code:
{code}

Return in this format:

FIXED: <code>

EXPLANATION:
What changed:
Why optimized:
Time complexity:
Space complexity:
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + API_KEY
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }

    r = requests.post(url, json=body)
    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = ""

    fixed = ""
    explanation = ""

    if "EXPLANATION:" in text:
        parts = text.split("EXPLANATION:")
        fixed = parts[0].replace("FIXED:", "").strip()
        explanation = parts[1].strip()
    else:
        fixed = text.strip()

    fixed = clean_code(fixed)

    return jsonify({
        "fixed": fixed,
        "explanation": explanation
    })


# =========================
# EXPLAIN
# =========================

@app.route("/explain", methods=["POST"])
def explain():

    data = request.json

    code = data.get("code", "")
    error = data.get("error", "")

    prompt = f"""
Explain the code.

Format:

Code Status:
Mistake:
Correction:
What code does:

Code:
{code}

Error:
{error}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + API_KEY
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }

    r = requests.post(url, json=body)
    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = ""

    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = text.replace("```", "")

    return jsonify({
        "explanation": text.strip()
    })


# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)