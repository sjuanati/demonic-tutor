import json

from utils.address import AddressUtils
from utils.contract import ContractUtils
from utils.file import FileUtils


class EventsExtractor:
    def __init__(self, w3_instance, model: str):
        self.w3 = w3_instance
        self.addr_utils = AddressUtils(self.w3)
        self.contract_utils = ContractUtils(self.w3)
        self.config = FileUtils.read_model(model)

    def get_data(self):
        function_signature = self.contract_utils.parse_function_signature(
            self.config["function_signature"]
        )
        parsed_args = self.contract_utils.parse_function_args(
            self.config["function_signature"]
        )
        numeric_types = self.config["numeric_types"]

        topics = [function_signature]
        filter_index = 0  # An index to keep track of our position in the "filters" list

        for _, _, indexed in parsed_args:
            if indexed:
                if filter_index < len(
                    self.config["filters"]
                ):  # Ensure we don't go out of bounds
                    filter_val = self.config["filters"][filter_index]
                    if filter_val:
                        topics.append(self.addr_utils.addr_to_hex(filter_val))
                    else:
                        topics.append(None)
                    filter_index += 1
                else:
                    topics.append(None)

        filter_params = {
            "fromBlock": self.config["start_block"],
            "toBlock": self.config["end_block"],
            "address": self.addr_utils.addr_checksum(self.config["contract_addr"]),
            "topics": topics,
        }
        print("filter_params", filter_params)
        events = []

        txns = self.w3.eth.get_logs(filter_params)

        """
        The topics array holds the indexed arguments. The first element of this array is always the event signature.
        The data field holds the non-indexed arguments, and this is where decoding based on type is important. Each argument is typically 32 bytes.
        Given your requirement, the aim is to simplify this process by making assumptions:

        We assume that the order of topics (after the first entry) and the order of parsed_args (with indexed=True) are the same.
        Similarly, the order of non-indexed arguments in the data field matches the order of parsed_args (with indexed=False).
        """
        for log in txns:
            event_data = {
                "txn_hash": log["transactionHash"].hex(),
                "block_num": log["blockNumber"],
            }

            # Extract indexed arguments
            indexed_args = [
                arg for arg in parsed_args if arg[2]
            ]  # where arg[2] is the indexed flag
            for idx, (arg_type, arg_name, _) in enumerate(indexed_args):
                value = log["topics"][idx + 1].hex()

                # If it's an address type, format it properly and then clean it up
                if arg_type == "address":
                    value = self.addr_utils.addr_to_hex(
                        value
                    )  # This ensures 0x-prefixed 42 characters
                    value = self.addr_utils.clean_address(
                        value
                    )  # Now remove unnecessary leading zeros

                # If it's a numeric type, adjust its value
                elif numeric_types[idx]:
                    multiplier = 10 ** numeric_types[idx]
                    value = int(value, 16) / multiplier

                event_data[arg_name] = value

            # Extract and decode non-indexed arguments
            non_indexed_args = [arg for arg in parsed_args if not arg[2]]
            data_offset = 0
            non_indexed_idx_offset = len(
                indexed_args
            )  # To get the correct index from numeric_types
            for idx, (arg_type, arg_name, _) in enumerate(non_indexed_args):
                raw_data = log["data"][data_offset : data_offset + 32]
                decoded_data = self.w3.eth.codec.decode([arg_type], raw_data)[
                    0
                ]  # decode() returns a list, get the first item

                # If it's a numeric type, adjust its value
                if numeric_types[non_indexed_idx_offset + idx]:
                    multiplier = 10 ** numeric_types[non_indexed_idx_offset + idx]
                    decoded_data = decoded_data / multiplier

                event_data[arg_name] = decoded_data
                data_offset += 32

            events.append(event_data)

        # handle comma in the last records
        return json.dumps(events, indent=4)

    def get_erc20_transfers(
        self,
        contract_addr: str,
        start_block: int = 0,
        end_block="latest",
        from_address: str = None,
        to_address: str = None,
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
1. Other Data Types: The approach should work for most Ethereum standard types, including but not limited to int, bytes, bool, and address. However, for more complex data types like struct or custom arrays, additional handling might be required.
2. Events Without Indexed Fields: The code, as it's currently structured, should handle events that don't have indexed fields. In the event processing loop, if an argument isn't indexed, it'll look into the data part of the log, and if it's indexed, it'll look into the topics. So, even if there are no indexed fields, the code will simply fetch all data from the data part.
3. Events with All Indexed Fields: If an event has all its fields indexed, the code will only fetch from topics after skipping the first topic which is reserved for the event signature.
4. Events Without Any Data: If an event signature doesn't have any data (rare, but possible), our loop will effectively not run, so there shouldn't be an issue.
5. Multiple Events with the Same Name but Different Parameters: This is a tricky scenario. The Ethereum ABI does not handle overloading very well, so if you have two events with the same name but different parameters, they could produce colliding signatures. This is a rare case but worth mentioning. In such cases, additional logic will be required.
6. Dynamic Types: If an event contains a dynamic type like string or bytes, the data part of the log needs additional processing to handle these dynamic fields. The current logic assumes fixed-length (32 bytes) arguments, so this would need to be addressed if you anticipate events with dynamic types.
For a thorough verification, I would recommend testing the tool with a variety of events from different contracts to ensure full compatibility. If you run into issues with specific event types or configurations, please provide the details, and I'd be happy to help further!






"""
