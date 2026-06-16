from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)

# ================= DATABASE =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODEL =================
class ContentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    audience = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    deadline = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    campaign_type = db.Column(db.String(100))
    formats = db.Column(db.Text)
    teams = db.Column(db.Text)
    summary = db.Column(db.Text)
    tasks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================= RULE-BASED FALLBACK =================
def rule_based_analysis(description, platform):
    text = description.lower()

    if "diwali" in text or "festival" in text:
        campaign_type = "Festival Marketing Campaign"
        summary = f"A festival-themed campaign on {platform} with creative designs and influencer shoutouts."
    elif "launch" in text:
        campaign_type = "Product Launch Campaign"
        summary = f"A product launch campaign on {platform} with influencer and video support."
    elif "sale" in text or "discount" in text:
        campaign_type = "Promotional Campaign"
        summary = f"A promotional campaign on {platform} highlighting discounts and offers."
    else:
        campaign_type = "General Marketing Campaign"
        summary = f"A general marketing campaign on {platform} with creative content planning."

    if "women" in text:
        audience = "Women (18–35)"
    elif "men" in text:
        audience = "Men (18–35)"
    elif "student" in text or "college" in text:
        audience = "Students (18–25)"
    else:
        audience = "General Audience"

    formats_map = {
        "Instagram": ["Reels", "Stories", "Influencer Content"],
        "LinkedIn": ["Posts", "Articles", "Carousels"],
        "YouTube": ["Videos", "Shorts"],
        "Facebook": ["Posts", "Ads"],
        "Website": ["Blog Posts", "Landing Pages"],
        "Email Marketing": ["Newsletters", "Promotional Emails"]
    }
    formats = formats_map.get(platform, ["General Content"])

    teams = ["Content Team", "Creative Team", "Marketing Team"]
    if "influencer" in text:
        teams.append("Influencer Marketing Team")
    if "video" in text or "reel" in text:
        teams.append("Video Production Team")

    tasks = [
        "Campaign Research",
        "Concept Creation",
        "Content Planning",
        "Design Creation",
        "Review & Approval",
        "Content Scheduling"
    ]
    if "diwali" in text or "festival" in text:
        tasks.append("Festival Theme Design")
    if "influencer" in text:
        tasks.append("Influencer Identification")
    if "reel" in text or "video" in text:
        tasks.append("Reels Script Writing")

    return {
        "campaign_type": campaign_type,
        "audience": audience,
        "formats": ", ".join(formats),
        "teams": ", ".join(teams),
        "summary": summary,
        "tasks": ", ".join(tasks)
    }


# ================= AI LOGIC =================
def analyze_request(description, platform, audience):

    try:
        print("🔥 USING GEMINI AI")
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are an expert marketing strategist.

Analyze the following content request.

Target Audience:
{audience}

Description:
{description}

Platform:
{platform}

Return ONLY valid JSON:

{{
    "campaign_type": "string",
    "audience": "string",
    "formats": ["format1","format2"],
    "teams": ["team1","team2"],
    "summary": "short summary",
    "tasks": ["task1","task2","task3"]
}}
"""

        response = model.generate_content(prompt)

        ai_output = response.text.strip()

        # Remove markdown code blocks if Gemini adds them
        ai_output = ai_output.replace("```json", "").replace("```", "").strip()

        analysis = json.loads(ai_output)

        return {
            "campaign_type": analysis.get("campaign_type", ""),
            "audience": analysis.get("audience", audience),
            "formats": ", ".join(analysis.get("formats", [])),
            "teams": ", ".join(analysis.get("teams", [])),
            "summary": analysis.get("summary", ""),
            "tasks": ", ".join(analysis.get("tasks", []))
        }

    except Exception as e:
        print("Gemini Error:", e)
        print("🔁 USING RULE-BASED FALLBACK")
        
        return rule_based_analysis(description, platform)


# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.form
    analysis = analyze_request(data["description"], data["platform"], data["audience"])

    new_request = ContentRequest(
        client=data["client"],
        brand=data["brand"],
        title=data["title"],
        description=data["description"],
        audience=data["audience"],
        platform=data["platform"],
        deadline=data["deadline"],
        priority=data["priority"],
        campaign_type=analysis["campaign_type"],
        formats=analysis["formats"],
        teams=analysis["teams"],
        summary=analysis["summary"],
        tasks=analysis["tasks"]
    )

    db.session.add(new_request)
    db.session.commit()
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    search = request.args.get("search", "")
    platform_filter = request.args.get("platform", "")
    priority_filter = request.args.get("priority", "")
    sort_by = request.args.get("sort", "created_at")

    query = ContentRequest.query
    if search:
        query = query.filter(
            (ContentRequest.client.contains(search)) |
            (ContentRequest.brand.contains(search)) |
            (ContentRequest.title.contains(search))
        )
    if platform_filter:
        query = query.filter_by(platform=platform_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)

    if sort_by == "deadline":
        query = query.order_by(ContentRequest.deadline.asc())
    elif sort_by == "priority":
        query = query.order_by(ContentRequest.priority.asc())
    else:
        query = query.order_by(ContentRequest.created_at.desc())

    requests = query.all()
    return render_template("dashboard.html", requests=requests)

@app.route("/delete/<int:id>")
def delete_request(id):
    record = ContentRequest.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect("/dashboard")

# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)  