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


class EventTester(unittest.TestCase):
    def setUp(self):
        self.dt_eth = DemonicTutor(NETWORKS["ETHEREUM"])
        self.dt_avax = DemonicTutor(NETWORKS["AVALANCHE"])
        self.dt_matic = DemonicTutor(NETWORKS["POLYGON"])
        self.dt_op = DemonicTutor(NETWORKS["OPTIMISM"])
        self.loader = FileUtils()

    def test_eth_dynamic_string_and_bytes(self):
        """
        Non-indexed dynamic string and bytes arguments
        LogicContractSet (string _version, uint256 _upgrade, address _logicContract, bytes _upgradeData)
        """
        actual = json.loads(
            self.dt_eth.export_log_data(
                "01_eth_dynamic_string_and_bytes.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "01_eth_dynamic_string_and_bytes.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_eth_indexed_bytes32(self):
        """
        Indexed bytes32 argument
        ModuleAdded (uint8[] _types, index_topic_1 bytes32 _name, ...)
        """
        actual = json.loads(
            self.dt_eth.export_log_data(
                "02_eth_indexed_bytes32.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "02_eth_indexed_bytes32.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_eth_string(self):
        """
        String argument
        RegisterTicker (index_topic_1 address _owner, string _ticker, ...)
        """
        actual = json.loads(
            self.dt_eth.export_log_data("03_eth_string.json", Context.TEST_EVENT.INPUT)
        )
        expected = self.loader.read_file(
            "03_eth_string.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_eth_bool_filter(self):
        """
        Filter by indexed boolean
        LogNewWithdrawal(address indexed sender, address indexed recipient, uint256 amount, uint256 index, bool indexed tranche...);
        """
        actual = json.loads(
            self.dt_eth.export_log_data(
                "04_eth_bool_filter.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "04_eth_bool_filter.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_eth_array_and_no_indices(self):
        """
        Array of integers
        LogNewTrancheBalance(uint256[2],uint256)
        """
        actual = json.loads(
            self.dt_eth.export_log_data(
                "05_eth_array_no_indices.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "05_eth_array_no_indices.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_eth_array_multiple_types(self):
        """
        Array of integers with different decimals -> [1e18, 1e6, 1e6]
        LogNewWithdrawal (index_topic_1 address user, ..., uint256[3] tokenAmounts)
        """
        actual_dai = json.loads(
            self.dt_eth.export_log_data(
                "06_eth_array_multi_decimals.json", Context.TEST_EVENT.INPUT
            )
        )
        expected_dai = self.loader.read_file(
            "06_eth_array_multi_decimals.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual_dai, expected_dai)

    def test_eth_negative_amount(self):
        """
        Negative amount
        Swap (index_topic_1 address sender, ..., uint128 liquidity, int24 tick)
        """
        actual = json.loads(
            self.dt_eth.export_log_data(
                "07_eth_negative_amount.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "07_eth_negative_amount.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_eth_dynamic_array(self):
        """
        3 dynamic arrays
        PoolBalanceChanged (..., address[] tokens, int256[] deltas, uint256[] protocolFeeAmounts)
        """
        actual = json.loads(
            self.dt_eth.export_log_data(
                "08_eth_dynamic_array.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "08_eth_dynamic_array.json", Context.TEST_EVENT.OUTPUT
        )

        self.assertEqual(actual, expected)

    def test_avax_general(self):
        """
        Test a random Avalanche event (e.g.: Aave's Accrued event)
        """
        actual = json.loads(
            self.dt_avax.export_log_data(
                "09_avax_sample.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "09_avax_sample.json", Context.TEST_EVENT.OUTPUT
        )
        self.assertEqual(actual, expected)

    def test_polygon_general(self):
        """
        Test a random Polygon event (e.g.: Aave's LogFeeTransfer event)
        """
        actual = json.loads(
            self.dt_matic.export_log_data(
                "10_matic_sample.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "10_matic_sample.json", Context.TEST_EVENT.OUTPUT
        )
        self.assertEqual(actual, expected)

    def test_op_general(self):
        """
        Filter by indexed bytes32 and uint8
        RegistrationRequested (index_topic_1 bytes32 hash ..., index_topic_3 uint8 source)
        """
        actual = json.loads(
            self.dt_op.export_log_data(
                "11_op_int_bytes_filters.json", Context.TEST_EVENT.INPUT
            )
        )
        expected = self.loader.read_file(
            "11_op_int_bytes_filters.json", Context.TEST_EVENT.OUTPUT
        )
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
