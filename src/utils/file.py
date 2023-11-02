import os
import json
import pandas as pd
from typing import Dict, Any
from utils.logger import logger


class FileUtils:
    # Directory paths configuration
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dir_paths = {
        "main_input": os.path.join(current_dir, "..", "models"),
        "main_output": os.path.join(current_dir, "..", "data"),
        "test_input": os.path.join(current_dir, "..", "tests/data/input"),
        "test_output": os.path.join(current_dir, "..", "tests/data/output"),
    }

    @staticmethod
    def _get_full_path(file_name: str, context: str) -> str:
        if context not in FileUtils.dir_paths:
            raise ValueError(f"Invalid context provided: '{context}'")
        dir_path = FileUtils.dir_paths[context]
        return os.path.join(dir_path, file_name)

    @staticmethod
    def read_file(file_name: str, context: str) -> Dict[str, Any]:
        full_path = FileUtils._get_full_path(file_name, context)

        # Reads a JSON file based on its name and context
        try:
            with open(full_path, "r") as f:
                return json.load(f)
        except FileNotFoundError as err:
            logger.error(
                f"File '{file_name}' not found in context '{context}'"
                f" -> {err}"
                )
            raise
        except json.JSONDecodeError as error:
            logger.error(
                f"File '{file_name}' in context '{context}' "
                f"could not be parsed as JSON: {error}"
            )
            raise

    @staticmethod
    def json_to_csv(data, file_name: str, context: str):
        full_path = FileUtils._get_full_path(file_name, context)
        csv_path = os.path.splitext(full_path)[0] + ".csv"

        # Converts a JSON data structure into a CSV file
        try:
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
        except ValueError as error:
            logger.error(
                f"Error while converting data to DataFrame for file "
                f"'{file_name}' in context '{context}': {error}"
            )
            raise
        except Exception as error:
            logger.error(
                f"Unexpected error while processing file '{file_name}' "
                "in context '{context}': {error}"
            )
            raise
