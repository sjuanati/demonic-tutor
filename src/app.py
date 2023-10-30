import os

from web3 import Web3
from dotenv import load_dotenv
from extractors.transactions import TransactionExtractor

load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")


class DemonicTutor:
    def __init__(self, provider_url):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        assert self.w3.is_connected(), "Not connected to Ethereum node."

        # Initialize the extractor with the web3 instance
        self.tx_extractor = TransactionExtractor(self.w3)

    # A bit useless, at gives a bunch of tx data, but relevant info is
    # within the events
    def get_all_transactions(self, contract_address, start_block=0, end_block="latest"):
        return self.tx_extractor.get_all_transactions(
            contract_address, start_block, end_block
        )

    def get_erc20_transfers(
        self,
        contract_addr,
        start_block=0,
        end_block="latest",
        from_addr=None,
        to_addr=None,
    ):
        return self.tx_extractor.get_erc20_transfers(
            contract_addr, start_block, end_block, from_addr, to_addr
        )


if __name__ == "__main__":
    dt = DemonicTutor(INFURA_URL)
    # txns = dt.get_all_transactions(
    #     contract_address="0x204d9de758217a39149767731a87bcc32427b6ef",
    #     start_block=18447447,  # 18228314,
    #     end_block="latest",
    # )

    # todo: send 1e6 or 1e18
    txns = dt.get_erc20_transfers(
        contract_addr="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        start_block=18447447,  # 18228314,
        end_block="latest",
        from_addr="0x204d9DE758217A39149767731a87Bcc32427b6ef",  # redemption contract
        to_addr=None,
    )
    print(txns)
