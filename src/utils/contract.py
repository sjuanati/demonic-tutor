"""
todo:
    - logs showing the following for each conversion (example):
        - function signature: 'Transfer(address,address,uint256)'
        - function hash (eip-712): 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
        - filters: {'fromBlock': 18465740, 'toBlock': 'latest', 'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'topics': ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', '0x000000000000000000000000204d9DE758217A39149767731a87Bcc32427b6ef', None]}
        - # records: X
"""

import re


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

        print("clean_sig", clean_signature)

        eip_712_signature = self.w3.keccak(text=clean_signature).hex()
        print("eip_712_signature", eip_712_signature)

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
                arg_type, arg_name = arg.split()

            parsed_args.append((arg_type, arg_name, indexed))

        return parsed_args

    @staticmethod
    def parse_txn_data(log):
        return {
            "txn_hash": log["transactionHash"].hex(),
            "block_num": log["blockNumber"],
        }

    def parse_indexed_args(self, log, parsed_args, indexed_args_positions, config):
        event_data = {}
        for idx, pos in enumerate(indexed_args_positions):
            arg_type, arg_name, _ = parsed_args[pos]
            value = log["topics"][idx + 1].hex()

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

    def parse_non_indexed_args(
        self, log, parsed_args, non_indexed_args_positions, config
    ):
        event_data = {}
        data_offset = 0
        for _, pos in enumerate(non_indexed_args_positions):
            arg_type, arg_name, _ = parsed_args[pos]
            raw_data = log["data"][data_offset : data_offset + 32]

            decoded_data = self.w3.eth.codec.decode([arg_type], raw_data)[0]

            if arg_type == "uint256":
                multiplier = 10 ** config["decimals"].get(arg_name, 0)
                decoded_data = decoded_data / multiplier

            elif arg_type == "address":
                decoded_data = self.addr_utils.clean_address(decoded_data)

            elif arg_type == "bool":
                decoded_data = self.parse_bool(decoded_data)

            event_data[arg_name] = decoded_data
            data_offset += 32
        return event_data

    @staticmethod
    def parse_bool(hex_value: str) -> bool:
        return hex_value[-1] == "1"
