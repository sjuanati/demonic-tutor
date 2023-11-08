import os

from web3 import Web3
from dotenv import load_dotenv
from utils.context import Context
from utils.block import BlockUtils
from utils.logger import setup_logger
from exporters.event import EventExporter
from utils.exceptions import (
    FileUtilsError,
    BlockUtilsError,
    FilterEventError,
)

load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
logger = setup_logger(__name__)


class DemonicTutor:
    def __init__(self, provider_url):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        if not self.w3.is_connected():
            try:
                # Try some dummy operation to trigger an exception
                # @TODO: careful, if unauthorized for url, gives the full url incl. key
                self.w3.eth.block_number
            except Exception as e:
                raise ConnectionError(
                    f"Initial connection to Ethereum node failed. Reason: {str(e)}"
                )
            else:
                raise ConnectionError("Initial connection to Ethereum node failed.")

    def get_block_number_by_timestamp(self):
        try:
            timestamp = int(input("Enter a unix timestamp: "))
            block = BlockUtils(self.w3).get_closest_block_number_by_timestamp(timestamp)
            print(f"eth block: {block}")
        except ValueError as e:
            logger.error(e)
        except BlockUtilsError:
            """handled in class utils.block"""

    def get_block_number_by_date(self):
        # eg: 20221010 10:10:10
        try:
            date_input = input("Enter the date in format 'YYYYMMDD HH:MM:SS': ")
            block = BlockUtils(self.w3).get_closest_block_number_by_date(date_input)
            print(f"eth block: {block}")
        except BlockUtilsError:
            """handled in class utils.block"""

    def export_log_data(self, model: str = "", context: str = Context.MAIN.INPUT):
        # eg: gro-gtranche_withdrawal.json
        try:
            if not model:
                model = input("Enter the model for log extraction (src/models): ")
            ev_exporter = EventExporter(self.w3, model, context)
            events = ev_exporter.extract_data()
            # print(events) # to add new tests
            return events
        except FileUtilsError:
            """handled in utils.file"""
        except FilterEventError:
            """handled in filters.event"""
