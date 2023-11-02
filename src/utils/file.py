import os
import json
import pandas as pd

from typing import Dict, Any
from utils.logger import setup_logger
from utils.context import Context

logger = setup_logger(__name__)


class FileUtils:
    @staticmethod
    def read_file(file_name: str, context: str) -> Dict[str, Any]:
        full_path = os.path.join(context, file_name)

        # Reads a JSON file based on its name and context
        try:
            with open(full_path, "r") as f:
                return json.load(f)
        except FileNotFoundError as err:
            logger.error(
                f"File '{file_name}' not found in context '{context}'" f" -> {err}"
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
        full_path = os.path.join(context, file_name)
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
