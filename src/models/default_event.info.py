"""
From the main menu, if option `3) Export Log Data into csv` is chosen and no model name is given,
the model to be executed will be that in /src/models/default_event.json.
The output CSV file will be created at /src/data/default_event.csv.
"""

default_event = {
    "contract_addr": (
        "Address of the EVM contract that emits the events to be extracted. "
        "E.g.: 0x6b175474e89094c44da98b954eedeac495271d0f"
    ),
    "start_block": "Start block number for data extraction. E.g.: 18473342",
    "end_block": "End block number for data extraction. E.g.: 18473542",
    "function_sig": (
        "Function signature copied from Etherscan or the smart contract code. "
        "E.g.: Transfer (index_topic_1 address src, index_topic_2 address dst, uint256 wad)"
    ),
    "filters": (
        "Criteria used to filter events based on indexed parameters. "
        "Must contain ALL indexed arguments. If no indexed arguments in signature, use {}. "
        "E.g.: { 'src': null, 'dst': null }"
    ),
    "decimals": (
        "Used to format integer values into their decimal representations. "
        "Must contain ALL arguments. Only fill in those that are uint or int. "
        "E.g.: { 'src': null, 'dst': null, 'wad': 18 }"
    ),
}
