from flask import Flask, render_template, send_from_directory, send_file, abort, redirect, url_for, request, jsonify
import os
from flask import session


app = Flask(__name__)
app.secret_key = 'hardikfileexplorer_1a8d3f90e0b74e22b6f9d87ac4fcd134'

# Actual SSD path
FILE_ROOT = "/Volumes/samba/usb1_1_1"  # <-- Update this to your mount path

# Allowed file extensions
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
PDF_EXTENSION = '.pdf'
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

# Folders to hide
HIDDEN_FOLDERS = {'server', 'System Volume Information', '$RECYCLE.BIN', 'server2'}

#For DropX
UPLOAD_FOLDER = 'dropx_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def root():
    default_tab = session.get('default_tab', 'files')

    if default_tab == 'videos':
        return redirect(url_for('all_videos'))
    elif default_tab == 'images':
        return redirect(url_for('all_images'))
    elif default_tab == 'pdfs':
        return redirect(url_for('all_pdfs'))
    elif default_tab == 'dropx':
        return redirect(url_for('dropx'))
    else:
        return redirect(url_for('browse', subpath=''))

@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    full_path = os.path.join(FILE_ROOT, subpath)

    if not os.path.exists(full_path):
        return abort(404)

    try:
        entries = os.listdir(full_path)
    except PermissionError:
        return "Access denied to this folder."

    folders = [e for e in entries 
               if os.path.isdir(os.path.join(full_path, e)) 
               and not e.startswith('.') 
               and e not in HIDDEN_FOLDERS]

    videos = [e for e in entries 
              if e.lower().endswith(VIDEO_EXTENSIONS) 
              and not e.startswith('.')]

    pdfs = [e for e in entries 
            if e.lower().endswith(PDF_EXTENSION) 
            and not e.startswith('.')]

    # ✅ Only show other_files if enabled in session
    other_files = []
    if session.get('show_other_files', False):
        other_files = [e for e in entries 
                       if os.path.isfile(os.path.join(full_path, e)) 
                       and not e.lower().endswith(VIDEO_EXTENSIONS) 
                       and not e.lower().endswith(PDF_EXTENSION) 
                       and not e.startswith('.')]

    return render_template("index.html", 
                           folders=folders, 
                           videos=videos, 
                           pdfs=pdfs, 
                           other_files=other_files, 
                           subpath=subpath)

@app.route('/video/<path:filepath>')
def stream_video(filepath):
    dir_path = os.path.join(FILE_ROOT, os.path.dirname(filepath))
    filename = os.path.basename(filepath)
    return send_from_directory(dir_path, filename)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/play/<path:filepath>')
def play_video(filepath):
    return render_template("player.html", filepath=filepath)

@app.route('/viewpdf')
def view_pdf():
    pdf_path = request.args.get('pdf')
    return render_template('pdfviewer.html', pdf_path=pdf_path)
def get_all_pdfs(base_dir):
    pdf_list = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith('.'):
                continue
            if file.lower().endswith(PDF_EXTENSION):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                mtime = os.path.getmtime(full_path)
                pdf_list.append((rel_path.replace("\\", "/"), mtime))
    return sorted(pdf_list, key=lambda x: x[1], reverse=True)
@app.route('/all_pdfs')
def all_pdfs():
    base_dir = FILE_ROOT  # adjust as needed  #GoldernHaze
    pdfs = get_all_pdfs(base_dir)
    return render_template("pdfs.html", pdfs=[p[0] for p in pdfs])

@app.route('/file/<path:path>')
def serve_file(path):
    full_path = os.path.join(FILE_ROOT, path)
    if os.path.isfile(full_path):
        return send_file(full_path)
    else:
        return "File not found", 404
def get_all_videos(base_dir):
    video_list = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith("._"):  # ⛔ Skip macOS metadata files
                continue
            if file.lower().endswith(VIDEO_EXTENSIONS):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                mtime = os.path.getmtime(full_path)
                video_list.append((rel_path.replace("\\", "/"), mtime))
    # Sort by modified time (descending)
    return sorted(video_list, key=lambda x: x[1], reverse=True)

@app.route('/all_videos')
def all_videos():
    base_dir = FILE_ROOT  # <-- change this if needed #GoldernHaze
    videos = get_all_videos(base_dir)
    return render_template("videos.html", videos=[v[0] for v in videos])

def get_all_images(base_dir):
    image_list = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith("._") or file.startswith("."):
                continue
            if file.lower().endswith(IMAGE_EXTENSIONS):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                mtime = os.path.getmtime(full_path)
                image_list.append((rel_path, mtime))
    return sorted(image_list, key=lambda x: x[1], reverse=True)
@app.route('/all_images')
def all_images():
    base_dir = FILE_ROOT
    images = get_all_images(base_dir)
    return render_template("images.html", images=[img[0] for img in images])




@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    content_type = request.args.get("type", "files")

    base_dir = FILE_ROOT

    matched = []

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith("._"):
                continue  # skip dot files
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
            if query in file.lower():
                if content_type == "videos" and file.lower().endswith(VIDEO_EXTENSIONS):
                    matched.append(rel_path)
                elif content_type == "pdfs" and file.lower().endswith(".pdf"):
                    matched.append(rel_path)
                elif content_type == "files":
                    matched.append(rel_path)

    return render_template("search_results.html", query=query, results=matched, tab=content_type)
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Save checkbox setting to session
        show_other_files = request.form.get('show_other_files') == 'on'
        session['show_other_files'] = show_other_files

        # Optional: you can also add more settings here
        default_tab = request.form.get('default_tab', 'files')
        session['default_tab'] = default_tab

        return redirect(url_for('settings'))

    return render_template(
        'settings.html',
        show_other_files=session.get('show_other_files', False),
        default_tab=session.get('default_tab', 'files')
    )

@app.route('/dropx')
def dropx():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    return render_template('dropx.html', files=files, tab='dropx')


@app.route('/upload-dropx', methods=['POST'])
def upload_dropx():
    file = request.files['file']
    name = request.form.get('rename') or file.filename
    file.save(os.path.join(UPLOAD_FOLDER, name))
    return '', 204


@app.route('/list-dropx')
def list_dropx():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(sorted(files, reverse=True))


@app.route('/dropx_storage/<filename>')
def download_dropx_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/delete-dropx/<filename>', methods=['POST'])
def delete_dropx(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return '', 204


@app.route('/delete-dropx-file/<filename>')
def delete_dropx_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return '', 204


@app.route('/delete-all-dropx', methods=['POST'])
def delete_all_dropx():
    for file in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, file))
    return '', 204

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=80,
        #ssl_context=('cert/game.com.pem', 'cert/game.com-key.pem'),
        debug=True
    )
