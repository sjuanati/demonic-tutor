import json

from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from filters.event import build_filter_params
from parsers.event_func_sig_parser import EventFuncSigParser
from parsers.event_func_args_list import EventFuncArgsList
from parsers.event_func_args_parser import EventFuncArgsParser
from utils.exceptions import FilterEventError, ParserEventError

logger = setup_logger(__name__)

""" @TODO
    According to web3py docs, w3.eth.get_logs() should raise a `Web3Exception`,
    but it's not the case -> it's raising `ValueError` when too many records.
    => Try with other ethereum node providers
"""


class EventExporter:
    def __init__(self, w3_instance, model: str, context: str = Context.MAIN.INPUT):
        self.model = model
        self.w3 = w3_instance
        self.context = context
        self.config = FileUtils.read_file(model, context)
        self.ev_func_sig_parser = EventFuncSigParser(self.w3, context)
        self.ev_func_args_list = EventFuncArgsList(self.w3, context)
        self.ev_func_args_parser = EventFuncArgsParser(self.w3, context)

    def extract_data(self):
        """Parses and exports event logs, and converts the results to a CSV format"""
        events = []
        num_records = 0

        try:
            # Retrieve EIP-712 function signature
            function_sig = self.ev_func_sig_parser.parse_function_sig(
                self.config["function_sig"]
            )

            # Retrieve function arguments to be processed
            parsed_args_list = self.ev_func_args_list.get_function_args_list(
                self.config["function_sig"]
            )

            # Build filter parameters based on indexed args
            filter_params = build_filter_params(
                self.config,
                function_sig,
                parsed_args_list,
                self.w3,
                self.context,
                self.ev_func_args_list.num_indexed_args,
            )

            # Retrieve logs based on the filter parameters
            logs = self.get_logs_in_range(filter_params)

            for log in logs:
                # Extract transaction data
                txn_data = self.ev_func_args_parser.parse_txn_data(log)

                # Extract indexed args
                indexed_data = self.ev_func_args_parser.parse_indexed_args(
                    log, parsed_args_list, self.config
                )

                # Extract and decode non-indexed args
                non_indexed_data = self.ev_func_args_parser.parse_non_indexed_args(
                    log, parsed_args_list, self.config
                )

                # merge data to build the complete item
                events.append({**txn_data, **indexed_data, **non_indexed_data})

                num_records += 1

            # dump data into csv file
            if self.context == Context.MAIN.INPUT:
                logger.info(f"# records: {num_records}")
                FileUtils().json_to_csv(events, self.model, Context.MAIN.OUTPUT)

            return json.dumps(events, indent=4)
        
        except FilterEventError:
            """handled in function build_filter_params()"""
        except ParserEventError:
            """handled in classes EventFunc*"""
        except Exception as e:
            logger.error(f"extract_data(): {e}")

    # iterative (non-recursive) binary-search approach
    def get_logs_in_range(self, params):
        """Fetches logs in the provided block range, handling possible errors"""
        logs = []
        ranges_to_check = [params]

        while ranges_to_check:
            current_range = ranges_to_check.pop()
            from_block, to_block = current_range["fromBlock"], current_range["toBlock"]
            self._log_event_processing(from_block, to_block, "Reading")

            try:
                logs.extend(self.w3.eth.get_logs(current_range))
                self._log_event_processing(from_block, to_block, "Processed")

            except ValueError as e:
                error_data = str(e)
                if "'code': -32005" in error_data:
                    ranges_to_check.extend(self._split_block_range(current_range))
                else:
                    logger.error(f"An unexpected error occurred: {error_data}")
                    raise e

        return logs

    @staticmethod
    def _split_block_range(filters):
        """Splits the given block range into two equal halves"""
        mid_block = (filters["fromBlock"] + filters["toBlock"]) // 2
        if mid_block == filters["fromBlock"]:
            logger.error(f"Too many results in a single block: {mid_block}")
            return []

        lower, upper = filters.copy(), filters.copy()
        lower["toBlock"] = mid_block
        upper["fromBlock"] = mid_block + 1

        return lower, upper

    def _log_event_processing(self, from_block, to_block, status):
        """Helper function to log event processing status"""
        if self.context == Context.MAIN.INPUT:
            logger.info(f"{status} events from blocks {from_block} to {to_block}")
