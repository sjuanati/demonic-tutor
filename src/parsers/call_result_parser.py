import re

from utils.logger import setup_logger
from utils.address import AddressUtils
from utils.exceptions import ParserCallError

logger = setup_logger(__name__)


class CallResultParser:
    def __init__(self, w3_instance):
        self.w3 = w3_instance
        self.addr_utils = AddressUtils(self.w3)

    def parse_result(self, func_name, abi, result, output_decimals):
        """
        Parses contract call results into a formatted dictionary with decimal conversions.
        """
        try:
            # Ensure result is in list format, as it returns a list if 2+ output values
            # or a single value if only 1 output value
            if not isinstance(result, list):
                result = [result]

            # Extract output parameter names from ABI
            function_abi = next(filter(lambda f: f.get("name") == func_name, abi), None)

            # Check if there are output variable names
            if function_abi and "outputs" in function_abi:
                # Retrieves output names or assigns `output_N` if not found
                output_names = self._get_output_names(function_abi)

                # if output_decimals is fulfilled in the Model
                if output_decimals:
                    result = self._apply_decimal_conversion(
                        result, output_names, output_decimals
                    )

                # Map the result tuple to a dictionary using the output names
                return dict(zip(output_names, result))
            else:
                # Show result without output names
                logger.warning(f"No ABI entry found for func {func_name}")
                return {f"output_{i}": val for i, val in enumerate(result)}
        except Exception as e:
            logger.error(f"parse_result(): {e}")
            raise ParserCallError(e)

    @staticmethod
    def _get_output_names(function_abi):
        """
        Extracts or assigns names to ABI output parameters.
        """
        # give names to output variables based on ABI definition
        output_names = [
            output["name"] for output in function_abi["outputs"] if "name" in output
        ]
        # give names to output variables (when they are not functions)
        output_names = [
            f"output_{i+1}" if item == "" else item
            for i, item in enumerate(output_names)
        ]
        return output_names

    def _apply_decimal_conversion(self, result, output_names, output_decimals):
        """
        Applies decimal conversions to numerical output values.
        """
        # Check if output_decimal elements are aligned with expected ABI output
        self._check_outputs(output_names, output_decimals)

        # If there are decimal values (>0), apply 10**N conversion
        for i in range(len(output_decimals)):
            dec_value = list(output_decimals.values())[i]
            if dec_value and dec_value > 0:
                # handle arrays, applying the same decimal conversion to all elems
                if isinstance(result[i], list):
                    result[i] = [item / 10**dec_value for item in result[i]]
                # handle single values
                else:
                    result[i] = result[i] / 10**dec_value

        return result

    def _check_outputs(self, output_names, output_decimals):
        """
        Verifies alignment of output names with decimal definitions.
        """
        # Formatting the args for printing
        f_output_names = (
            f'ABI output names: ({", ".join(name for name in output_names)})'
        )
        f_output_decimals = f'Model output decimal names: ({", ".join(name for name in output_decimals)})'

        # Check if both args have the same number of records
        if len(output_names) != len(output_decimals):
            error_msg = f"Num. of {f_output_names} != Num. of {f_output_decimals}"
            self._raise_exception("_check_outputs", error_msg)

        # Check if both args have the same names
        if not all(name in output_decimals for name in output_names):
            error_msg = f"Names for {f_output_names} != Names for {f_output_decimals}"
            self._raise_exception("_check_outputs", error_msg)

    @staticmethod
    def _raise_exception(func: str, error_msg: str):
        """
        Logs and raises a formatted exception.
        """
        err = f"{func}(): {error_msg}"
        logger.error(err)
        raise ParserCallError(err)
