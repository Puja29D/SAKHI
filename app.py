from flask import Flask, render_template, request, jsonify, session, g, redirect, url_for, make_response, send_from_directory
from database import db, init_db
from models import User, ActivityLog, RightsView, CalmSession, StreakTracker, ParentActivity
import random
from datetime import datetime
import os
import io
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyAaQKM1s33sNlNgNd-NAyMBgyPxbet76Is"))

# Create the model
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 1024,
}
model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  generation_config=generation_config,
  system_instruction="""You are a helpful and friendly customer support assistant for Sakhi.

Your role is to:
- Greet visitors warmly and assist them with any questions about Sakhi's platform.
- Help users navigate the website and find what they need (Healing Tools, My Rights, Dashboard).
- Handle common FAQs efficiently.
- Escalate complex issues to a human agent or helpline when needed.

Guidelines:
- Always maintain a professional, empathetic, friendly, and helpful tone.
- Keep responses concise and easy to understand.
- If you don't know the answer to something, say so honestly and offer to connect the user with a team member.
- Do not make up information or promises that aren't true.
- Respond only in the language the user writes in.

Business Details:
- Company Name: Sakhi
- Services/Products: A safe space application providing healing tools, rights awareness, and progress tracking for users, plus a parent dashboard.
- Working Hours: 24/7 online platform
- Contact Email: support@sakhi.example.com

If a user wants to speak to a human or needs urgent help, direct them to: support@sakhi.example.com or National Helplines (India) - iCall: 9152987821, Women Helpline: 1091."""
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sakhi-safe-space-key' # In production, use environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sakhi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

# --- Helper Functions ---

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def log_activity(page_name):
    user = get_current_user()
    if user:
        log = ActivityLog(user_id=user.id, page_visited=page_name)
        db.session.add(log)
        db.session.commit()

# --- Routes ---

@app.route('/')
def index():
    # For prototype, auto-login or create a guest user if not present
    if 'user_id' not in session:
        new_user = User(name="Brave One")
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
    
    return render_template('dashboard.html', user=get_current_user())

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return index() # Redirect to creation/login
        
    log_activity('dashboard')
    
    # Mock data for activity summary
    days_joined = (datetime.utcnow() - user.created_at).days
    resources_accessed = ActivityLog.query.filter_by(user_id=user.id).count()
    calm_sessions = CalmSession.query.filter_by(user_id=user.id).count()
    
    return render_template('dashboard.html', 
                           user=user, 
                           days_joined=days_joined,
                           resources_accessed=resources_accessed,
                           calm_sessions=calm_sessions)

@app.route('/rights')
def rights():
    log_activity('rights')
    return render_template('rights.html')

@app.route('/calm')
def calm():
    log_activity('calm')
    return render_template('calm.html')


@app.route('/parent/dashboard')
def parent_dashboard_redirect():
    return redirect(url_for('parent_dashboard'))

@app.route('/parent-dashboard')
def parent_dashboard():
    # Parent dashboard might not user the main user session, or could use a separate one.
    # For now, we'll just log it as a page visit if a user is logged in, 
    # but strictly it's for parents.
    return render_template('parent_dashboard.html')

@app.route('/quick-exit')
def quick_exit():
    session.clear()
    return jsonify({"status": "success", "url": "https://www.google.com"})

@app.route('/sounds/<path:filename>')
def serve_sounds(filename):
    return send_from_directory('sounds', filename)

# --- API Endpoints ---

QUOTE_LIST = [
    "You are stronger than you know.",
    "Peace begins with a deep breath.",
    "Your courage is your crown.",
    "Healing is not linear, and that is okay.",
    "You are worthy of safety and joy."
]

@app.route('/api/quote')
def get_quote():
    return jsonify({"quote": random.choice(QUOTE_LIST)})

@app.route('/api/mood', methods=['POST'])
def save_mood():
    user = get_current_user()
    if user:
        mood = request.json.get('mood')
        user.mood_today = mood
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "User not found"}), 404

@app.route('/api/calm-session', methods=['POST'])
def save_calm_session():
    user = get_current_user()
    if user:
        data = request.json
        session_log = CalmSession(
            user_id=user.id,
            type=data.get('type'),
            duration_seconds=data.get('duration')
        )
        db.session.add(session_log)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "User not found"}), 404

@app.route('/api/streak', methods=['GET'])
def get_streak():
    user = get_current_user()
    if user:
        # Simple Logic: Just return stored streak for now
        return jsonify({"streak": user.streak_days})
    return jsonify({"streak": 0})

