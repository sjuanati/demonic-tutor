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
    def __init__(self, w3_instance):
        self.w3 = w3_instance

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
    def parse_bool(hex_value: str) -> bool:
        return hex_value[-1] == "1"
