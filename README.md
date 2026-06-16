# AI-Powered Content Operations Assistant

## 📌 Overview
The **AI-Powered Content Operations Assistant** is a Flask-based web application that helps teams manage, analyze, and automate content requests using AI (Google Gemini API) with a rule-based fallback system.

It takes a content request as input and generates:
- Campaign type
- Target audience
- Content formats
- Required teams
- Summary
- Task breakdown

---

## 🚀 Features
- AI-powered content analysis using Google Gemini API
- Automatic fallback rule-based system if AI fails or quota exceeds
- Content request submission form
- Smart campaign classification (Festival, Product Launch, Promotions, etc.)
- Audience detection
- Platform-based format suggestions (Instagram, LinkedIn, YouTube, etc.)
- Task generation for workflow planning
- Dashboard with:
  - Search
  - Filter (Platform, Priority)
  - Sorting (Deadline, Priority, Date)
- Delete request functionality
- SQLite database integration

---

## 🛠️ Tech Stack
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- Google Gemini AI API

---

## 📁 Project Structure
AI_Content_Assistant/
│
├── app.py
├── templates/
│ ├── index.html
│ └── dashboard.html
├── content.db
├── .env 
└── README.md


---

## ⚙️ Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Arqam-M/ai-content-operations-assistant.git
cd ai-content-operations-assistant
```
1. Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows    

2. Install Dependencies
pip install flask flask_sqlalchemy python-dotenv google-generativeai

3. Run the Application
python app.py

⚠️ Important Notes
If Gemini API quota is exceeded, system automatically switches to rule-based fallback
Make sure internet is available for AI features

🧠 AI Logic

The system uses:

Google Gemini API (Primary AI engine)
Rule-based fallback system (backup logic when API fails)

Fallback triggers when:

API quota is exceeded
API is unavailable
Invalid response is returned
