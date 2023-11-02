import json

from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from utils.address import AddressUtils
from utils.contract import ContractUtils

logger = setup_logger(__name__)


class EventsExtractor:
    def __init__(self, w3_instance, model: str, context: str = Context.MAIN.INPUT):
        self.w3 = w3_instance
        self.model = model
        self.context = context
        self.addr_utils = AddressUtils(self.w3)
        self.contract_utils = ContractUtils(self.w3, self.addr_utils, context)
        self.config = FileUtils.read_file(model, context)

    def _build_filter_params(self, function_sig, parsed_args):
        topics = [function_sig]
        for arg_type, arg_name, indexed in parsed_args:
            if indexed:
                filter_value = self.config["filters"].get(arg_name)
                if filter_value is not None:
                    if arg_type == "address":
                        filter_value = self.addr_utils.addr_to_hex(filter_value)
                    # TODO: test filtering by integer
                    elif arg_type.startswith("uint"):
                        filter_value = hex(filter_value)
                    elif isinstance(filter_value, bool):
                        filter_value = "0x{:064x}".format(int(filter_value))
                    # TODO: Add more type conversions if necessary
                    topics.append(filter_value)
                else:
                    topics.append(None)

        filter_params = {
            "fromBlock": self.config["start_block"],
            "toBlock": self.config["end_block"],
            "address": self.addr_utils.addr_checksum(self.config["contract_addr"]),
            "topics": topics,
        }

        if self.context == Context.MAIN.INPUT:
            logger.info(f"filter: {filter_params}")

        return filter_params

    def get_data(self):
        events = []
        num_records = 0
        function_sig = self.contract_utils.parse_function_sig(
            self.config["function_sig"]
        )
        parsed_args = self.contract_utils.parse_function_args(
            self.config["function_sig"]
        )

        filter_params = self._build_filter_params(function_sig, parsed_args)

        logs = self.w3.eth.get_logs(filter_params)

        for log in logs:
            # Extract transaction data
            txn_data = self.contract_utils.parse_txn_data(log)

            # Extract indexed arguments
            indexed_data = self.contract_utils.parse_indexed_args(
                log, parsed_args, self.config
            )

            # Extract and decode non-indexed arguments
            non_indexed_data = self.contract_utils.parse_non_indexed_args(
                log, parsed_args, self.config
            )

            # merge data to build the complete item
            events.append({**txn_data, **indexed_data, **non_indexed_data})

            num_records += 1

        # dump data into file
        if self.context == Context.MAIN.INPUT:
            logger.info(f"# records: {num_records}")
            FileUtils().json_to_csv(events, self.model, Context.MAIN.OUTPUT)

        return json.dumps(events, indent=4)


"""
Tests:
    - ev without indexed fields
    - ev with all fields indexed
    - ev with randomly indexed fields (not ordered)
    - ev with struct or custom arrays
    - ev without any data
    - ev with dynamic types in data part (string or bytes) -> now fixed-length (32 bytes) arguments
    - multiple ev with same name but diff parameters
"""
