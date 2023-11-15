"""e.g.: Github search: "bytes32[] indexed" """

import os
import sys
import json
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import NETWORKS
from utils.file import FileUtils
from utils.context import Context
from demonic_tutor import DemonicTutor


class CallTester(unittest.TestCase):
    def setUp(self):
        self.dt = DemonicTutor(NETWORKS["ETHEREUM"])
        self.loader = FileUtils()

    def test_address_uint_args(self):
        """tbd"""
        actual = json.loads(
            self.dt.export_call_data("01_addr_uint_args.json", Context.TEST_CALL.INPUT)
        )
        expected = self.loader.read_file(
            "01_addr_uint_args.json", Context.TEST_CALL.OUTPUT
        )
        self.assertEqual(actual, expected)

    def test_no_args_infinity_value(self):
        """Variable (instead of function) returning an infinity value"""
        actual = json.loads(
            self.dt.export_call_data(
                "02_no_args_infinity_result.json", Context.TEST_CALL.INPUT
            )
        )
        expected = self.loader.read_file(
            "02_no_args_infinity_result.json", Context.TEST_CALL.OUTPUT
        )
        self.assertEqual(actual, expected)

    def test_bool_arg(self):
        """Boolean argument"""
        actual = json.loads(
            self.dt.export_call_data("03_bool_arg.json", Context.TEST_CALL.INPUT)
        )
        expected = self.loader.read_file("03_bool_arg.json", Context.TEST_CALL.OUTPUT)
        self.assertEqual(actual, expected)

    def test_array_with_decimal_conversion(self):
        """Boolean argument"""
        actual = json.loads(
            self.dt.export_call_data("04_arrays_with_dec_conversion.json", Context.TEST_CALL.INPUT)
        )
        expected = self.loader.read_file("04_arrays_with_dec_conversion.json", Context.TEST_CALL.OUTPUT)
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
