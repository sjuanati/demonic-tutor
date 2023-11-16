import os
import json

from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
from utils.context import Context
from utils.block import BlockUtils
from utils.logger import setup_logger
from exporters.event import EventExporter
from exporters.call import CallExporter
from web3.exceptions import ABIFunctionNotFound
from constants import NETWORKS, DEFAULT_CALL_FILE, DEFAULT_EVENT_FILE
from utils.exceptions import (
    FileUtilsError,
    ParserCallError,
    BlockUtilsError,
    FilterEventError,
)

load_dotenv()
logger = setup_logger(__name__)


class DemonicTutor:
    def __init__(self, network):
        self.network = network
        self.set_network(network)

    def set_network(self, network: str):
        provider_url = os.getenv(f"PROVIDER_{network}")
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        # To properly interpret the PoA-specific block structure: (e.g.: Polygon network)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.network = network
        if not self.w3.is_connected():
            try:
                # Try some dummy operation to trigger an exception
                # @TODO: careful, if unauthorized for url, gives the full url incl. key
                self.w3.eth.block_number
            except Exception as e:
                raise ConnectionError(
                    f"Initial connection to node provider failed. Reason: {str(e)}"
                )
            else:
                raise ConnectionError("Initial connection to node provider failed.")

    def change_network(self):
        num_networks = len(NETWORKS) - 1
        print("Available networks:")
        for i, network in enumerate(NETWORKS.values()):
            print(f"   {i} -> {network}")
        try:
            index_option = int(input(f"Choose between 0 and {num_networks}: "))
            if 0 <= index_option <= num_networks:
                network = list(NETWORKS.values())[index_option]
                self.set_network(network)
            else:
                input("Wrong option selected -> network not changed\n")
        except ValueError:
            """back to main menu"""

    def get_block_number_by_timestamp(self):
        try:
            timestamp = int(input("Enter a unix timestamp: "))
            block = BlockUtils(
                self.w3, self.network
            ).get_closest_block_number_by_timestamp(timestamp)
            print(f"block: {block}")
        except ValueError as e:
            logger.error(e)
        except BlockUtilsError:
            """handled in class utils.block"""

    def get_block_number_by_date(self):
        # eg: 20221010 10:10:10
        try:
            date_input = input("Enter the date in format 'YYYYMMDD HH:MM:SS': ")
            block = BlockUtils(self.w3, self.network).get_closest_block_number_by_date(
                date_input
            )
            print(f"eth block: {block}")
        except BlockUtilsError:
            """handled in class utils.block"""

    def export_log_data(self, model: str = "", context: str = Context.MAIN.INPUT):
        # eg: gro-gtranche_withdrawal.json
        try:
            if not model:
                user_input = input("Enter the model for log extraction (src/models): ")
                model = user_input if user_input else DEFAULT_EVENT_FILE
            ev_exporter = EventExporter(self.w3, model, context)
            events = ev_exporter.extract_data()
            # print(events) # to add new tests
            return events
        except FileUtilsError:
            """handled in utils.file"""
        except FilterEventError:
            """handled in filters.event"""

    def export_call_data(self, model: str = "", context: str = Context.MAIN.INPUT):
        try:
            # TODO: exceptions
            if not model:
                user_input = input("Enter the model for contract call (src/models): ")
                model = user_input if user_input else DEFAULT_CALL_FILE
            call_exporter = CallExporter(self.w3, model, context)
            data = call_exporter.extract_data()
            if data is not None:
                data_json = json.dumps(data, indent=4)
                if context == Context.MAIN.INPUT:
                    print(data_json)
                return data_json
        except FileUtilsError:
            """handled in utils.file"""
        except (ABIFunctionNotFound, ParserCallError):
            """handled in callers.call"""
