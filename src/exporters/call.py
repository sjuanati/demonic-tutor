from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from utils.exceptions import ParserCallError
from parsers.call_args_parser import CallArgsParser
from parsers.call_result_parser import CallResultParser

logger = setup_logger(__name__)


class CallExporter:
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
        self.arg_parser = CallArgsParser(self.w3)
        self.result_parser = CallResultParser(self.w3)

    def extract_data(self):
        try:
            # Get model config
            abi, contract_addr, block = self._get_contract()
            func_name, func_args, arg_types = self._get_function()
            output_decimals = self._get_outout()

            # Retrieve contract
            contract = self.w3.eth.contract(address=contract_addr, abi=abi)

            # Parse function arguments
            parsed_args = self.arg_parser.parse_args(func_args, arg_types)
            if self.context == Context.MAIN.INPUT:
                logger.info(
                    f"Calling `{func_name}({', '.join(map(str, parsed_args))})`"
                )

            # Get data from function contract
            result = contract.functions[func_name](*parsed_args).call(
                block_identifier=block
            )

            # Return parse result from contract call
            return self.result_parser.parse_result(
                func_name, abi, result, output_decimals
            )

        except KeyError as e:
            logger.error(f"extract_data(): Error found on key {e}")
        except ParserCallError:
            """handled in parsers.call_args_parser"""
        except Exception as e:
            logger.error(f"extract_data(): {e}")
            raise ParserCallError(e)

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
