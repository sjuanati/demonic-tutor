class TransactionExtractor:
    def __init__(self, w3_instance):
        self.w3 = w3_instance

    # todo: either generic class or utils
    def get_checksum_addr(self, addr: str):
        return self.w3.to_checksum_address(addr)

    def get_all_transactions(self, contract_address, start_block=0, end_block="latest"):
        """
        Extract all transactions from a contract.
        """
        # Filter & get all the transactions
        filter_params = {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": self.get_checksum_addr(contract_address),
        }
        return self.w3.eth.get_logs(filter_params)

    def get_erc20_transfers(
        self,
        contract_addr,
        start_block=0,
        end_block="latest",
        from_address=None,
        to_address=None,
    ):
        """
        Extract all ERC20 token transfers from/to a contract.
        """
        transfer_signature = self.w3.keccak(
            text="Transfer(address,address,uint256)"
        ).hex()
        topics = [transfer_signature]

        # If from_address is provided, add it as a topic with padding
        if from_address:
            # padded_address = bytes.fromhex(from_address[2:]).rjust(32, b"\0")
            padded_address = "0x" + "0" * 24 + from_address[2:]
            topics.append(padded_address)
        elif to_address:  # If only to_address is provided, add a None placeholder for from_address
            topics.append(None)

        # If to_address is provided, add it as a topic with padding
        if to_address:
            # padded_address = bytes.fromhex(to_address[2:]).rjust(32, b"\0")
            padded_address = "0x" + "0" * 24 + to_address[2:]
            topics.append(padded_address)

        filter_params = {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": self.get_checksum_addr(contract_addr),
            "topics": topics,
        }
        print('topics:', topics)
        transfers = []
        txns = self.w3.eth.get_logs(filter_params)

        for log in txns:
            txn_hash = log["transactionHash"].hex()
            block_num = log["blockNumber"]
            _from = log["topics"][1].hex()  # Extract the `from` address
            _to = log["topics"][2].hex()  # Extract the `to` address

            # Convert the HexBytes data to integer and adjust for USDC's 1e6 precision
            value = int(log["data"].hex(), 16) / 1e6

            transfers.append(
                {
                    "txn_hash": txn_hash,
                    "block_num": block_num,
                    "from": _from,
                    "to": _to,
                    "value": value,
                }
            )

        return transfers
