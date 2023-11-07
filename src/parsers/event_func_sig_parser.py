import re

from utils.context import Context
from utils.logger import setup_logger
from utils.exceptions import ParserEventError

logger = setup_logger(__name__)


class EventFuncSigParser:
    def __init__(self, w3_instance, context):
        self.w3 = w3_instance
        self.context = context

    def parse_function_sig(self, signature: str) -> str:
        try:
            clean_signature = self._clean_signature(signature)
            function_name = self._extract_function_name(clean_signature, signature)
            argument_types = self._extract_argument_types(clean_signature, signature)
            cleaned_signature = f"{function_name}({','.join(argument_types)})"
            return self._convert_to_eip712(cleaned_signature)
        except Exception as e:
            logger.error(e)
            raise ParserEventError()

    @staticmethod
    def _clean_signature(signature: str) -> str:
        # Remove index_topic_N and "indexed" references, then strip whitespaces
        return re.sub(r"(index_topic_\d+|indexed)\s*", "", signature).strip()

    @staticmethod
    def _extract_function_name(clean_signature: str, original_signature: str) -> str:
        # Extract the function name using regex
        match = re.match(r"(\w+)\s?\(", clean_signature)
        if not match:
            raise ValueError(
                f"Function name could not be extracted from the signature: '{original_signature}'"
            )
        return match.group(1)

    @staticmethod
    def _extract_argument_types(clean_signature: str, original_signature: str) -> list:
        # Extract the arguments portion from the signature enclosed in parentheses
        search = re.search(r"\((.*)\)", clean_signature)
        if not search:
            raise ValueError(
                f"Argument section could not be extracted from the signature: '{original_signature}'"
            )
        argument_section = search.group(1)
        arguments = argument_section.split(",")

        # Process each argument from the extracted section to identify their types
        argument_types = []
        for arg in arguments:
            parts = arg.strip().split()
            if len(parts) < 2:
                raise ValueError(
                    f"Argument '{arg}' in signature '{original_signature}' is not in the expected format 'type name'."
                )
            argument_types.append(parts[0])
        return argument_types


    def _convert_to_eip712(self, cleaned_signature: str) -> str:
        # Convert signature to EIP-712
        eip_712_signature = self.w3.keccak(text=cleaned_signature).hex()

        # Log if context is appropriate
        if self.context == Context.MAIN.INPUT:
            logger.info(f"function sig: {cleaned_signature}")
            logger.info(f"function hash: {eip_712_signature}")
        return eip_712_signature
