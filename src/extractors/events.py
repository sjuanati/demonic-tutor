import json

from utils.file import FileUtils
from utils.address import AddressUtils
from utils.contract import ContractUtils


class EventsExtractor:
    def __init__(self, w3_instance, model: str):
        self.w3 = w3_instance
        self.addr_utils = AddressUtils(self.w3)
        self.contract_utils = ContractUtils(self.w3)
        self.config = FileUtils.read_model(model)


    def get_data(self):
        function_sig = self.contract_utils.parse_function_sig(self.config["function_sig"])
        parsed_args = self.contract_utils.parse_function_args(self.config["function_sig"])

        topics = [function_sig]

        for arg_type, arg_name, indexed in parsed_args:
            if indexed:
                # topics.append(self.addr_utils.addr_to_hex(self.config["filters"].get(arg_name, None)))
                filter_value = self.config["filters"].get(arg_name)
                if filter_value:
                    topics.append(self.addr_utils.addr_to_hex(filter_value))

        filter_params = {
            "fromBlock": self.config["start_block"],
            "toBlock": self.config["end_block"],
            "address": self.addr_utils.addr_checksum(self.config["contract_addr"]),
            "topics": topics,
        }
        print("filter_params", filter_params)
        events = []

        txns = self.w3.eth.get_logs(filter_params)

        indexed_args_positions = [idx for idx, (_, _, indexed) in enumerate(parsed_args) if indexed]
        non_indexed_args_positions = [idx for idx, (_, _, indexed) in enumerate(parsed_args) if not indexed]

        for log in txns:
            event_data = {
                "txn_hash": log["transactionHash"].hex(),
                "block_num": log["blockNumber"],
            }

            # Extract indexed arguments
            for idx, pos in enumerate(indexed_args_positions):
                arg_type, arg_name, _ = parsed_args[pos]
                value = log["topics"][idx + 1].hex()

                if arg_type == "address":
                    value = self.addr_utils.addr_to_hex(value)
                    value = self.addr_utils.clean_address(value)

                elif arg_type == "uint256":
                    multiplier = 10 ** self.config["decimals"].get(arg_name, 0)
                    value = int(value, 16) / multiplier

                elif arg_type == "bool":
                    value = self.contract_utils.parse_bool(value)

                event_data[arg_name] = value

            # Extract and decode non-indexed arguments
            data_offset = 0
            for idx, pos in enumerate(non_indexed_args_positions):
                arg_type, arg_name, _ = parsed_args[pos]
                raw_data = log["data"][data_offset: data_offset + 32]

                decoded_data = self.w3.eth.codec.decode([arg_type], raw_data)[0]

                if arg_type == "uint256":
                    multiplier = 10 ** self.config["decimals"].get(arg_name, 0)
                    decoded_data = decoded_data / multiplier

                elif arg_type == "address":
                    decoded_data = self.addr_utils.clean_address(decoded_data)

                elif arg_type == "bool":
                    decoded_data = self.contract_utils.parse_bool(decoded_data)

                event_data[arg_name] = decoded_data
                data_offset += 32

            events.append(event_data)

        return json.dumps(events, indent=4)


"""
1. Other Data Types: The approach should work for most Ethereum standard types, including but not limited to int, bytes, bool, and address. However, for more complex data types like struct or custom arrays, additional handling might be required.
2. Events Without Indexed Fields: The code, as it's currently structured, should handle events that don't have indexed fields. In the event processing loop, if an argument isn't indexed, it'll look into the data part of the log, and if it's indexed, it'll look into the topics. So, even if there are no indexed fields, the code will simply fetch all data from the data part.
3. Events with All Indexed Fields: If an event has all its fields indexed, the code will only fetch from topics after skipping the first topic which is reserved for the event signature.
4. Events Without Any Data: If an event signature doesn't have any data (rare, but possible), our loop will effectively not run, so there shouldn't be an issue.
5. Multiple Events with the Same Name but Different Parameters: This is a tricky scenario. The Ethereum ABI does not handle overloading very well, so if you have two events with the same name but different parameters, they could produce colliding signatures. This is a rare case but worth mentioning. In such cases, additional logic will be required.
6. Dynamic Types: If an event contains a dynamic type like string or bytes, the data part of the log needs additional processing to handle these dynamic fields. The current logic assumes fixed-length (32 bytes) arguments, so this would need to be addressed if you anticipate events with dynamic types.
For a thorough verification, I would recommend testing the tool with a variety of events from different contracts to ensure full compatibility. If you run into issues with specific event types or configurations, please provide the details, and I'd be happy to help further!




    def get_erc20_transfers(
        self,
        contract_addr: str,
        start_block: int = 0,
        end_block="latest",
        from_address: str = None,
        to_address: str = None,
    ):
        '''
        Previous working version: Extract all ERC20 token transfers from/to a contract.
        '''
        transfer_signature = self.w3.keccak(
            text="Transfer(address,address,uint256)"
        ).hex()
        topics = [transfer_signature]

        # If from_address is provided, add it as a topic with padding
        if from_address:
            topics.append(self.addr_utils.addr_to_hex(from_address))
        elif (
            to_address
        ):  # If only to_address is provided, add a None placeholder for from_address
            topics.append(None)

        # If to_address is provided, add it as a topic with padding
        if to_address:
            topics.append(self.addr_utils.addr_to_hex(to_address))

        filter_params = {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": self.addr_utils.addr_checksum(contract_addr),
            "topics": topics,
        }
        print("topics:", topics)
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

"""
