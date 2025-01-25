#!/usr/bin/env python3
import os
import json
import csv
from flask import Flask, render_template, send_from_directory, jsonify, request
from pyngrok import ngrok

app = Flask(__name__)

ANNOTATIONS_DIR = "annotations"
os.makedirs(ANNOTATIONS_DIR, exist_ok=True)

# Updated user-to-dataset mapping
USER_DATASET_MAP = {
    "hkim": "hkim_notes.csv",
    "chrystina": "chrystina_notes.csv",
    "yuan": "yuan_notes.csv",
    "wjang": "wjang_notes.csv"
}

# Serve the main annotation HTML file
@app.route("/")
def index():
    return render_template("index.html")

def parse_questionnaire(questionnaire_field):
    """Parse the Questionnaire field into a list of questions with options."""
    questions = []
    if questionnaire_field:
        for question_block in questionnaire_field.split("|"):
            question_data = question_block.strip().split("\n")
            if len(question_data) > 1:
                question = question_data[0].strip()
                options = [opt.strip() for opt in question_data[1:] if opt.strip()]
                questions.append({"question": question, "options": options})
    return questions

def load_dataset(filename):
    """Load dataset from the CSV file."""
    dataset = []
    file_path = os.path.join("static", filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dataset.append({
                    "noteid": row.get("noteid",""),
                    "text": row.get("text", ""),
                    "questions": row.get("questions", "")
                })
    return dataset

@app.route("/get-data", methods=["GET"])
def get_data():
    """Send the dataset to the frontend."""
    username = request.args.get("username")
    if not username or username not in USER_DATASET_MAP:
        return jsonify({"error": "Invalid username or dataset not found"}), 400
    
    dataset_filename = USER_DATASET_MAP[username]
    dataset = load_dataset(dataset_filename)
    return jsonify(dataset)

@app.route("/save-annotations", methods=["POST"])
def save_annotations():
    """Save annotations for a specific user."""
    data = request.json
    username = data["username"]
    annotations = data["annotations"]

    # Save annotations to a JSON file
    file_path = os.path.join(ANNOTATIONS_DIR, f"{username}.json")
    with open(file_path, "w") as file:
        json.dump(annotations, file)

    return jsonify({"message": "Annotations saved successfully!"})

@app.route("/load-annotations", methods=["GET"])
def load_annotations():
    """Load saved annotations for a specific user."""
    username = request.args.get("username")
    file_path = os.path.join(ANNOTATIONS_DIR, f"{username}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            annotations = json.load(file)
        return jsonify(annotations)
    else:
        return jsonify([])  # Return an empty list if no annotations exist

# Serve the CSV file (or any other static files)
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    # Start ngrok tunnel
    public_url = ngrok.connect(8000).public_url
    print(f"ngrok tunnel available at: {public_url}")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=8000)
