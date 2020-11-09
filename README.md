## General Data Types


### Calculating 

#### Fees

`,timestamp,name,action,price,balance,share_price,fee,mgmt,perf`

### Contracts

see `contract-addresses/` for `.json` and `.csv`

### Data Percision 

#### GraphQL / Javascript

The limited precision of numbers in JavaScript is Number.MAX_SAFE_INTEGER nanoseconds is about 104 days

```js
// uint32 (two's complement) max
// more conservative than Number.MAX_SAFE_INTEGER
const MAX = 4294967295
```
> source: https://github.com/metamask/json-rpc-engine/blob/5001c0dc013dba0f11f64847f66bfbbbcf9b92bb/src/getUniqueId.js#L3


### Exchange

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| data | object | The trade data corresponding to the columns fields\. |
| \[EXCHANGE\] | array | The array containing arrays of trade data\. |
| metadata | object | The metadata associated with the trade data\. |
| columns | array | The name of the columns associated with the returned data e\.g\. \[ timestamp, tradeId, \.\.\.\]\. |
| timestamp | number | The time at which the data was recorded\. |
| nanoseconds | number | The nanosecond part of the timestamp where applicable\. |
| tradeId | number | The exchange provided id of the trade\. |
| price | number | The price at which the asset was traded\. |
| volume | number | The total amount of that asset that was traded\. |
| isBuy | bool | true if the trade is a buy, false otherwise\. |

### Time

| **Text Date:Date in human\-readable text** | **Saturday, January 3, 2009 6:15:05 PM** |
| ------------------------------------------ | ---------------------------------------- |
| RFC 822:RFC 822 formatted date             | Sat, 03 Jan 2009 18:15:05 \+0000         |
| ISO 8601:ISO 8601 formatted date           | 2009\-01\-03T18:15:05\+00:00             |
| UNIX Timestamp:seconds since Jan 1 1970    | 1231006505                               |
| Mac Timestamp:seconds since Jan 1 1904     | 3313851305                               |
| Microsoft Timestamp:days since Dec 31 1899 | 39816\.76047                             |
| FILETIME:100\-nanoseconds since Jan 1 1601 | 12875480105000000001C96DCF:33B61A80      |

### Contract Addresses

> Checksum'd (EIP55)

Incorrect: `0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e`

Correct: `0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e`

### Times

milliseconds 1604403060000

seconds 1604403060

> `gdate` is simply `GNU UTILS` on Mac OS X - for GNU/Linux its just 'date'

\$ gdate --iso-8601 2020-11-03

\$ gdate --iso-8601=seconds 2020-11-03T03:40:42-08:00

\$ date Tue Nov 3 03:41:07 PST 2020

\$ date -u Tue Nov 3 11:41:10 UTC 2020


## Data Analysis 

> as defined in 'structs.py'

#### RoiInfo

        dm_change: float = dm_change
        eth_balance: int = eth_balance
        token_balance: int = token_balance
        trade_volume: int = trade_volume

#### ExchangeInfo

        token_address: str,
        token_name: str,
        token_symbol: str,
        token_decimals: int,
        exchange_address: str,
        eth_balance: int,
        token_balance: int,

        token_address: str = token_address
        token_name: str = token_name
        token_symbol: str = token_symbol
        token_decimals: int = token_decimals
        exchange_address: str = exchange_address
        eth_balance: int = eth_balance
        token_balance: int = token_balance
        providers: Dict[str, int] = dict()
        history: List[int] = list()
        logs: List[dict] = list()
        roi: List[RoiInfo] = list()
        volume: List[Dict[str, int]] = list()
        valuable_traders: List[str] = list()

#### History

        block_number: int,
        dm_change: float,
        bnt_balance: int,
        token_balance: int,
        trade_volume: int,


        block_number: int = block_number
        dm_change: float = dm_change
        bnt_balance: int = bnt_balance
        token_balance: int = token_balance
        trade_volume: int = trade_volume


#### RelayInfo:

        token_address: str = token_address
        token_symbol: str = token_symbol
        underlying_token_symbol: str = None
        converter_address: str = converter_address
        bnt_balance: int = 0
        token_decimals: int = None
        token_balance: int = 0
        providers: Dict[str, int] = dict()
        history: List[History] = list()
        converter_logs: List[dict] = list()
        relay_logs: List[dict] = list()




#### Market Data

```json
{
  "status": 200,
  "title": "OK",
  "description": "Successful request",
  "payload": {
    "metadata": {
      "startDate": "2020-07-25T00:00:00.000Z",
      "endDate": "2020-07-26T00:00:00.000Z"
    },
    "data": [
      {
        "exchange": "binance",
        "timestamp": "2020-07-25T00:00:00.000Z",
        "open": 3.0294,
        "high": 3.0331,
        "low": 3.0271,
        "close": 3.0331,
        "volume": 600.27
      },
      {...}
    ]
  }
}
```

## License

SPDX-License-Identifier: ISC
