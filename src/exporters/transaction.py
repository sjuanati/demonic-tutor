
'''
    def get_all_transactions(self, contract_address, start_block=0, end_block="latest"):
        """
        Extract all transactions from a contract.
        """
        # Filter & get all the transactions
        filter_params = {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": self.addr_utils.addr_checksum(contract_address),
        }
        return self.w3.eth.get_logs(filter_params)
'''