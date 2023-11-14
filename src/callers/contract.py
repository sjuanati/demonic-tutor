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
        try:
            # Get model config
            abi, contract_addr, block = self._get_contract()
            func_name, func_args, arg_types = self._get_function()
            output_decimals = self._get_outout()
            
            # Retrieve contract
            contract = self.w3.eth.contract(address=contract_addr, abi=abi)

            # Parse function arguments
            parsed_args = self.parser.parse_args(func_args, arg_types)
            logger.info(f"Calling `{func_name}({', '.join(map(str, parsed_args))})`")

            # Get data from function contract
            result = contract.functions[func_name](*parsed_args).call(
                block_identifier=block
            )

            # Return parse result from contract call
            return self.parser.parse_result(func_name, abi, result, output_decimals)

        except KeyError as e:
            logger.error(f"get_function_data(): Error found on key {e}")
        except (ABIFunctionNotFound, Web3ValidationError) as e:
            logger.error(f"get_function_data(): {e}")
        except ValueError:
            """handled in parsers.contract_call_args_parser"""
        except Exception as e:
            logger.error(f"get_function_data(): {e}")
            raise e

    def _get_contract(self):
        return (
            self.config["abi"],
            self.config["contract_addr"],
            self.config["block"],
        )

    def _get_function(self):
        return (
            self.config["function_name"],
            self.config["arguments"],
            self.config["arg_types"],
        )

    def _get_outout(self):
        return self.config["output_decimals"]
