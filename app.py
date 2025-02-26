#!/usr/bin/env python3
import os
import json
import csv
from flask import Flask, render_template, send_from_directory, jsonify, request

app = Flask(__name__)

ANNOTATIONS_DIR = "annotations"
DATASET_DIR = "static"
os.makedirs(ANNOTATIONS_DIR, exist_ok=True)

USER_DATASET_MAP = {
    "hkim": "hkim_notes.csv",
    "chrystina": "chrystina_notes.csv",
    "yuan": "yuan_notes.csv",
    "wjang": "wjang_notes.csv"
}

@app.route("/")
def index():
    return render_template("index.html")


def load_dataset(filename):
    dataset = []
    file_path = os.path.join(DATASET_DIR, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    dataset.append({
                        "noteid": row.get("noteid", ""),
                        "text": row.get("text", ""),
                        "questions": row.get("questions", "")
                    })
        except Exception as e:
            print(f"Error loading dataset {filename}: {e}")
    return dataset


@app.route("/get-data", methods=["GET"])
def get_data():
    username = request.args.get("username")
    if not username or username not in USER_DATASET_MAP:
        return jsonify({"error": "Invalid username or dataset not found"}), 400

    dataset_filename = USER_DATASET_MAP[username]
    dataset = load_dataset(dataset_filename)
    if not dataset:
        return jsonify({"error": f"No data found for user {username}"}), 404

    return jsonify(dataset)


@app.route("/save-annotations", methods=["POST"])
def save_annotations():
    data = request.json
    username = data.get("username")
    annotations = data.get("annotations")

    if not username or not annotations:
        return jsonify({"error": "Invalid data provided"}), 400

    file_path = os.path.join(ANNOTATIONS_DIR, f"{username}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(annotations, file, ensure_ascii=False, indent=4)
        return jsonify({"message": f"Annotations for {username} saved successfully!"})
    except Exception as e:
        print(f"Error saving annotations for {username}: {e}")
        return jsonify({"error": "Failed to save annotations"}), 500


@app.route("/load-annotations", methods=["GET"])
def load_annotations():
    username = request.args.get("username")
    if not username or username not in USER_DATASET_MAP:
        return jsonify({"error": "Invalid username"}), 400

    file_path = os.path.join(ANNOTATIONS_DIR, f"{username}.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                annotations = json.load(file)
            return jsonify(annotations)
        else:
            return jsonify([])  # Return an empty list for new users
    except Exception as e:
        print(f"Error loading annotations for {username}: {e}")
        return jsonify({"error": "Failed to load annotations"}), 500


@app.route("/<path:filename>")
def static_files(filename):
    try:
        return send_from_directory(".", filename)
    except Exception as e:
        print(f"Error serving static file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404
        
@app.route("/download-annotations", methods=["GET"])
def download_annotations():
    annotations_zip = "annotations.zip"
    # Create a zip file of the annotations directory
    os.system(f"zip -r {annotations_zip} {ANNOTATIONS_DIR}")
    # Serve the zip file for download
    return send_from_directory(".", annotations_zip, as_attachment=True)

@app.route("/list-annotations", methods=["GET"])
def list_annotations():
    """Returns a list of available annotation files."""
    try:
        files = os.listdir(ANNOTATIONS_DIR)
        return jsonify({"annotation_files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download-annotation/<filename>", methods=["GET"])
def download_annotation(filename):
    """Allows downloading of annotation files."""
    file_path = os.path.join(ANNOTATIONS_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(ANNOTATIONS_DIR, filename, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404
        
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if PORT is not set
    print(f"Starting app on port: {port}")  # Debug line to print the port value
    app.run(host="0.0.0.0", port=port, debug=True)

