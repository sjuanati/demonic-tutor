import os

from web3 import Web3
from dotenv import load_dotenv
from utils.logger import setup_logger
from extractors.events import EventsExtractor
from utils.exceptions import (
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
            raise ConnectionError("Initial connection to Ethereum node failed.")

    def get_data(self, model: str, context: str = "main_input"):
        self.ev_extractor = EventsExtractor(self.w3, model, context)
        return self.ev_extractor.get_data()


if __name__ == "__main__":
    try:
        # TODO: should be async?
        dt = DemonicTutor(INFURA_URL)
        # data = dt.get_data("gro-redemption_claim_usdc-transfers.json")
        # data = dt.get_data("gro-teamvesting_claim_gro.json")
        # data = dt.get_data("gro-gtranche_newtranchebalance.json")  # Arrays
        # data = dt.get_data("gro-gtranche_withdrawal.json")  # Filter by bool
        # data = dt.get_data("gro-withdrawhandler-usdc.json")  # Filter by bool
        # data = dt.get_data("uniswap-pool_swap.json")  # Negative int
        data = dt.get_data("balancer-pool_changed.json")  # Negative int
        print(data)

    except ConnectionError as ce:
        print(f"Connection error: {ce}")
    except InvalidConfigurationError as ice:
        logger.error(f"Configuration error: {ice}")
    except DataExtractionError as dee:
        logger.error(f"Data extraction error: {dee}")
    except FilterCreationError as fce:
        logger.error(f"Filter creation error: {fce}")
    except FileNotFoundError as fnf:
        """already captured in class FileUtils()"""
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


"""
    def get_erc20_transfers(
        self,
        contract_addr,
        start_block=0,
        end_block="latest",
        from_addr=None,
        to_addr=None,
    ):
        return self.ev_extractor.get_erc20_transfers(
            contract_addr, start_block, end_block, from_addr, to_addr
        )

    # txns = dt.get_all_transactions(
    #     contract_address="0x204d9de758217a39149767731a87bcc32427b6ef",
    #     start_block=18447447,  # 18228314,
    #     end_block="latest",
    # )

    # A bit useless, at gives a bunch of tx data, but relevant info is
    # within the events
    def get_all_transactions(self, contract_address, start_block=0, end_block="latest"):
        return self.tx_extractor.get_all_transactions(
            contract_address, start_block, end_block
        )
"""
