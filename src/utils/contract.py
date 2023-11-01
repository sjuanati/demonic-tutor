"""
todo:
    - logs showing the following for each conversion (example):
        - function signature: 'Transfer(address,address,uint256)'
        - function hash (eip-712): 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
        - filters: {'fromBlock': 18465740, 'toBlock': 'latest', 'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'topics': ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', '0x000000000000000000000000204d9DE758217A39149767731a87Bcc32427b6ef', None]}
        - # records: X
"""

"""
In Ethereum, array arguments cannot be indexed in event logs. Only fixed-size data types (e.g., address, uint256, bytes32)
can be indexed. This is due to the way Ethereum handles indexed parameters by creating a Keccak-256 hash of the value,
which is then added to the log topic. Arrays, being dynamic in size, don't fit into this mechanism.
"""

import re

from utils.logger import logger


class ContractUtils:
    def __init__(self, w3_instance, addr_utils):
        self.w3 = w3_instance
        self.addr_utils = addr_utils

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

        logger.info(f"function sig: {clean_signature}")
        logger.info(f"function hash: {eip_712_signature}")

        return eip_712_signature

    @staticmethod
    def parse_function_args(signature: str):
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

        if isinstance(decimals, list):  # Fetch the right decimal if it's an array
            decimals = decimals[index]

        if data_type == "uint256":
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

            if "[" in arg_type:
                base_type = arg_type.split("[")[0]
                length = int(arg_type.split("[")[1].split("]")[0])
                values = []

                for i in range(length):
                    raw_data_segment = log["data"][data_offset : data_offset + 32]
                    values.append(
                        self.decode_and_convert(
                            base_type, raw_data_segment, decimals_value, i
                        )
                    )
                    data_offset += 32

                event_data[arg_name] = values
            else:
                raw_data = log["data"][data_offset : data_offset + 32]
                event_data[arg_name] = self.decode_and_convert(
                    arg_type, raw_data, decimals_value
                )
                data_offset += 32

        return event_data

    @staticmethod
    def parse_bool(hex_value: str) -> bool:
        return hex_value[-1] == "1"
