"""
From the main menu, if option `4) Call Contract function` is chosen and no model name is given,
the model to be executed will be that in /src/models/default_contract.json.
"""

default_contract = {
    "contract_addr": (
        "Address of the EVM contract to retrieve data from. "
        "E.g.: 0xF43c6bDD2F9158B5A78DCcf732D190C490e28644"
    ),
    "block": "Block number at which the data retrieval is targeted. E.g.: 18564560",
    "function_name": "Exact name of the contract function to be called. E.g.: vestedBalance",
    "arguments": (
        "Arguments to pass to the function. Must contain ALL arguments from the function signature. "
        "E.g.: {'account': '0xd0ec53a6144dee637052bf94b443fd1d49f45076'}"
    ),
    "arg_types": (
        "Types of the function arguments. Must match the argument types from the function signature exactly. "
        "E.g.: {'account': 'address'}"
    ),
    "output_decimals": (
        "Optional. If provided, defines the number of decimal places for numeric outputs; "
        "if not applicable, use an empty object '{}'. "
        "E.g.: {'vested': 18, 'available': 18}"
    ),
    "abi": "Contract's ABI containing the function to be called. ",
}
