import os

from web3 import Web3
from dotenv import load_dotenv
from utils.context import Context
from utils.logger import setup_logger
from utils.block import BlockUtils
from exporters.event import EventExporter
from utils.exceptions import (
    BlockUtilsError,
    DataExtractionError,
    FilterCreationError,
    InvalidConfigurationError,
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

    def extract_data(self, model: str, context: str = Context.MAIN.INPUT):
        ev_extractor = EventExporter(self.w3, model, context)
        return ev_extractor.extract_data()
    
    def get_block_number_by_timestamp(self, timestamp: int):
        block = BlockUtils(self.w3).get_closest_block_number_by_timestamp(timestamp)
        print('timestamp', block)

    def get_closest_block_number_by_date(self, date: str):
        block = BlockUtils(self.w3).get_closest_block_number_by_date(date)
        print('timestamp', block)



if __name__ == "__main__":
    try:
        # TODO: should be async?
        dt = DemonicTutor(INFURA_URL)
        # data = dt.extract_data("gro-redemption_claim_usdc-transfers.json")
        # data = dt.extract_data("gro-teamvesting_claim_gro.json")
        # data = dt.extract_data("gro-gtranche_newtranchebalance.json")  # Arrays
        # data = dt.extract_data("gro-gtranche_withdrawal.json")  # Filter by bool
        # data = dt.extract_data("gro-withdrawhandler-usdc.json")  # Filter by bool
        # data = dt.extract_data("uniswap-pool_swap.json")  # Negative int
        # data = dt.extract_data("balancer-pool_changed.json")  # Negative int
        # print(data)
        # dt.get_block_number_by_timestamp(1699050588)
        dt.get_closest_block_number_by_date('20231106 06:06:00')

    except ConnectionError as ce:
        print(f"Connection error: {ce}")
    except InvalidConfigurationError as ice:
        logger.error(f"Configuration error: {ice}")
    except DataExtractionError as dee:
        logger.error(f"Data extraction error: {dee}")
    except FilterCreationError as fce:
        logger.error(f"Filter creation error: {fce}")
    except FileNotFoundError:
        """already captured in class FileUtils()"""
    except BlockUtilsError:
        """already captured in class BlockUtils()"""
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

