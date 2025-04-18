# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)


# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from .routes import main
    app.register_blueprint(main)

    return app


# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    JSON_FOLDER = os.path.join(os.getcwd(), "json_data")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


# app/routes.py
from flask import Blueprint, render_template, request, jsonify
import os
import json
from app.utils.file_handlers import get_json_files, load_json_data
from app.utils.json_parser import extract_metadata

main = Blueprint('main', __name__)

@main.route('/')
def index():
    files = get_json_files()
    metadata = extract_metadata(files)
    return render_template('viewer.html', metadata=metadata)

@main.route('/get_filtered_responses', methods=['POST'])
def get_filtered_responses():
    filters = request.json
    files = get_json_files()
    data = load_json_data(files, filters)
    return jsonify(data)


# app/utils/file_handlers.py
import os
import json
from werkzeug.utils import safe_join  # SECURITY NOTE
from config import Config


def get_json_files():
    json_files = []
    for root, _, files in os.walk(Config.JSON_FOLDER):
        for file in files:
            if file.endswith(".json"):
                json_files.append(safe_join(root, file))
    return json_files


def load_json_data(files, filters):
    matched = []
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                for response in content.get("responses", []):
                    if all(response.get(k) == v for k, v in filters.items() if v):
                        matched.append(response)
        except Exception as e:
            continue  # Skip malformed files
    return matched


# app/utils/json_parser.py
def extract_metadata(files):
    metadata = set()
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                for r in content.get("responses", []):
                    metadata.add((r.get("project"), r.get("step"), r.get("prompt_name")))
        except:
            continue
    return sorted(metadata)