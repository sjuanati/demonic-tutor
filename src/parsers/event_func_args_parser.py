from constants import EVM_WORD_SIZE
from utils.logger import setup_logger
from utils.address import AddressUtils
from utils.exceptions import ParserEventError

logger = setup_logger(__name__)


class EventFuncArgsParser:
    def __init__(self, w3_instance, context):
        self.w3 = w3_instance
        self.addr_utils = AddressUtils(self.w3)
        self.context = context

    def parse_indexed_args(self, log, parsed_args, config):
        """
        Returns a dictionary with all indexed arguments from a log entry.
        E.g.: {'sender': '0xd790d', 'recipient': '0x790d', 'tranche': True}
        """
        try:
            event_data = {}
            for i, (arg_type, arg_name) in enumerate(
                (arg_type, arg_name)
                for arg_type, arg_name, indexed in parsed_args
                if indexed
            ):
                raw_data = log["topics"][i + 1]
                decoded_value = self.decode_and_convert(
                    arg_type, raw_data, config["decimals"].get(arg_name, 0)
                )
                event_data[arg_name] = decoded_value
            return event_data

        except Exception as e:
            logger.error(f"parse_indexed_args(): {e}")
            raise ParserEventError()

    # TODO: test non-uint arrays
    def parse_non_indexed_args(self, log, parsed_args, config):
        """
        Returns a dictionary with all non-indexed arguments from a log entry.
        E.g.:  {'amount': 33.873, 'index': 0, 'yieldTokenAmounts': 32.806, 'calcAmount': 33.873}
        """
        event_data = {}
        data_offset = 0

        for _, (arg_type, arg_name, indexed) in enumerate(parsed_args):
            if not indexed:
                decimals = config["decimals"].get(arg_name, 0)
                # Handle dynamic-size array types
                if "[]" in arg_type:
                    event_data[arg_name], data_offset = self._parse_dynamic_array(
                        log, arg_type, data_offset, decimals
                    )
                # Handle fixed-size array types
                elif "[" in arg_type and "]" in arg_type:
                    event_data[arg_name], data_offset = self._parse_fixed_array(
                        log, arg_type, data_offset, decimals
                    )
                # Handle dynamic-size strings
                elif arg_type == 'string':
                    event_data[arg_name], data_offset = self._parse_dynamic_string(
                        log, data_offset
                    )
                # Handle other types
                else:
                    event_data[arg_name], data_offset = self._parse_scalar_type(
                        log, arg_type, data_offset, decimals
                    )
        return event_data

    def _parse_dynamic_array(self, log, arg_type, data_offset, decimals):
        """
        Returns a dynamic-size array from the log data.
        E.g.: [-7.751727026743274, 0.0] or ['0x..c599', '0x..01c3', '0x..7407']
        """
        try:
            base_type = arg_type.replace("[]", "")

            # Get the position (offset) where the dynamic array starts:
            # - First 32 bytes: lenght of the array (eg: 3)
            # - Following 32 bytes: each element of the array
            raw_data = log["data"][data_offset : data_offset + EVM_WORD_SIZE]
            arr_offset = int.from_bytes(raw_data, byteorder="big")

            # Get the length of the dynamic array and move past the
            # length where the array items start
            raw_data = log["data"][arr_offset : arr_offset + EVM_WORD_SIZE]
            num_items = int.from_bytes(raw_data, byteorder="big")
            arr_offset += EVM_WORD_SIZE

            # Process each array item
            values = []
            for _ in range(num_items):
                raw_data_segment = log["data"][arr_offset : arr_offset + EVM_WORD_SIZE]
                values.append(
                    self.decode_and_convert(base_type, raw_data_segment, decimals)
                )
                arr_offset += EVM_WORD_SIZE

            data_offset += EVM_WORD_SIZE

            return values, data_offset

        except Exception as e:
            logger.error(f"_parse_dynamic_array(): {e}")
            raise ParserEventError()

    def _parse_fixed_array(self, log, arg_type, data_offset, decimals):
        """
        Returns a fixed-size array from the log data.
        E.g.: [577758.84, 2498856.81]
        """
        try:
            base_type = arg_type.split("[")[0]
            length = int(arg_type.split("[")[1].split("]")[0])
            values = []

            # Process each array item
            for i in range(length):
                raw_data_segment = log["data"][
                    data_offset : data_offset + EVM_WORD_SIZE
                ]
                values.append(
                    self.decode_and_convert(base_type, raw_data_segment, decimals, i)
                )
                data_offset += EVM_WORD_SIZE

            return values, data_offset

        except Exception as e:
            logger.error(f"_parse_fixed_array(): {e}")
            raise ParserEventError()

    def _parse_dynamic_string(self, log, data_offset):
        """
        Returns a string from the log data.
        """
        try:
            # Get the position (offset) where the dynamic string starts:
            # - First 32 bytes: offset of the string data (eg: 0x80)
            raw_data = log["data"][data_offset:data_offset + EVM_WORD_SIZE]
            str_offset = int.from_bytes(raw_data, byteorder="big")

            # Get the length of the dynamic string and move past the
            # length where the string data starts
            raw_data = log["data"][str_offset:str_offset + EVM_WORD_SIZE]
            str_length = int.from_bytes(raw_data, byteorder="big")
            str_offset += EVM_WORD_SIZE

            # Extract the string data
            raw_string_data = log["data"][str_offset:str_offset + str_length]

            # Decode the string data from bytes to a UTF-8 string
            decoded_string = raw_string_data.decode('utf-8')

            # Update data_offset by the size of the offset
            data_offset += EVM_WORD_SIZE

            return decoded_string, data_offset

        except Exception as e:
            logger.error(f"_parse_dynamic_string(): {e}")
            raise ParserEventError()


    def _parse_scalar_type(self, log, arg_type, data_offset, decimals):
        """
        Returns ascalar type from the log data (non indexed / non array arguments)
        E.g.: 306.27 or 0x..49aC
        """
        try:
            raw_data = log["data"][data_offset : data_offset + EVM_WORD_SIZE]
            value = self.decode_and_convert(arg_type, raw_data, decimals)
            data_offset += EVM_WORD_SIZE

            return value, data_offset

        except Exception as e:
            logger.error(f"_parse_scalar_type(): {e}")
            raise ParserEventError()

    # TODO: other types: bool, enums, mappings, strings
    def decode_and_convert(self, data_type, raw_data, decimals, index=0):
        """Decodes raw blockchain data of a given type into a human-readable format."""
        try:
            decoded = self.w3.eth.codec.decode([data_type], raw_data)[0]

            # dev: Not needed if every dynamic item will have the same decimal
            # Fetch the right decimal if it's an array
            if isinstance(decimals, list):
                decimals = decimals[index]

            if data_type.startswith("uint") or data_type.startswith("int"):
                multiplier = 10**decimals
                return decoded / multiplier

            elif data_type == "address":
                return self.addr_utils.clean_address(decoded)

            elif data_type.startswith("bytes"):
                return decoded.hex()

            return decoded

        except Exception as e:
            logger.error(f"decode_and_convert(): {e}")
            raise ParserEventError()

    @staticmethod
    def parse_txn_data(log):
        """
        Returns the transaction hash and block number from a given log entry
        """
        return {
            "txn_hash": log["transactionHash"].hex(),
            "block_num": log["blockNumber"],
        }
