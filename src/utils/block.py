import time
import calendar

from datetime import datetime
from utils.logger import setup_logger
from constants import ETH_GENESIS_BLOCK
from utils.exceptions import BlockUtilsError

logger = setup_logger(__name__)


class BlockUtils:
    TS_ERROR_MSG = "Wrong ts: {} (for reference, current ts = {})"
    RANGE_ERROR_MSG = "Ts {} out of blockchain data range {} to {}"

    def __init__(self, w3_instance):
        self.w3 = w3_instance

    @staticmethod
    def convert_date_to_ts(date: str):
        try:
            dt = datetime.strptime(date, "%Y%m%d %H:%M:%S")
            return calendar.timegm(dt.utctimetuple())
        except Exception as e:
            logger.error(e)
            raise BlockUtilsError()

    @staticmethod
    def validate_timestamp(timestamp: int):
        """Validate if the provided timestamp format is correct."""
        current_time = int(time.time())
        if (
            not isinstance(timestamp, int)
            or timestamp < ETH_GENESIS_BLOCK
            or timestamp > current_time
        ):
            logger.error(BlockUtils.TS_ERROR_MSG.format(timestamp, current_time))
            raise BlockUtilsError()

    def validate_range(self, timestamp: int):
        """Validate if the provided timestamp is within the range of the blockchain data"""
        earliest_ts = self.w3.eth.get_block("earliest").timestamp
        latest_ts = self.w3.eth.get_block("latest").timestamp
        if not (earliest_ts <= timestamp <= latest_ts):
            logger.error(self.RANGE_ERROR_MSG.format(timestamp, earliest_ts, latest_ts))
            raise BlockUtilsError()

    def get_closest_block_number_by_timestamp(self, timestamp: int) -> int:
        """Return the closest block number (before or at) the given timestamp using binary search."""
        try:
            # Validate timestamp format
            self.validate_timestamp(timestamp)

            # Validate timestamp range
            self.validate_range(timestamp)

            # start binary search
            lower, upper = (
                self.w3.eth.get_block("earliest").number,
                self.w3.eth.get_block("latest").number,
            )

            if timestamp <= self.w3.eth.get_block(lower).timestamp:
                return lower

            while lower <= upper:
                mid = (lower + upper) // 2
                mid_block = self.w3.eth.get_block(mid)
                mid_timestamp = mid_block.timestamp

                if mid_timestamp == timestamp:
                    return mid
                elif mid_timestamp < timestamp:
                    lower = mid + 1
                else:
                    upper = mid - 1

            return lower - 1
        except BlockUtilsError:
            raise
        except Exception as e:
            logger.error(f"Failed to get closest block number by timestamp: {e}")
            raise BlockUtilsError()

    def get_closest_block_number_by_date(self, date: str) -> int:
        """Return the closest block number (before or at) the given date using binary search."""

        # Validate date format
        ts = self.convert_date_to_ts(date)
        return self.get_closest_block_number_by_timestamp(ts)
