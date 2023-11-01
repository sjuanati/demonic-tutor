"""
todo:
    - extract outputs to csv files
"""
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(current_dir, "..", "models")
input_test_dir = os.path.join(current_dir, "..", "tests/data/input")
output_test_dir = os.path.join(current_dir, "..", "tests/data/output")

# TODO: refactor to one method
class FileUtils:
    def __init__(self):
        pass

    @staticmethod
    def read_model(file_name: str):
        full_path = os.path.join(model_dir, file_name)
        with open(full_path, "r") as f:
            file = json.load(f)
        return file

    @staticmethod
    def read_input_test(file_name: str):
        full_path = os.path.join(input_test_dir, file_name)
        with open(full_path, "r") as f:
            file = json.load(f)
        return file
    
    @staticmethod
    def read_output_test(file_name: str):
        full_path = os.path.join(output_test_dir, file_name)
        with open(full_path, "r") as f:
            file = json.load(f)
        return file