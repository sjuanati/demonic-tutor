import re

from utils.logger import setup_logger
from utils.address import AddressUtils
from utils.exceptions import ParserCallError

logger = setup_logger(__name__)


class CallArgsParser:
    def __init__(self, w3_instance):
        self.w3 = w3_instance
        self.addr_utils = AddressUtils(self.w3)

    def parse_args(self, args, arg_types):
        """
        Parses and validates a list of arguments based on their expected types.
        """
        self._check_args(args, arg_types)
        arg_values = list(args.values())
        arg_types_list = list(arg_types.values())
        parsed_args = [
            self._parse_argument(arg_values[i], arg_types_list[i])
            for i in range(len(arg_values))
        ]
        return parsed_args

    def _parse_argument(self, arg: str, arg_type: str):
        """
        Processes and converts a single argument to its correct Ethereum
        arg_type representation.
        """
        # Bool type
        if arg_type == "bool":
            if isinstance(arg, bool):
                return arg
            else:
                error_msg = f"arg: {arg} is not a boolean type (True or False)"
                self._raise_exception("_parse_argument", error_msg)
        elif arg_type.startswith("uint") or arg_type.startswith("int"):
            return arg
        # Address type
        elif arg_type == "address":
            return self.addr_utils.addr_checksum(arg)
        # Bytes or String types
        elif arg_type.startswith("bytes") or arg_type == "string":
            if not arg.startswith("0x"):
                arg = "0x" + arg
            self._is_valid_bytes32(arg)
            return arg
        # Type not found
        else:
            error_msg = f"No matching type: {arg_type}"
            self._raise_exception("_parse_argument", error_msg)

    def _check_args(self, args, arg_types):
        """
        Ensures the arguments list and types list are of equal length.
        """
        if len(args) != len(arg_types):
            error_msg = f"Num. of arguments != Num. of types in model"
            self._raise_exception("_check_args", error_msg)

    def _is_valid_bytes32(self, value):
        """
        Validates a string to check if it's a properly formatted bytes32 hexadecimal.
        """
        if not re.match(r"^0x[a-fA-F0-9]{64}$", value):
            error_msg = f"`{value}` is not a valid bytes32 type"
            self._raise_exception("_parse_argument", error_msg)

    @staticmethod
    def _raise_exception(func: str, error_msg: str):
        """
        Logs an error message and raises a ParserCallError with the message.
        """
        err = f"{func}(): {error_msg}"
        logger.error(err)
        raise ParserCallError(err)
