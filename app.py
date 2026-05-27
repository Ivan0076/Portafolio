import os
import json
import uuid
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, abort, send_from_directory)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'portfolio-secret-2024-xyz-change-this')

# ── Config ───────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
# data.json lives in the uploads folder so it persists on Render disk
DATA_FILE     = os.path.join(UPLOAD_FOLDER, 'data.json')

# Archivos permitidos — incluye formatos 3D y video
ALLOWED_EXT = {
    # imágenes
    'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg',
    # video
    'mp4', 'webm', 'mov',
    # 3D
    'glb', 'gltf', 'obj', 'fbx',
}

# 500 MB — Flask sólo valida en disco; en Render el proxy acepta hasta el límite del plan
MAX_CONTENT = 500 * 1024 * 1024

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Owner credentials (¡CAMBIA ESTO!) ────────────────────────────────────────
OWNER_USERNAME     = os.environ.get('OWNER_USERNAME', 'admin')
OWNER_PASSWORD_HASH = os.environ.get(
    'OWNER_PASSWORD_HASH',
    generate_password_hash('portfolio2024!')
)

CATEGORIES = ['3D Models', '2D Animations', '3D Animations', 'Illustrations']

VIDEO_EXT  = {'mp4', 'webm', 'mov'}
MODEL3D_EXT = {'glb', 'gltf', 'obj', 'fbx'}

# ── Context processor ─────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    data = load_data()
    return {
        'now': datetime.now(),
        'profile': data['profile'],
        'VIDEO_EXT': VIDEO_EXT,
        'MODEL3D_EXT': MODEL3D_EXT,
    }

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(DATA_FILE):
        return {'projects': [], 'profile': default_profile()}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def default_profile():
    return {
        'name': 'Iván Aldama',
        'title': 'Diseñador Digital de Medios Interactivos',
        'bio': 'Apasionado por crear experiencias digitales memorables a través del diseño, la animación y la narrativa visual.',
        'location': 'Ciudad Juárez, México',
        'email': 'contacto@ejemplo.com',
        'skills': ['Modelado 3D', 'Animación 2D/3D', 'Ilustración Digital',
                   'Motion Graphics', 'UI/UX Design', 'Diseño Editorial'],
        'interests': ['Arte Digital', 'Cine de Animación', 'Videojuegos', 'Fotografía', 'Desarrollo web'],
        'tools': ['Blender', 'After Effects', 'Illustrator', 'Photoshop', 'Maya 3D', 'Figma'],
        'avatar': '',
    }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def get_file_type(filename):
    """Devuelve 'image' | 'video' | '3d' | 'unknown'"""
    if not filename or '.' not in filename:
        return 'unknown'
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in VIDEO_EXT:   return 'video'
    if ext in MODEL3D_EXT: return '3d'
    return 'image'

# ── Auth ──────────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Acceso restringido. Inicia sesión primero.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Public routes ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    data = load_data()
    recent = sorted(data['projects'], key=lambda p: p.get('date', ''), reverse=True)[:3]
    return render_template('index.html', profile=data['profile'], recent=recent)

@app.route('/portfolio')
def portfolio():
    data = load_data()
    cat  = request.args.get('category', 'all')
    projects = data['projects']
    if cat != 'all':
        projects = [p for p in projects if p.get('category') == cat]
    projects = sorted(projects, key=lambda p: p.get('date', ''), reverse=True)
    return render_template('portfolio.html', projects=projects,
                           categories=CATEGORIES, active_cat=cat,
                           profile=data['profile'])

@app.route('/project/<pid>')
def project_detail(pid):
    data = load_data()
    proj = next((p for p in data['projects'] if p['id'] == pid), None)
    if not proj:
        abort(404)
    file_type = get_file_type(proj.get('image', ''))
    thumb_type = get_file_type(proj.get('thumbnail', ''))
    return render_template('project_detail.html', project=proj,
                           profile=data['profile'],
                           file_type=file_type,
                           thumb_type=thumb_type)

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == OWNER_USERNAME and check_password_hash(OWNER_PASSWORD_HASH, password):
            session['logged_in'] = True
            session.permanent = False
            return redirect(url_for('dashboard'))
        error = 'Credenciales incorrectas.'
    return render_template('login.html', error=error)

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── Admin routes ──────────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
def dashboard():
    data = load_data()
    stats = {cat: sum(1 for p in data['projects'] if p.get('category') == cat)
             for cat in CATEGORIES}
    return render_template('dashboard.html', profile=data['profile'],
                           projects=data['projects'], stats=stats, categories=CATEGORIES)

