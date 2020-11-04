"""
File containing token names and decimals.

The list is hardcoded as a fallback and can be overwritten via the update() method.
"""

TOKENS = {
    "T0000": {"alias": "OWL", "decimals": 18},
    "T0001": {"alias": "WETH", "decimals": 18},
    "T0002": {"alias": "USDT", "decimals": 6},
    "T0003": {"alias": "TUSD", "decimals": 18},
    "T0004": {"alias": "USDC", "decimals": 6},
    "T0005": {"alias": "PAX", "decimals": 18},
    "T0006": {"alias": "GUSD", "decimals": 2},
    "T0007": {"alias": "DAI", "decimals": 18},
    "T0008": {"alias": "sETH", "decimals": 18},
    "T0009": {"alias": "sUSD", "decimals": 18},
    "T0010": {"alias": "sBTC", "decimals": 18},
    "T0011": {"alias": "WBTC", "decimals": 8},
    "T0012": {"alias": "SAI", "decimals": 18},
    "T0013": {"alias": "cDAI", "decimals": 8},
    "T0014": {"alias": "aDAI", "decimals": 18},
    "T0015": {"alias": "SNX", "decimals": 18},
    "T0016": {"alias": "CHAI", "decimals": 18},
    "T0017": {"alias": "PAXG", "decimals": 18},
    "T0018": {"alias": "GNO", "decimals": 18},
    "T0019": {"alias": "PAN", "decimals": 18},
    "T0020": {"alias": "GEN", "decimals": 18},
    "T0021": {"alias": "oETH", "decimals": 8},
    "T0022": {"alias": "GRID", "decimals": 12},
    "T0023": {"alias": "MKR", "decimals": 18},
    "T0024": {"alias": "LINK", "decimals": 18},
    "T0025": {"alias": "TAU", "decimals": 18},
    "T0026": {"alias": "SNGLS", "decimals": 0},
    "T0027": {"alias": "DZAR", "decimals": 6},
    "T0028": {"alias": "BiLira", "decimals": 6},
    "T0029": {"alias": "RPL", "decimals": 18},
    "T0030": {"alias": "PARETO", "decimals": 18},
    "T0031": {"alias": "aUSDC", "decimals": 6},
    "T0032": {"alias": "aSUSD", "decimals": 18},
    "T0033": {"alias": "aTUSD", "decimals": 18},
    "T0034": {"alias": "aUSDT", "decimals": 6},
    "T0035": {"alias": "aETH", "decimals": 18},
    "T0036": {"alias": "aBAT", "decimals": 18},
    "T0037": {"alias": "aKNC", "decimals": 18},
    "T0038": {"alias": "aLEND", "decimals": 18},
    "T0039": {"alias": "aLINK", "decimals": 18},
    "T0040": {"alias": "aMANA", "decimals": 18},
    "T0041": {"alias": "aMKR", "decimals": 18},
    "T0042": {"alias": "aSNX", "decimals": 18},
    "T0043": {"alias": "BAT", "decimals": 18},
    "T0044": {"alias": "BTU", "decimals": 18},
    "T0045": {"alias": "bDAI", "decimals": 18},
    "T0046": {"alias": "ANT", "decimals": 18},
    "T0047": {"alias": "SPL", "decimals": 18},
    "T0048": {"alias": "UMA", "decimals": 18},
    "T0049": {"alias": "sEUR", "decimals": 18},
    "T0050": {"alias": "XRT", "decimals": 9},
    "T0051": {"alias": "DXD", "decimals": 18},
    "T0052": {
        "alias": "oETH $200 Put 05/29/20",
        "decimals": 7,
    },
    "T0053": {"alias": "ocDAI", "decimals": 8},
    "T0054": {"alias": "ocUSDC", "decimals": 8},
    "T0055": {"alias": "oETH", "decimals": 7},
    "T0056": {"alias": "NOIA", "decimals": 18},
    "T0057": {"alias": "TLN", "decimals": 18},
    "T0058": {"alias": "UAX", "decimals": 2},
    "T0059": {"alias": "DMG", "decimals": 18},
    "T0060": {"alias": "STA", "decimals": 18},
    "T0061": {"alias": "thrm", "decimals": 18},
    "T0062": {"alias": "PNK", "decimals": 18},
    "T0063": {"alias": "BITS", "decimals": 8},
    "T0072": {
        "alias": "MTA",
        "decimals": 18,
    },
    "T0073": {
        "alias": "mUSD",
        "decimals": 18,
    },
    "T0079": {"alias": "DIA", "decimals": 18},
}


def update(tokens):
    """Update global to TOKENS variable."""
    global TOKENS

    for token_id in tokens:

        if token_id not in TOKENS:
            TOKENS[token_id] = {}

        if isinstance(tokens, dict):
            token_info = tokens[token_id]
            if token_info is None:
                token_info = {}

            alias = token_info.get("alias")
            if alias is not None:
                TOKENS[token_id]["alias"] = alias

            decimals = token_info.get("decimals")
            if decimals is not None:
                TOKENS[token_id]["decimals"] = decimals
