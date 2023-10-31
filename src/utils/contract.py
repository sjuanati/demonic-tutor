import re


class ContractUtils:
    def __init__(self, w3_instance):
        self.w3 = w3_instance

    def parse_function_signature(self, signature: str) -> str:
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
