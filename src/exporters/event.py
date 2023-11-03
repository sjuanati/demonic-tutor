import json

from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from utils.address import AddressUtils
from parsers.event import EventParser
from filters.event import build_filter_params

logger = setup_logger(__name__)


class EventExporter:
    def __init__(self, w3_instance, model: str, context: str = Context.MAIN.INPUT):
        self.w3 = w3_instance
        self.model = model
        self.context = context
        self.addr_utils = AddressUtils(self.w3)
        self.ev_parser = EventParser(self.w3, self.addr_utils, context)
        self.config = FileUtils.read_file(model, context)

    def extract_data(self):
        events = []
        num_records = 0
        function_sig = self.ev_parser.parse_function_sig(self.config["function_sig"])
        parsed_args = self.ev_parser.parse_function_args(self.config["function_sig"])

        # filter_params = self._build_filter_params(function_sig, parsed_args)
        filter_params = build_filter_params(
            self.config, function_sig, parsed_args, self.w3, self.context
        )

        logs = self.w3.eth.get_logs(filter_params)

        for log in logs:
            # Extract transaction data
            txn_data = self.ev_parser.parse_txn_data(log)

            # Extract indexed arguments
            indexed_data = self.ev_parser.parse_indexed_args(
                log, parsed_args, self.config
            )

            # Extract and decode non-indexed arguments
            non_indexed_data = self.ev_parser.parse_non_indexed_args(
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