def _save_upload(file_field_name):
    """Guarda un archivo subido y devuelve el nombre guardado o ''."""
    file = request.files.get(file_field_name)
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        fname = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, fname))
        return fname
    return ''

def _delete_upload(filename):
    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            os.remove(path)

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    data = load_data()
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '')
        desc     = request.form.get('description', '').strip()
        date     = request.form.get('date', datetime.today().strftime('%Y-%m-%d'))
        tags     = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
        orientation = request.form.get('orientation', 'landscape')  # landscape | portrait

        main_file = _save_upload('main_file')
        thumbnail = _save_upload('thumbnail')

        project = {
            'id': uuid.uuid4().hex,
            'title': title,
            'category': category,
            'description': desc,
            'date': date,
            'tags': tags,
            'image': main_file,        # archivo principal (imagen/video/3D)
            'thumbnail': thumbnail,    # miniatura manual (opcional)
            'orientation': orientation,
            'created_at': datetime.now().isoformat(),
        }
        data['projects'].append(project)
        save_data(data)
        flash('Proyecto creado exitosamente.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('project_form.html', project=None, categories=CATEGORIES, profile=data['profile'])

@app.route('/admin/project/<pid>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(pid):
    data = load_data()
    proj = next((p for p in data['projects'] if p['id'] == pid), None)
    if not proj:
        abort(404)
    if request.method == 'POST':
        proj['title']       = request.form.get('title', '').strip()
        proj['category']    = request.form.get('category', '')
        proj['description'] = request.form.get('description', '').strip()
        proj['date']        = request.form.get('date', proj['date'])
        proj['tags']        = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
        proj['orientation'] = request.form.get('orientation', proj.get('orientation', 'landscape'))

        new_main = _save_upload('main_file')
        if new_main:
            _delete_upload(proj.get('image'))
            proj['image'] = new_main

        new_thumb = _save_upload('thumbnail')
        if new_thumb:
            _delete_upload(proj.get('thumbnail'))
            proj['thumbnail'] = new_thumb

        save_data(data)
        flash('Proyecto actualizado.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('project_form.html', project=proj, categories=CATEGORIES, profile=data['profile'])

@app.route('/admin/project/<pid>/delete', methods=['POST'])
@login_required
def delete_project(pid):
    data = load_data()
    proj = next((p for p in data['projects'] if p['id'] == pid), None)
    if proj:
        _delete_upload(proj.get('image'))
        _delete_upload(proj.get('thumbnail'))
        data['projects'] = [p for p in data['projects'] if p['id'] != pid]
        save_data(data)
        flash('Proyecto eliminado.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    data = load_data()
    if request.method == 'POST':
        data['profile']['name']      = request.form.get('name', '').strip()
        data['profile']['title']     = request.form.get('title', '').strip()
        data['profile']['bio']       = request.form.get('bio', '').strip()
        data['profile']['location']  = request.form.get('location', '').strip()
        data['profile']['email']     = request.form.get('email', '').strip()
        data['profile']['skills']    = [s.strip() for s in request.form.get('skills', '').split(',') if s.strip()]
        data['profile']['interests'] = [i.strip() for i in request.form.get('interests', '').split(',') if i.strip()]
        data['profile']['tools']     = [t.strip() for t in request.form.get('tools', '').split(',') if t.strip()]

        new_avatar = _save_upload('avatar')
        if new_avatar:
            _delete_upload(data['profile'].get('avatar'))
            data['profile']['avatar'] = new_avatar

        save_data(data)
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('profile_form.html', profile=data['profile'])

@app.errorhandler(404)
def not_found(e):
    data = load_data()
    return render_template('404.html', profile=data['profile']), 404

@app.errorhandler(413)
def too_large(e):
    flash('Archivo demasiado grande. Máximo 500 MB.', 'error')
    return redirect(request.referrer or url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