@app.route('/api/rights-content')
def get_rights_content():
    # Content could be loaded from a JSON file or DB in a real app
    # For this prototype, we'll serve it static or render in template
    return jsonify({"status": "ready"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"status": "error", "message": "Empty message"}), 400
        
    try:
        # We start a new chat session for each request in this prototype.
        # In a real application, you'd maintain chat history in the DB or session.
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        return jsonify({"status": "success", "response": response.text})
    except Exception as e:
        error_msg = str(e)
        print(f"Chat API Error: {error_msg}")
        if "api key" in error_msg.lower() or "api_key" in error_msg.lower() or "invalid argument" in error_msg.lower():
             fallback_response = "Hi! I am currently in **Offline Demo Mode** because my Gemini API key is invalid or missing.\n\n*(Note for admin: The string `gen-lang-client-0477143991` is a Google Cloud Project ID, not an API key. Please obtain a valid API key starting with `AIza...` from Google AI Studio and update the configuration).* \n\nHow can I help you once I'm online?"
             return jsonify({"status": "success", "response": fallback_response})
             
        return jsonify({"status": "error", "message": "I'm having trouble connecting right now. Please try again later."}), 500

@app.route('/download/first-steps-guide')
def download_first_steps_guide():
    """Generate and serve the 'First Steps' Guide as a downloadable PDF."""
    # Build a minimal valid PDF manually (no extra dependencies needed)
    pdf_content = _generate_first_steps_pdf()
    
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=Sakhi_First_Steps_Guide.pdf'
    return response

def _generate_first_steps_pdf():
    """Generate a simple PDF document with the First Steps guide content."""
    # Content for the guide
    sections = [
        ("SAKHI - First Steps Guide for Parents & Guardians", ""),
        ("", "This guide is for parents and guardians who have learned that their"),
        ("", "child may have experienced abuse. Your response matters deeply."),
        ("", ""),
        ("Step 1: Stay Calm", ""),
        ("", "Your child needs to see that you are a safe person to talk to."),
        ("", "Take a deep breath before responding. Your composure gives them strength."),
        ("", ""),
        ("Step 2: Listen and Believe", ""),
        ("", "Say: 'I believe you. I am here for you. It is not your fault.'"),
        ("", "Avoid: 'Why didn't you tell me sooner?' or any blaming questions."),
        ("", "Let them share at their own pace. Do not pressure for details."),
        ("", ""),
        ("Step 3: Ensure Immediate Safety", ""),
        ("", "- Is the offender still accessible to the child? Ensure physical separation."),
        ("", "- Does the child need urgent medical care?"),
        ("", "- Preserve evidence if the incident was recent."),
        ("", "  (Do not wash clothes or bathe if possible)"),
        ("", ""),
        ("Step 4: Report and Seek Help", ""),
        ("", "CHILDLINE (India): 1098 - Free, 24/7, anonymous"),
        ("", "Police Emergency: 100"),
        ("", "Women Helpline: 1091"),
        ("", "iCall Helpline: 9152987821"),
        ("", ""),
        ("Step 5: Get Professional Support", ""),
        ("", "- Find a child psychologist or trauma-informed therapist."),
        ("", "- Consider family counseling to support healing together."),
        ("", "- Your child's school counselor can also be a resource."),
        ("", ""),
        ("Step 6: Know the Law - POCSO Act", ""),
        ("", "The Protection of Children from Sexual Offences (POCSO) Act, 2012"),
        ("", "makes it mandatory to report child sexual abuse."),
        ("", "- Reporting is confidential and child-friendly."),
        ("", "- The child's identity is protected by law."),
        ("", "- You will NOT get in trouble for reporting."),
        ("", ""),
        ("Remember", ""),
        ("", "Healing takes time. Your child's recovery begins with your support."),
        ("", "You showed up. That is what matters."),
        ("", ""),
        ("", "For more resources, visit Sakhi at support@sakhi.example.com"),
    ]

    # Build PDF content using raw PDF format
    buf = io.BytesIO()
    
    # Build page content lines
    lines = []
    y = 750  # Start position from top
    for title, text in sections:
        if title:
            lines.append(f"BT /F2 14 Tf {50} {y} Td ({_pdf_escape(title)}) Tj ET")
            y -= 22
        if text:
            lines.append(f"BT /F1 11 Tf {55} {y} Td ({_pdf_escape(text)}) Tj ET")
            y -= 16
        if not title and not text:
            y -= 10
        # Start a new page if running low on space
        if y < 60:
            y = 750
    
    stream_content = "\n".join(lines)
    stream_length = len(stream_content)
    
    pdf = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>
endobj

4 0 obj
<< /Length {stream_length} >>
stream
{stream_content}
endstream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

6 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>
endobj

xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000{str(317 + stream_length).zfill(3)} 00000 n 
0000000{str(394 + stream_length).zfill(3)} 00000 n 

trailer
<< /Size 7 /Root 1 0 R >>
startxref
{471 + stream_length}
%%EOF"""
    
    return pdf.encode('latin-1')

def _pdf_escape(text):
    """Escape special PDF characters in text."""
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)').replace("'", "\\'") 

if __name__ == '__main__':
    app.run(debug=True, port=5000)
