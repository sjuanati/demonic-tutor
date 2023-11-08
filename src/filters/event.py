from utils.context import Context
from utils.logger import setup_logger
from utils.address import AddressUtils
from utils.exceptions import FilterEventError

logger = setup_logger(__name__)


def build_filter_params(
    config, function_sig, parsed_args, w3_instance, context, num_indexed_args
):
    try:
        addr_utils = AddressUtils(w3_instance)
        topics = [function_sig]

        # check if # indexed args in signature = indexed args in model->filters
        num_indexed_args_in_model = len(config["filters"])
        if num_indexed_args != num_indexed_args_in_model:
            e = (
                f"{num_indexed_args} indexed args in function, but "
                f"{num_indexed_args_in_model} in model->filters section"
            )
            raise ValueError(e)

        for arg_type, arg_name, indexed in parsed_args:
            if indexed:
                filter_value = config["filters"].get(arg_name)
                # TODO: include bytes
                if filter_value is not None:
                    if arg_type == "address":
                        filter_value = addr_utils.addr_to_hex(filter_value)
                    # TODO: test filtering by integer
                    elif arg_type.startswith("uint") or arg_type.startswith("int"):
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

    except Exception as e:
        logger.error(f"build_filter_params(): {e}")
        raise FilterEventError()
