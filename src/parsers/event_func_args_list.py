import re

from utils.context import Context
from utils.logger import setup_logger
from utils.exceptions import ParserEventError

logger = setup_logger(__name__)


class EventFuncArgsList:
    def __init__(self, w3_instance, context):
        self.w3 = w3_instance
        self.context = context
        self.num_indexed_args = 0

    def get_function_args_list(self, signature: str):
        """
        Entry point to parse the arguments from a signature into tuples:
        - Tuple structure: (field_type, field_name, indexed)
        - Tuple example: ('address', 'sender', True)
        """
        try:
            arguments = self._extract_arguments(signature)
            parsed_args_list = self._parse_arguments(arguments)
        except re.error as regex_error:
            logger.error(f"Regex error: {regex_error}")
            raise ParserEventError(
                "Error processing the regex for argument extraction."
            )
        except ValueError as val_error:
            logger.error(f"Value error: {val_error}")
            raise ParserEventError("Error in the format of the provided arguments.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ParserEventError("An unexpected error occurred during parsing.")

        if self.context == Context.MAIN.INPUT:
            logger.info(f"parsed args: {parsed_args_list}")

        return parsed_args_list

    def _extract_arguments(self, signature: str) -> list:
        """Extracts and returns the argument section from a function signature."""
        # Extract the arguments section using regex
        argument_section = re.search(r"\((.*)\)", signature).group(1)

        # Split the arguments by comma
        arguments = [arg.strip() for arg in argument_section.split(",")]

        return arguments

    def _parse_arguments(self, arguments: list) -> list:
        """Processes a list of arguments and categorizes them into tuples."""
        parsed_args = []
        for arg in arguments:
            if "index_topic_" in arg:
                parsed_arg = self._parse_indexed_argument(arg)
            elif "indexed" in arg:
                parsed_arg = self._parse_flagged_indexed_argument(arg)
            else:
                parsed_arg = self._parse_non_indexed_argument(arg)
            parsed_args.append(parsed_arg)
        return parsed_args

    def _parse_indexed_argument(self, arg: str) -> tuple:
        """Parses arguments with 'index_topic_' format."""
        _, arg_type, arg_name = arg.split()
        self.num_indexed_args += 1
        return arg_type, arg_name, True

    def _parse_flagged_indexed_argument(self, arg: str) -> tuple:
        """Parses arguments with the 'indexed' keyword."""
        parts = arg.split()
        arg_type = parts[0]
        arg_name = parts[-1]
        self.num_indexed_args += 1
        return arg_type, arg_name, True

    def _parse_non_indexed_argument(self, arg: str) -> tuple:
        """Parses non-indexed arguments, handling normal and array types."""
        if "[" in arg and "]" in arg:
            arg_type = re.match(r"(.+)\s", arg).group(1)
            arg_name = re.search(r"\]\s(.+)", arg).group(1)
        else:
            arg_type, arg_name = arg.split()
        return arg_type, arg_name, False
