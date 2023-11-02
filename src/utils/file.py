"""
todo:
    - extract outputs to csv files
"""

import os
import json
from typing import Dict


class FileUtils:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_main_dir = os.path.join(current_dir, "..", "models")
    input_test_dir = os.path.join(current_dir, "..", "tests/data/input")
    output_test_dir = os.path.join(current_dir, "..", "tests/data/output")

    @staticmethod
    def read_file(file_name: str, context: str):
        # Directory path mapping
        dir_paths = {
            "main": FileUtils.input_main_dir,
            "input_test": FileUtils.input_test_dir,
            "output_test": FileUtils.output_test_dir,
        }

        # Validate the context and retrieve the correct directory path
        if context not in dir_paths:
            raise ValueError(f"Invalid context provided: '{context}'")

        dir_path = dir_paths[context]
        full_path = os.path.join(dir_path, file_name)

        # Read the file and return its content
        try:
            with open(full_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {full_path}")
        except json.JSONDecodeError as error:
            raise json.JSONDecodeError(
                f"File could not be parsed as JSON: {full_path}", error.doc, error.pos
            )
