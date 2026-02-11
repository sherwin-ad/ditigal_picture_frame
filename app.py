
import os
import threading
import webbrowser
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from feh_manager import FehController

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flashing messages

# Configuration
UPLOAD_FOLDER = os.path.join('static', 'photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMIN_PASSWORD = 'admin'  # Set your desired password here

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ADMIN_PASSWORD'] = ADMIN_PASSWORD
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize FehController
feh = FehController(app.config['UPLOAD_FOLDER'])
# Try to start the slideshow on launch (will only work on Linux with display)
try:
    feh.start()
except Exception as e:
    print(f"Could not start feh automatically: {e}")

def open_browser():
    """Open the slideshow in the default web browser after a short delay."""
    webbrowser.open('http://localhost:5000/play')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            flash('Logged in successfully.')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('Invalid password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out.')
    return redirect(url_for('login'))

def get_images():
    images = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                images.append(filename)
    images.sort()
    return images

@app.route('/')
@login_required
def index():
    images = get_images()
    return render_template('index.html', images=images, mode='admin')

@app.route('/play')
def play():
    """Public route for the slideshow (read-only, for local display)."""
    images = get_images()
    return render_template('index.html', images=images, mode='display')

@app.route('/gallery')
@login_required
def gallery():
    images = get_images()
    return render_template('gallery.html', images=images)


@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    if not allowed_file(filename):
         flash('Invalid file type')
         return redirect(url_for('gallery'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'Deleted {filename}')
        except Exception as e:
            flash(f'Error deleting file: {e}')
    else:
        flash('File not found')
    
    return redirect(url_for('gallery'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'files[]' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    
    uploaded = False
    for file in files:
        if not file or not file.filename:
            continue
        
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded = True
    
    if uploaded:
        flash('Files successfully uploaded')
        # Optional: feh has --reload which auto-reloads, but we can force restart if needed
        # feh.restart() 
    else:
        flash('No valid files uploaded')

    return redirect(url_for('index'))

@app.route('/control/feh/<action>')
@login_required
def control_feh(action):
    if action == 'start':
        feh.start()
        flash('Started local slideshow (feh)')
    elif action == 'stop':
        feh.stop()
        flash('Stopped local slideshow (feh)')
    elif action == 'restart':
        feh.restart()
        flash('Restarted local slideshow (feh)')
    else:
        flash(f'Unknown action: {action}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Open browser on startup (delayed to allow server to start)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.5, open_browser).start()
    
    # Run on 0.0.0.0 to be accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
