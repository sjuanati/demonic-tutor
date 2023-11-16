# Demonic Tutor: Your Gateway to EVM Blockchain Data

## Introduction

In the world of Magic: The Gathering, the Demonic Tutor card stands as a powerful tool, granting players the ability to delve into their deck and select precisely the card they need. Drawing inspiration from this, the Demonic Tutor app emerges as a similarly potent instrument in the realm of blockchain technology. Just as the card allows a strategic peek into a deck, this app offers an unparalleled window into the Ethereum Virtual Machine (EVM) blockchain, enabling users to efficiently extract a wealth of data with precision and ease.

![Demonic Tutor pic](https://github.com/sjuanati/demonic-tutor/blob/main/src/img/demonic-tutor.jpg)


## Detailed Guides and Examples

Demonic Tutor streamlines and automates the process of data extraction from EVM-based blockchains, bringing efficiency and depth to blockchain data analysis. Here are its main features:

### Automated Event Data Extraction

Users can easily extract event data over specified block ranges by providing a simple input model. This model includes essential details such as the contract address, block range, event signature, and filters for indexed arguments. This feature simplifies the process of targeting and retrieving specific event data from the blockchain.

### Contract Call Data Retrieval at Any Block

The app allows for performing contract calls to extract data at any given block number. This feature is crucial for analyzing the state of smart contracts at different points in time, offering insights into contract interactions and state changes.

### Flexible Timestamp and Date to Block Number Conversion

Demonic Tutor provides the capability to convert both Unix timestamps and standard date formats into blockchain block numbers, enhancing the accuracy of temporal analysis in blockchain research.

### Multi-Chain Compatibility

The app has been tested across multiple EVM-compatible blockchains, including Ethereum, Polygon, Optimism, Binance Smart Chain, and Avalanche. This multi-chain functionality ensures that users can apply Demonic Tutor across various blockchain environments, maximizing its utility in diverse blockchain ecosystems.

## Features

The app comes equipped with a straightforward and intuitive menu that guides users through its various capabilities. From changing the network for data extraction to exporting logs and calling contract functions, the menu presents a seamless navigation experience:

![Demonic Tutor Main Menu](https://github.com/sjuanati/demonic-tutor/blob/main/src/img/menu.jpg)

Simply input the number corresponding to your desired action, and follow the prompts to execute powerful data retrieval and analysis within the EVM blockchain ecosystem.

### Change Network
To interact with different EVM-compatible blockchains, use option `0` from the main menu to change the network. This will allow you to set the context for subsequent data extraction or contract interaction tasks.

### Convert Timestamp to Block Number

Utilize option `1` from the main menu to convert a Unix timestamp to the corresponding block number.

Example:
```
Please choose an option (0-9): 1
Enter a unix timestamp: 1683532800
block: 17214447
```

### Convert Date to Block Number

Utilize option `2` from the main menu to convert a standard date format to the corresponding block number.

Example:

```
Please choose an option (0-3): 2
Enter the date in format 'YYYYMMDD HH:MM:SS': 20230508 08:00:00
eth block: 17214447
```

### Event Data Extraction

To extract event data, select option `3` from the main menu and follow the prompts. Provide the necessary input model to specify contract address, block range, and other parameters.

#### Model Template:

```json
{
    "contract_addr": "Address of the EVM contract that emits the events to be extracted",
    "start_block": "Start block number for data extraction",
    "end_block": "End block number for data extraction",
    "function_sig": "Function signature from the smart contract",
    "filters": "Criteria to filter events based on indexed parameters",
    "decimals": "Optional: Formatting for integer values as decimals"
}
```

See further details on the [model template](https://github.com/sjuanati/demonic-tutor/blob/main/src/models/default_event.info.py)

<details>
<summary> Example: </summary>

Input Model: (in /src/models/default_event.json)

```json
{
    "contract_addr": "0xc53b9b1d3dd035259c6d414b5e790755bca5f667",
    "start_block": 17677590,
    "end_block": 17677600,
    "function_sig": "ModuleAdded (uint8[] _types, index_topic_1 bytes32 _name, index_topic_2 address _moduleFactory, address _module, uint256 _moduleCost, uint256 _budget, bytes32 _label, bool _archived)",
    "filters": {
        "_name": null,
        "_moduleFactory": "0x5fafcfc0afd80d2f95133170172b045024ca8fd1"
    },
    "decimals": {
        "_types": 0,
        "_name": null,
        "_moduleFactory": null,
        "_module": null,
        "_moduleCost": 0,
        "_budget": 18,
        "_label": null,
        "_archived": null 
    }
}
```

Output Data:

```json
[
    {
        "txn_hash": "0xcd793c8125bcedae28b0862b283ddcae371ced8488ae2a6f975a68baef98c082",
        "block_num": 17677591,
        "_name": "47656e6572616c5472616e736665724d616e6167657200000000000000000000",
        "_moduleFactory": "0x5fafcfc0afd80d2f95133170172b045024ca8fd1",
        "_types": [2, 6],
        "_module": "0xfd326f612997251c736f781b38392fc86aa8243a",
        "_moduleCost": 0,
        "_moduleBudget": 0.0,
        "_label": "0000000000000000000000000000000000000000000000000000000000000000",
        "_archived": false
    }
]
```

Output CSV file: (in /src/data/default_event.csv)

```csv
txn_hash,block_num,_name,_moduleFactory,_types,_module,_moduleCost,_budget,_label,_archived
0xcd793c8125bcedae28b0862b283ddcae371ced8488ae2a6f975a68baef98c082,17677591,47656e6572616c5472616e736665724d616e6167657200000000000000000000,0x5fafcfc0afd80d2f95133170172b045024ca8fd1,"[2, 6]",0xfd326f612997251c736f781b38392fc86aa8243a,0,0.0,0000000000000000000000000000000000000000000000000000000000000000,False

```
</details>

### Contract Call Data Retrieval

Demonic Tutor enables users to execute contract calls to retrieve data at any specified block number. This functionality is crucial for analyzing the state and interactions of smart contracts at specific points in the blockchain's history.

For performing contract calls, choose option `4` from the main menu. Provide the necessary input model to specify contract address, block number, and function arguments.

#### Model Template:

```json
{
    "contract_addr": "Mandatory: Address of the EVM contract to retrieve data from",
    "block": "Optional: Block number at which the data retrieval is targeted",
    "function_name": "Mandatory: Exact name of the contract function to be called",
    "arguments": "Mandatory: Arguments to pass to the function",
    "arg_types": "Mandatory: Types of the function arguments",
    "output_decimals": "Optional: Decimal formatting for numeric outputs",
    "abi": "Contract's ABI containing the function to be called"
}
```

See further details on the [model template](https://github.com/sjuanati/demonic-tutor/blob/main/src/models/default_call.info.py)

<details>
<summary>Example:</summary>

Input Model: (in /src/models/default_call.json)

```json
{
    "contract_addr": "0x19A07afE97279cb6de1c9E73A13B7b0b63F7E67A",
    "block": 18564560,
    "function_name": "pnlDistribution",
    "arguments": {},
    "arg_types": {},
    "output_decimals": {
        "newTrancheBalances": 18,
        "profit": 18,
        "loss": 18
    },
    "abi": [ ... ]
}
```

Outut data:

```json
{
    "newTrancheBalances": [
        576818.9599763307,
        2498269.4616636974
    ],
    "profit": 14.780158785013175,
    "loss": 0
}
```
</details>

## Pending Updates

- **Installation Instructions**: Step-by-step instructions will be provided to help new users set up and start using Demonic Tutor seamlessly.

- **Testing Procedures**: Detailed information on how to run tests to ensure the app is functioning correctly on your local setup.