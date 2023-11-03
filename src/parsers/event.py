import re

from constants import EVM_WORD_SIZE
from utils.context import Context
from utils.logger import setup_logger


logger = setup_logger(__name__)


class EventParser:
    def __init__(self, w3_instance, addr_utils, context):
        self.w3 = w3_instance
        self.addr_utils = addr_utils
        self.context = context

    def parse_function_sig(self, signature: str) -> str:
        # Remove index_topic_N and "indexed" references, then strip whitespaces
        clean_signature = re.sub(r"(index_topic_\d+|indexed)\s*", "", signature).strip()

        # Extract the function name using regex
        function_name = re.match(r"(\w+)\s?\(", clean_signature).group(1)

        # Extract argument types by splitting the string and removing argument names
        argument_section = re.search(r"\((.*)\)", clean_signature).group(1)
        argument_types = [arg.split()[0] for arg in argument_section.split(",")]

        # Construct and return the cleaned signature
        clean_signature = f"{function_name}({','.join(argument_types)})"

        # Convert signature to EIP-712
        eip_712_signature = self.w3.keccak(text=clean_signature).hex()

        if self.context == Context.MAIN.INPUT:
            logger.info(f"function sig: {clean_signature}")
            logger.info(f"function hash: {eip_712_signature}")

        return eip_712_signature

    def parse_function_args(self, signature: str):
        # Extract the arguments section using regex
        argument_section = re.search(r"\((.*)\)", signature).group(1)

        # Split the arguments by comma
        arguments = [arg.strip() for arg in argument_section.split(",")]

        parsed_args = []
        for arg in arguments:
            # Check if the argument is indexed by searching for "index_topic_N"
            if "index_topic_" in arg:
                indexed = True
                _, arg_type, arg_name = arg.split()
            # Check for the "indexed" keyword for the second format
            elif "indexed" in arg:
                indexed = True
                parts = arg.split()
                arg_type = parts[0]
                arg_name = parts[-1]
            else:
                indexed = False
                # Check for array type
                if "[" in arg and "]" in arg:
                    arg_type = re.match(r"(.+)\s", arg).group(1)
                    arg_name = re.search(r"\]\s(.+)", arg).group(1)
                else:
                    arg_type, arg_name = arg.split()

            parsed_args.append((arg_type, arg_name, indexed))

        if self.context == Context.MAIN.INPUT:
            logger.info(f"parsed args: {parsed_args}")

        return parsed_args

    @staticmethod
    def parse_txn_data(log):
        return {
            "txn_hash": log["transactionHash"].hex(),
            "block_num": log["blockNumber"],
        }

    def parse_indexed_args(self, log, parsed_args, config):
        event_data = {}
        for i, (arg_type, arg_name, _) in enumerate(
            arg for arg in parsed_args if arg[2] is True
        ):
            value = log["topics"][i + 1].hex()

            if arg_type == "address":
                value = self.addr_utils.addr_to_hex(value)
                value = self.addr_utils.clean_address(value)

            elif arg_type == "uint256":
                multiplier = 10 ** config["decimals"].get(arg_name, 0)
                value = int(value, 16) / multiplier

            elif arg_type == "bool":
                value = self.parse_bool(value)

            event_data[arg_name] = value
        return event_data

    # TODO: update name / can be used for indexed args?
    def decode_and_convert(self, data_type, raw_data, decimals, index=0):
        decoded = self.w3.eth.codec.decode([data_type], raw_data)[0]

        # TODO: this might not be required. Assume every dynamic item will have the same decimal
        if isinstance(decimals, list):  # Fetch the right decimal if it's an array
            decimals = decimals[index]

        if data_type.startswith("uint") or data_type.startswith("int"):
            multiplier = 10**decimals
            return decoded / multiplier
        elif data_type == "address":
            return self.addr_utils.clean_address(decoded)
        return decoded

    # TODO: test non-uint arrays
    def parse_non_indexed_args(self, log, parsed_args, config):
        event_data = {}
        data_offset = 0

        for _, (arg_type, arg_name, _) in enumerate(
            arg for arg in parsed_args if arg[2] is False
        ):
            decimals_value = config["decimals"].get(arg_name, 0)

            # dynamic-size array
            if "[]" in arg_type:
                base_type = arg_type.replace("[]", "")

                # Get the position (offset) where the dynamic array starts:
                # - First 32 bytes: lenght of the array (eg: 3)
                # - Following 32 bytes: each element of the array
                raw_data = log["data"][data_offset : data_offset + EVM_WORD_SIZE]
                offset = int.from_bytes(raw_data, byteorder="big")

                # Get the length of the dynamic array and move past the
                # length where the array items start
                raw_data = log["data"][offset : offset + EVM_WORD_SIZE]
                num_items = int.from_bytes(raw_data, byteorder="big")
                offset += EVM_WORD_SIZE

                # Process each array item
                values = []
                for _ in range(num_items):
                    raw_data_segment = log["data"][offset : offset + EVM_WORD_SIZE]
                    values.append(
                        self.decode_and_convert(
                            base_type, raw_data_segment, decimals_value
                        )
                    )
                    offset += EVM_WORD_SIZE

                event_data[arg_name] = values
                data_offset += EVM_WORD_SIZE
            # fixed-size array
            elif "[" in arg_type:
                base_type = arg_type.split("[")[0]
                length = int(arg_type.split("[")[1].split("]")[0])
                values = []

                for i in range(length):
                    raw_data_segment = log["data"][
                        data_offset : data_offset + EVM_WORD_SIZE
                    ]
                    values.append(
                        self.decode_and_convert(
                            base_type, raw_data_segment, decimals_value, i
                        )
                    )
                    data_offset += EVM_WORD_SIZE
                event_data[arg_name] = values
            # other types (address, uint, bool)
            else:
                raw_data = log["data"][data_offset : data_offset + EVM_WORD_SIZE]
                event_data[arg_name] = self.decode_and_convert(
                    arg_type, raw_data, decimals_value
                )
                data_offset += EVM_WORD_SIZE

        return event_data

    @staticmethod
    def parse_bool(hex_value: str) -> bool:
        return hex_value[-1] == "1"
