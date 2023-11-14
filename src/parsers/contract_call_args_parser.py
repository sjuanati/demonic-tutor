from utils.logger import setup_logger
from utils.address import AddressUtils

logger = setup_logger(__name__)


class ContractCallArgsParser:
    def __init__(self, w3_instance, context):
        self.w3 = w3_instance
        self.addr_utils = AddressUtils(self.w3)
        self.context = context

    def parse_args(self, args, types):
        if len(args) != len(types):
            print("norrr")
            # raise e

        parsed_args = []
        for i in range(len(args)):
            parsed_args.append(
                self._parse_argument(list(args.values())[i], list(types.values())[i])
            )
        return parsed_args

    # TODO:
    # - detect return type and apply 1e18 or 1e6 conversions if uint
    def _parse_argument(self, arg: str, type: str):
        if type == "bool":
            if isinstance(arg, bool):
                return arg
            else:
                error_msg = f'_parse_argument(): arg: {arg} is not a boolean type (True or False)'
                logger.error(error_msg)
                raise ValueError(error_msg)
        elif type.startswith("uint") or type.startswith("int"):
            return arg
        elif type == "address":
            return self.addr_utils.addr_checksum(arg)
        else:
            error_msg = f'_parse_argument(): No matching type: {type}'
            logger.error(error_msg)
            raise ValueError(error_msg)
        # TODO: arrays, structs
