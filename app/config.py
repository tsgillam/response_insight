import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    JSON_FOLDER = os.path.join(os.getcwd(), "json_data")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
