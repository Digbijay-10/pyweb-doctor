from flask import Flask, request, jsonify
import requests
import re

API_KEY = ""

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
You are a Python debugger.

Fix the code error.

Rules:
Return fixed code
Do not explain too much

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
            "maxOutputTokens": 4096
        }
    }

    r = requests.post(url, json=body)

    print("STATUS:", r.status_code)
    print("RAW:", r.text)

    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = code

    # -------- FIX PARSER --------

    fixed = text

    if "Fix:" in text:
        parts = text.split("Fix:")
        fixed = parts[1]

    if "Meaning:" in fixed:
        fixed = fixed.split("Meaning:")[0]

    fixed = clean_code(fixed)

    return jsonify({"result": fixed.strip()})


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
You are a senior Python debugger, optimizer, and competitive programmer.

Your job is STRICT:

- Fix the code
- Ensure expected output is correct
- Ensure code runs without error
- Follow required complexity
- Optimize if possible
- Rewrite completely if needed
- Always return valid Python code

Expected output:
{expected}

Required time complexity:
{time_c}

Required space complexity:
{space_c}

Optimization goal:
{optimize}

Code:
{code}

Rules:

- If logic is wrong → rewrite code
- If syntax wrong → fix
- If slow → optimize
- If output mismatch → correct
- Code must run
- Code must be clean

Return ONLY in this format:

FIXED:
<code>

EXPLANATION:
What changed:
Why changed:
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
            "maxOutputTokens": 4096
        }
    }

    # -------------------
    # RETRY MODE
    # -------------------

    text = ""
    r = None

    for _ in range(2):

        r = requests.post(url, json=body)

        print("STATUS:", r.status_code)
        print("RAW:", r.text)

        try:
            result = r.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
        except:
            text = ""

        if "FIXED:" in text:
            break


    # -------------------
    # PARSER (JUDGE MODE)
    # -------------------

    fixed = ""
    explanation = ""

    if "FIXED:" in text:
        parts = text.split("FIXED:")
        rest = parts[1]

        if "EXPLANATION:" in rest:
            parts2 = rest.split("EXPLANATION:")
            fixed = parts2[0].strip()
            explanation = parts2[1].strip()
        else:
            fixed = rest.strip()

    else:
        fixed = text.strip()
        explanation = "Model format incorrect, fallback used"


    fixed = clean_code(fixed)

    if not fixed:
        fixed = code
        explanation = "Failed to generate fix, returned original code"


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
            "maxOutputTokens": 4096
        }
    }

    r = requests.post(url, json=body)

    print("STATUS:", r.status_code)
    print("RAW:", r.text)

    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = ""

    # safer cleanup
    text = text.replace("```python", "")
    text = text.replace("```", "")


    return jsonify({
        "explanation": text.strip()
    })


# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
