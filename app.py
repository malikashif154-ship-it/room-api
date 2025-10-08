from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return jsonify({"status": "running", "message": "Upload to /upload"})

@app.route("/upload", methods=["POST"])
def upload_files():
    if "images" not in request.files:
        return jsonify({"error": "No images"}), 400

    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "Empty list"}), 400

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(app.config["UPLOAD_FOLDER"], job_id)
    os.makedirs(job_dir, exist_ok=True)

    saved_files = []
    for file in files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(job_dir, filename)
            file.save(path)
            saved_files.append(path)

    if not saved_files:
        return jsonify({"error": "No valid image files"}), 400

    model_filename = f"{job_id}.glb"
    model_path = os.path.join(app.config["OUTPUT_FOLDER"], model_filename)

    # Dummy GLB file (replace this later)
    with open(model_path, "w") as f:
        f.write("// Dummy GLB file generated")

    model_url = request.host_url + "download/" + model_filename
    return jsonify({"status": "success", "model_url": model_url})

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
