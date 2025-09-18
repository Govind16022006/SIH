sizzwfrom flask import Flask, request, jsonify, render_template, redirect, url_for
import openai
import requests
import time
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add your actual OpenAI API Key here
openai.api_key = "YOUR_OPENAI_API_KEY"
# Add your D-ID API Key here
DID_API_KEY = "YOUR_DID_API_KEY"

# Simple in-memory user store
users = {}

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        for user in users.values():
            if user.email == email and user.password == password:
                login_user(user)
                return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    else:
        return render_template('login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if any(u.email == email for u in users.values()):
            return render_template('signup.html', error="Email already registered")
        user_id = str(len(users) + 1)
        new_user = User(user_id, name, email, password)
        users[user_id] = new_user
        login_user(new_user)
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')

@app.route('/guest')
def guest():
    guest_user = User('guest', 'Guest User', 'guest@example.com', '')
    users['guest'] = guest_user
    login_user(guest_user)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

@app.route('/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()
    question = data.get('question')

    # Call OpenAI GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": "GPT Error", "details": str(e)})

    # Send to D-ID for talking video
    try:
        headers = {
            "Authorization": f"Bearer {DID_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "script": {
                "type": "text",
                "input": answer
            },
            "source_url": "https://create-images-results.d-id.com/DefaultVideoCharacter1.png"
        }

        response = requests.post("https://api.d-id.com/talks", json=payload, headers=headers)
        talk_id = response.json().get("id")

        # Poll until video is ready
        video_url = None
        for _ in range(10):
            status_response = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
            status_data = status_response.json()
            video_url = status_data.get("result_url")
            if video_url:
                break
            time.sleep(2)

        if not video_url:
            return jsonify({"error": "Video generation failed"})

        return jsonify({"answer": answer, "video_url": video_url})

    except Exception as e:
        return jsonify({"error": "D-ID Error", "details": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
