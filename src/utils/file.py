import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(current_dir, "..", "models")

class FileUtils:
    def __init__(self):
        pass

    @staticmethod
    def read_model(file_name: str):
        full_path = os.path.join(model_dir, file_name)
        with open(full_path, "r") as f:
            file = json.load(f)
        return file
