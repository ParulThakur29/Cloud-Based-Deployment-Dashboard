from flask import Flask, render_template, request, redirect, jsonify, session
import psutil
import sqlite3
from database import init_db
from deploy import deploy_app, stop_app

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid login"

    return render_template('login.html')


# 🔐 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# 🏠 DASHBOARD
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('apps.db')
    apps = conn.execute("SELECT * FROM apps").fetchall()
    conn.close()

    stats = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent
    }

    return render_template('index.html', apps=apps, stats=stats)


# 🚀 DEPLOY
@app.route('/deploy', methods=['POST'])
def deploy():
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    image = request.form['image']

    try:
        container_id = deploy_app(image)

        conn = sqlite3.connect('apps.db')
        conn.execute(
            "INSERT INTO apps (name, status, container_id) VALUES (?, ?, ?)",
            (name, "Running", container_id)
        )
        conn.commit()
        conn.close()

        return redirect('/')
    
    except Exception as e:
        return f"Error: {str(e)}"


# 🛑 STOP
@app.route('/stop/<container_id>')
def stop(container_id):
    if 'user' not in session:
        return redirect('/login')

    stop_app(container_id)

    conn = sqlite3.connect('apps.db')
    conn.execute(
        "UPDATE apps SET status=? WHERE container_id=?",
        ("Stopped", container_id)
    )
    conn.commit()
    conn.close()

    return redirect('/')


# 📊 STATS API
@app.route('/stats')
def stats_api():
    return jsonify({
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent
    })


if __name__ == '__main__':
    app.run(debug=True)