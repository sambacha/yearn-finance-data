> as defined in 'structs.py'

### RoiInfo

        dm_change: float = dm_change
        eth_balance: int = eth_balance
        token_balance: int = token_balance
        trade_volume: int = trade_volume

### ExchangeInfo

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

### History

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


### RelayInfo:

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
