# StackSage (pyweb-doctor)

StackSage is an AI-powered VS Code extension that fixes, explains, and improves code using Google Gemini API with a Python Flask backend.

This project was built for the Google Gemini AI Hackathon.

---

## Features

- Fix incorrect code using AI
- Explain code in simple language
- Improve code quality
- Works inside VS Code
- Python backend using Flask
- Gemini API integration
- Automatic response cleaning
- Handles indentation errors

Commands available:

- Fix Code
- Explain Code
- Improve Code

---

## Technologies Used

- Google Gemini API
- Python Flask backend
- TypeScript VS Code extension
- Node.js
- REST API
- JSON
- GitHub

---

## Requirements

Install before running:

- Python 3.10+
- Node.js
- VS Code
- Gemini API key

Install Python packages:

pip install flask requests google-genai

---

## Reproducible Testing Instructions

Follow these steps to run the project.

### 1. Clone repo

git clone https://github.com/YOUR_USERNAME/pyweb-doctor.git

cd pyweb-doctor


### 2. Setup backend

cd backend

pip install -r requirements.txt


### 3. Set API key

Windows PowerShell

$env:GEMINI_API_KEY="YOUR_API_KEY"

Linux / Mac

export GEMINI_API_KEY="YOUR_API_KEY"


### 4. Run backend

python server.py

Expected output:

Running on http://127.0.0.1:5000


### 5. Run extension

Open extension folder in VS Code

Press F5


### 6. Test

Open any Python file

Select code

Right click →

Fix Code / Explain Code / Improve Code


### Expected result

- Code fixed
- Explanation shown
- No backend errors

---

## Known Issues

- Requires internet connection
- Requires valid API key
- Backend must be running

---

## Release Notes

### 1.0.0

Initial release

- Fix code
- Explain code
- Improve code
- Gemini integration

---

## Future Improvements

- Cloud deployment
- More languages
- ADK agent support
- UI improvements

---

## Author

Built for Google Gemini Hackathon