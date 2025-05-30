from flask import Flask, render_template, send_from_directory, send_file, abort, redirect, url_for, request
import os

app = Flask(__name__)

# Actual SSD path
FILE_ROOT = "/Volumes/SERVER"  # <-- Update this to your mount path

# Allowed file extensions
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
PDF_EXTENSION = '.pdf'

# Folders to hide
HIDDEN_FOLDERS = {'server', 'System Volume Information', '$RECYCLE.BIN', 'server2'}

@app.route('/')
def root():
    return redirect(url_for('browse', subpath=''))

@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    full_path = os.path.join(FILE_ROOT, subpath)

    if not os.path.exists(full_path):
        return abort(404)

    if os.path.isfile(full_path):
        # Optional: redirect based on file type
        if full_path.lower().endswith(PDF_EXTENSION):
            return redirect(url_for('view_pdf', pdf=subpath))
        elif full_path.lower().endswith(VIDEO_EXTENSIONS):
            return redirect(url_for('play_video', filepath=subpath))
        else:
            return send_file(full_path)

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

    # New: Other files (exclude videos, pdfs, hidden files)
    other_files = [e for e in entries 
                   if os.path.isfile(os.path.join(full_path, e)) 
                   and not e.lower().endswith(VIDEO_EXTENSIONS) 
                   and not e.lower().endswith(PDF_EXTENSION) 
                   and not e.startswith('.')]

    return render_template("index.html", 
                           folders=folders, 
                           videos=videos, 
                           pdfs=pdfs, 
                           other_files=other_files,  # <-- added here
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
