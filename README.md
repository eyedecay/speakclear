# SpeakClear
> Real-time audio transcription and speech analysis web app to help users improve communication skills.


---

## Overview
SpeakClear is a web application that allows users to record or upload audio, transcribes it in real-time, detects filler words, and highlights areas of high or low understanding.  
It is ideal for improving public speaking, presentations, or communication skills.

---

## Features
- Real-time audio transcription
- Filler word detection
- Visual feedback for speech clarity
- Supports multiple languages
- Modern React frontend with FastAPI backend

---

## Tech Stack
| Layer        | Technology |
|--------------|------------|
| Frontend     | React, HTML, CSS, JavaScript |
| Backend      | Python, FastAPI |
---

## Installation

### Prerequisites
- Python 3.9+  
- Node.js 18+  
- npm 

### Backend
```bash
# Clone repo
git clone https://github.com/username/speakclear.git
cd speakclear/app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

### Frontend
```bash
# Navigate to the frontend (client) directory
cd ../client   

# Install dependencies
npm install

# Start development server
npm run dev