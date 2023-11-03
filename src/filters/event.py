from utils.file import FileUtils
from utils.context import Context
from utils.logger import setup_logger
from utils.address import AddressUtils

logger = setup_logger(__name__)


def build_filter_params(config, function_sig, parsed_args, w3_instance, context):
    addr_utils = AddressUtils(w3_instance)

    topics = [function_sig]

    for arg_type, arg_name, indexed in parsed_args:
        if indexed:
            filter_value = config["filters"].get(arg_name)
            if filter_value is not None:
                if arg_type == "address":
                    filter_value = addr_utils.addr_to_hex(filter_value)
                # TODO: test filtering by integer
                elif arg_type.startswith("uint"):
                    filter_value = hex(filter_value)
                elif isinstance(filter_value, bool):
                    filter_value = "0x{:064x}".format(int(filter_value))
                # TODO: Add more type conversions if necessary
                topics.append(filter_value)
            else:
                topics.append(None)

    filter_params = {
        "fromBlock": config["start_block"],
        "toBlock": config["end_block"],
        "address": addr_utils.addr_checksum(config["contract_addr"]),
        "topics": topics,
    }

    if context == Context.MAIN.INPUT:
        logger.info(f"filter: {filter_params}")

    return filter_params
