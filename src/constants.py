EVM_WORD_SIZE = 32  # Size in bytes for each record in the data section of an Ethereum event
LOG_BACKUP_COUNT = 15  # Number of log backups to retain
LOG_FILE_MAX_SIZE = 300 * 10**6  # 300 MB
# TODO: genesis timestamp should be different by network
ETH_GENESIS_BLOCK = 1438269973 # timestamp for the 1st ethereum block
NETWORKS = {
    "ETHEREUM": "ETHEREUM",
    "ARBITRUM": "ARBITRUM",
    "AVALANCHE": "AVALANCHE",
    "BINANCE": "BINANCE",
    "OPTIMISM": "OPTIMISM",
    "POLYGON": "POLYGON",
}
