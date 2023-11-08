import os
import sys
import json
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demonic_tutor import DemonicTutor
from dotenv import load_dotenv
from utils.file import FileUtils
from utils.context import Context

load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")


class EventTester(unittest.TestCase):
    def setUp(self):
        self.dt = DemonicTutor(INFURA_URL)
        self.loader = FileUtils()

    def test_string(self):
        """
        Filter by indexed boolean
        RegisterTicker (index_topic_1 address _owner, string _ticker, ...)
        """
        actual = json.loads(self.dt.export_log_data("03_string.json", Context.TEST.INPUT))
        expected = self.loader.read_file("03_string.json", Context.TEST.OUTPUT)

        self.assertEqual(actual, expected)

    def test_bool_filter(self):
        """
        Filter by indexed boolean
        LogNewWithdrawal(address indexed sender, address indexed recipient, uint256 amount, uint256 index, bool indexed tranche...);
        """
        actual = json.loads(self.dt.export_log_data("04_bool_filter.json", Context.TEST.INPUT))
        expected = self.loader.read_file("04_bool_filter.json", Context.TEST.OUTPUT)

        self.assertEqual(actual, expected)

    def test_array_and_no_indices(self):
        """
        Array of integers
        LogNewTrancheBalance(uint256[2],uint256)
        """
        actual = json.loads(
            self.dt.export_log_data("05_array_no_indices.json", Context.TEST.INPUT)
        )
        expected = self.loader.read_file(
            "05_array_no_indices.json", Context.TEST.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_array_multiple_types(self):
        """
        Array of integers with different decimals -> [1e18, 1e6, 1e6]
        LogNewWithdrawal (index_topic_1 address user, ..., uint256[3] tokenAmounts)
        """
        actual_dai = json.loads(
            self.dt.export_log_data("06_array_multi_decimals_1.json", Context.TEST.INPUT)
        )
        expected_dai = self.loader.read_file(
            "06_array_multi_decimals_1.json", Context.TEST.OUTPUT
        )

        actual_usdc = json.loads(
            self.dt.export_log_data("06_array_multi_decimals_2.json", Context.TEST.INPUT)
        )
        expected_usdc = self.loader.read_file(
            "06_array_multi_decimals_2.json", Context.TEST.OUTPUT
        )

        self.assertEqual(actual_dai, expected_dai)
        self.assertEqual(actual_usdc, expected_usdc)

    def test_negative_amount(self):
        """
        Negative amount
        Swap (index_topic_1 address sender, ..., uint128 liquidity, int24 tick)
        """
        actual = json.loads(
            self.dt.export_log_data("07_negative_amount.json", Context.TEST.INPUT)
        )
        expected = self.loader.read_file("07_negative_amount.json", Context.TEST.OUTPUT)

        self.assertEqual(actual, expected)

    def test_dynamic_array(self):
        """
        3 dynamic arrays
        PoolBalanceChanged (..., address[] tokens, int256[] deltas, uint256[] protocolFeeAmounts)
        """
        actual = json.loads(
            self.dt.export_log_data("08-dynamic_array.json", Context.TEST.INPUT)
        )
        expected = self.loader.read_file("08-dynamic_array.json", Context.TEST.OUTPUT)

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
