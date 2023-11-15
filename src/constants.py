LOG_BACKUP_COUNT = 15  # Number of log backups to retain
LOG_FILE_MAX_SIZE = 300 * 10**6  # 300 MB
EVM_WORD_SIZE = (
    32  # Size in bytes for each record in the data section of an Ethereum event
)
DEFAULT_CALL_FILE = "default_call.json"
DEFAULT_EVENT_FILE = "default_event.json"
NETWORKS = {
    "ETHEREUM": "ETHEREUM",
    "ARBITRUM": "ARBITRUM",
    "AVALANCHE": "AVALANCHE",
    "BINANCE": "BINANCE",
    "OPTIMISM": "OPTIMISM",
    "POLYGON": "POLYGON",
}
GENESIS_TS = {
    "ETHEREUM": 1438269973, # Thursday 30 July 2015 15:26:13
    "ARBITRUM": 1622240000, # Friday 28 May 2021 22:13:20
    "AVALANCHE": 1600858926, # Wednesday 23 September 2020 11:02:06
    "BINANCE": 1598671448, # Saturday 29 August 2020 3:24:08
    "OPTIMISM": 1610639500, # Thursday 14 January 2021 15:51:40
    "POLYGON": 1590824836, # Saturday 30 May 2020 7:47:16
}

