import json

from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from utils.address import AddressUtils
from parsers.event import EventParser
from filters.event import build_filter_params

logger = setup_logger(__name__)

""" @TODO
    According to web3py docs, w3.eth.get_logs() should raise a `Web3Exception`,
    but it's not the case -> it's raising `ValueError` is too many records.
"""


class EventExporter:
    def __init__(self, w3_instance, model: str, context: str = Context.MAIN.INPUT):
        self.w3 = w3_instance
        self.model = model
        self.context = context
        self.addr_utils = AddressUtils(self.w3)
        self.ev_parser = EventParser(self.w3, self.addr_utils, context)
        self.config = FileUtils.read_file(model, context)

    def split_block_range(self, filters):
        mid_block = (filters["fromBlock"] + filters["toBlock"]) // 2
        if mid_block == filters["fromBlock"]:
            logger.error(f"Too many results in a single block: {mid_block}")
            return []

        lower, upper = filters.copy(), filters.copy()
        lower["toBlock"] = mid_block
        upper["fromBlock"] = mid_block + 1

        return lower, upper

    # iterative (instead of recursive) binary-search approach
    def get_logs_in_range(self, params):
        logs = []
        ranges_to_check = [params]

        while ranges_to_check:
            current_range = ranges_to_check.pop()
            from_block, to_block = current_range["fromBlock"], current_range["toBlock"]
            if self.context == Context.MAIN.INPUT:
                logger.info(f"Reading events from blocks {from_block} to {to_block}")

            try:
                logs.extend(self.w3.eth.get_logs(current_range))
                if self.context == Context.MAIN.INPUT:
                    logger.info(
                        f"Processed events from blocks {from_block} to {to_block}"
                    )

            except ValueError as e:
                error_data = str(e)
                if "'code': -32005" in error_data:
                    ranges_to_check.extend(self.split_block_range(current_range))
                else:
                    logger.error(f"An unexpected error occurred: {error_data}")
                    raise e

        return logs

    def extract_data(self):
        events = []
        num_records = 0

        function_sig = self.ev_parser.parse_function_sig(self.config["function_sig"])
        parsed_args = self.ev_parser.parse_function_args(self.config["function_sig"])
        filter_params = build_filter_params(
            self.config, function_sig, parsed_args, self.w3, self.context
        )

        logs = self.get_logs_in_range(filter_params)

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
