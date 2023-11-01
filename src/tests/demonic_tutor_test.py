import os
import sys
import json
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import DemonicTutor
from utils.file import FileUtils

from dotenv import load_dotenv

load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")


class TestDemonicTutorParsing(unittest.TestCase):
    def setUp(self):
        self.dt = DemonicTutor(INFURA_URL)
        self.loader = FileUtils()

    def test_bool_filter(self):
        """
        Filter by indexed boolean
        LogNewWithdrawal(address indexed sender, address indexed recipient, uint256 amount, uint256 index, bool indexed tranche...);
        """
        actual = json.loads(self.dt.get_data("04_bool_filter.json", "TestDemonicTutor"))
        expected = self.loader.read_output_test("04_bool_filter.json")

        self.assertEqual(actual, expected)

    def test_array(self):
        """
        Array of integers
        LogNewTrancheBalance(uint256[2],uint256)
        """
        actual = json.loads(self.dt.get_data("05_array.json", "TestDemonicTutor"))
        expected = self.loader.read_output_test("05_array.json")

        self.assertEqual(actual, expected)

    def test_array_multiple_types(self):
        """
        Array of integers with different decimals -> [1e18, 1e6, 1e6]
        LogNewWithdrawal (index_topic_1 address user, ..., uint256[3] tokenAmounts)
        """
        actual_dai = json.loads(self.dt.get_data("06_array_multi_decimals_1.json", "TestDemonicTutor"))
        expected_dai = self.loader.read_output_test("06_array_multi_decimals_1.json")

        actual_usdc = json.loads(self.dt.get_data("06_array_multi_decimals_2.json", "TestDemonicTutor"))
        expected_usdc = self.loader.read_output_test("06_array_multi_decimals_2.json")

        self.assertEqual(actual_dai, expected_dai)
        self.assertEqual(actual_usdc, expected_usdc)

    def test_negative_amount(self):
        """
        Negative amount
        Swap (index_topic_1 address sender, ..., uint128 liquidity, int24 tick)
        """
        actual = json.loads(self.dt.get_data("07_negative_amount.json", "TestDemonicTutor"))
        expected = self.loader.read_output_test("07_negative_amount.json")

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
