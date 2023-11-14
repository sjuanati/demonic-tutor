from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from parsers.contract_call_args_parser import ContractCallArgsParser
from web3.exceptions import ABIFunctionNotFound, Web3ValidationError

logger = setup_logger(__name__)


class ContractCaller:
    def __init__(
        self,
        w3_instance,
        model: str,
        context: str = Context.MAIN.INPUT,
    ):
        self.model = model
        self.w3 = w3_instance
        self.context = context
        self.config = FileUtils.read_file(model, context)
        self.parser = ContractCallArgsParser(self.w3, context)

    def get_function_data(self):
        # TODO: build a list with (arg_names, arg_types), similarly to event lists
        try:
            abi = self.config["abi"]
            contract_addr = self.config["contract_addr"]
            contract = self.w3.eth.contract(address=contract_addr, abi=abi)
            function_name = self.config["function_name"]
            args = self.config["arguments"]
            types = self.config["types"]
            block_number = self.config["block"]
            contract = self.w3.eth.contract(address=contract_addr, abi=abi)
            parsed_args = self.parser.parse_args(args, types)
            logger.info(
                f"Calling `{function_name}({', '.join(map(str, parsed_args))})`"
            )
            result = contract.functions[function_name](*parsed_args).call(
                block_identifier=block_number
            )
            return result
        except (ABIFunctionNotFound, Web3ValidationError) as e:
            print(f"get_function_data(): {e}")
        except ValueError:
            """handled in parsers.contract_call_args_parser"""
        except Exception as e:
            # TODO
            raise e
