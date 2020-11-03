"""Module that reads batch auction data from smart contract."""
from typing import Dict, List
from web3 import Web3
from decimal import Decimal
import logging

# Set smart contract info.
abi = '[{"constant":true,"inputs":[],"name":"IMPROVEMENT_DENOMINATOR","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getSecondsRemainingInBatch","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getEncodedOrders","outputs":[{"name":"elements","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"buyToken","type":"uint16"},{"name":"sellToken","type":"uint16"},{"name":"validUntil","type":"uint32"},{"name":"buyAmount","type":"uint128"},{"name":"sellAmount","type":"uint128"}],"name":"placeOrder","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"batchId","type":"uint32"},{"name":"claimedObjectiveValue","type":"uint256"},{"name":"owners","type":"address[]"},{"name":"orderIds","type":"uint16[]"},{"name":"buyVolumes","type":"uint128[]"},{"name":"prices","type":"uint128[]"},{"name":"tokenIdsForPrice","type":"uint16[]"}],"name":"submitSolution","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"id","type":"uint16"}],"name":"tokenIdToAddressMap","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"name":"requestWithdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"FEE_FOR_LISTING_TOKEN_IN_OWL","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"previousPageUser","type":"address"},{"name":"pageSize","type":"uint16"}],"name":"getUsersPaginated","outputs":[{"name":"users","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"name":"deposit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"orderIds","type":"uint16[]"}],"name":"cancelOrders","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"AMOUNT_MINIMUM","outputs":[{"name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToken","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"buyTokens","type":"uint16[]"},{"name":"sellTokens","type":"uint16[]"},{"name":"validFroms","type":"uint32[]"},{"name":"validUntils","type":"uint32[]"},{"name":"buyAmounts","type":"uint128[]"},{"name":"sellAmounts","type":"uint128[]"}],"name":"placeValidFromOrders","outputs":[{"name":"orderIds","type":"uint16[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint16"}],"name":"currentPrices","outputs":[{"name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"user","type":"address"}],"name":"getEncodedUserOrders","outputs":[{"name":"elements","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"uint256"}],"name":"orders","outputs":[{"name":"buyToken","type":"uint16"},{"name":"sellToken","type":"uint16"},{"name":"validFrom","type":"uint32"},{"name":"validUntil","type":"uint32"},{"name":"priceNumerator","type":"uint128"},{"name":"priceDenominator","type":"uint128"},{"name":"usedAmount","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"UNLIMITED_ORDER_AMOUNT","outputs":[{"name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"numTokens","outputs":[{"name":"","type":"uint16"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"lastCreditBatchId","outputs":[{"name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"previousPageUser","type":"address"},{"name":"previousPageUserOffset","type":"uint16"},{"name":"pageSize","type":"uint16"}],"name":"getEncodedUsersPaginated","outputs":[{"name":"elements","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"addr","type":"address"}],"name":"hasToken","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"latestSolution","outputs":[{"name":"batchId","type":"uint32"},{"name":"solutionSubmitter","type":"address"},{"name":"feeReward","type":"uint256"},{"name":"objectiveValue","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"getPendingDeposit","outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cancellations","type":"uint16[]"},{"name":"buyTokens","type":"uint16[]"},{"name":"sellTokens","type":"uint16[]"},{"name":"validFroms","type":"uint32[]"},{"name":"validUntils","type":"uint32[]"},{"name":"buyAmounts","type":"uint128[]"},{"name":"sellAmounts","type":"uint128[]"}],"name":"replaceOrders","outputs":[{"name":"","type":"uint16[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"getPendingWithdraw","outputs":[{"name":"","type":"uint256"},{"name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"batchId","type":"uint32"}],"name":"acceptingSolutions","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"}],"name":"addToken","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"FEE_DENOMINATOR","outputs":[{"name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"ENCODED_AUCTION_ELEMENT_WIDTH","outputs":[{"name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"BATCH_TIME","outputs":[{"name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getCurrentBatchId","outputs":[{"name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"offset","type":"uint16"},{"name":"pageSize","type":"uint16"}],"name":"getEncodedUserOrdersPaginated","outputs":[{"name":"elements","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"addr","type":"address"}],"name":"tokenAddressToIdMap","outputs":[{"name":"","type":"uint16"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"},{"name":"batchId","type":"uint32"}],"name":"requestFutureWithdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"hasValidWithdrawRequest","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MAX_TOKENS","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"user","type":"address"},{"name":"token","type":"address"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"MAX_TOUCHED_ORDERS","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getCurrentObjectiveValue","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"maxTokens","type":"uint256"},{"name":"_feeToken","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":false,"name":"index","type":"uint16"},{"indexed":true,"name":"buyToken","type":"uint16"},{"indexed":true,"name":"sellToken","type":"uint16"},{"indexed":false,"name":"validFrom","type":"uint32"},{"indexed":false,"name":"validUntil","type":"uint32"},{"indexed":false,"name":"priceNumerator","type":"uint128"},{"indexed":false,"name":"priceDenominator","type":"uint128"}],"name":"OrderPlacement","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"token","type":"address"},{"indexed":false,"name":"id","type":"uint16"}],"name":"TokenListing","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":false,"name":"id","type":"uint16"}],"name":"OrderCancellation","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":false,"name":"id","type":"uint16"}],"name":"OrderDeletion","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"orderId","type":"uint16"},{"indexed":true,"name":"sellToken","type":"uint16"},{"indexed":false,"name":"buyToken","type":"uint16"},{"indexed":false,"name":"executedSellAmount","type":"uint128"},{"indexed":false,"name":"executedBuyAmount","type":"uint128"}],"name":"Trade","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"orderId","type":"uint16"},{"indexed":true,"name":"sellToken","type":"uint16"},{"indexed":false,"name":"buyToken","type":"uint16"},{"indexed":false,"name":"executedSellAmount","type":"uint128"},{"indexed":false,"name":"executedBuyAmount","type":"uint128"}],"name":"TradeReversion","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"submitter","type":"address"},{"indexed":false,"name":"utility","type":"uint256"},{"indexed":false,"name":"disregardedUtility","type":"uint256"},{"indexed":false,"name":"burntFees","type":"uint256"},{"indexed":false,"name":"lastAuctionBurntFees","type":"uint256"},{"indexed":false,"name":"prices","type":"uint128[]"},{"indexed":false,"name":"tokenIdsForPrice","type":"uint16[]"}],"name":"SolutionSubmission","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"user","type":"address"},{"indexed":true,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"batchId","type":"uint32"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"user","type":"address"},{"indexed":true,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"batchId","type":"uint32"}],"name":"WithdrawRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"user","type":"address"},{"indexed":true,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"Withdraw","type":"event"}]'


class ContractReader:

    def __init__(self, network="mainnet"):
        # Specify Infura credentials
        node_url = ("https://" + network +
                    ".infura.io/v3/9408f47dedf04716a03ef994182cf150")
        addresses = {
            "mainnet": "0x6F400810b62df8E13fded51bE75fF5393eaa841F",
            "rinkeby": "0xC576eA7bd102F7E476368a5E98FA455d1Ea34dE2",
        }
        web3 = Web3(Web3.HTTPProvider(node_url))
        self.contract = web3.eth.contract(address=addresses[network], abi=abi)

    def get_current_batch_id(self):
        """Get ID of current batch."""
        return self.contract.functions.getCurrentBatchId().call()

    def get_current_orderbook(self):
        """Get all currently valid orders from smart contract.

        Returns:
            A list of all orders.

        """
        orders = self.get_orderbook()

        # Skip orders that are no longer or not yet valid.
        batch_id = self.get_current_batch_id()
        orders = list(
            filter(
                lambda order: order["validUntil"] >= batch_id and order[
                    "validFrom"] <= batch_id,
                orders,
            ))
        return orders

    def get_orderbook(self):
        """Get all order data from smart contract.

        Returns:
            A list of all orders.

        """
        orders_raw = []

        # Get orders via paginated approach.
        page_size = 100
        current_user = "0x0000000000000000000000000000000000000000"
        current_offset = 0
        last_page_size = page_size

        # Read unprocessed order data.
        while last_page_size == page_size:

            orders_decoded_raw = decode_orders(
                self.contract.functions.getEncodedUsersPaginated(
                    Web3.toChecksumAddress(current_user), current_offset,
                    page_size).call())

            orders_raw += orders_decoded_raw
            if len(orders_decoded_raw) > 0:
                current_user = orders_decoded_raw[-1]["accountID"]
                current_offset = len(
                    [o for o in orders_raw if o["accountID"] == current_user])

            last_page_size = len(orders_decoded_raw)

        # Process order data.
        orders = []
        for o in orders_raw:

            # Set token names.
            sell_token = "T%04d" % o["sellToken"]
            buy_token = "T%04d" % o["buyToken"]

            # Get sell amount.
            sell_amount = Decimal(
                min(o["remainingAmount"], o["sellTokenBalance"]))
            if sell_amount == 0:
                continue

            # Compute buy amount from sell amount and limit price.
            limit_price = Decimal(o["priceNumerator"]) / Decimal(
                o["priceDenominator"])
            if limit_price == 0:
                buy_amount = 1
            else:
                buy_amount = (sell_amount * limit_price).to_integral_value()

            logging.debug(
                "Read order: sellAmount %40d %7s -- buyAmount %40d %7s -- accountID %s"
                % (sell_amount, sell_token, buy_amount, buy_token,
                   o["accountID"]))

            orders.append({
                "accountID": o["accountID"],
                "sellToken": sell_token,
                "buyToken": buy_token,
                "sellAmount": str(int(sell_amount)),
                "buyAmount": str(int(buy_amount)),
                "validFrom": o["validFrom"],
                "validUntil": o["validUntil"],
            })

        return orders

    def get_account_balances(self, tokens: List[str],
                             orders: List[Dict]) -> Dict[str, Dict[str, str]]:
        """Get account balances of the sell tokens of all orders.

        Args:
            tokens: List of tokens with their JSON name (i.e., 'token0' etc.)
            orders: List of extracted orders.

        Returns:
            A dict of the account balances.

        """
        # Get token adresses first.
        token_adresses = {}
        for t in tokens:
            tID = int(t.replace("T", ""))
            token_adresses[t] = self.contract.functions.tokenIdToAddressMap(
                tID).call()

        # Read account balances.
        accounts = {}

        for o in orders:
            tS = o["sellToken"]
            aID = o["accountID"]

            if aID not in accounts:
                accounts[aID] = {}

            if tS not in accounts[aID]:
                accounts[aID][tS] = str(
                    self.contract.functions.getBalance(
                        Web3.toChecksumAddress(aID), token_adresses[tS]).call())

        return accounts


def decode_orders(orders_encoded):
    """Decode order byte string into list of orders."""
    orders_decoded = []

    # Iterate over order byte strings (one order = 112 bytes).
    for order_bytes in [
            orders_encoded[k:k + 112]
            for k in range(0, len(orders_encoded), 112)
    ]:

        orders_decoded.append(_read_order_from_bytes(order_bytes))

    return orders_decoded


def _read_order_from_bytes(order_bytes) -> Dict[str, str]:
    """Decode order information from bytes.

    Each order is encoded as 112 bytes:
    -- 20 bytes for accountID
    -- 32 bytes for account balance of the sellToken
    --  2 bytes for buyToken
    --  2 bytes for sellToken
    --  4 bytes for validFrom
    --  4 bytes for validUntil
    -- 16 bytes for priceNumerator
    -- 16 bytes for priceDenominator
    -- 16 bytes for remainingAmount (i.e., sellAmount)

    Returns:
        A dict containing the order information.

    """
    assert len(order_bytes) == 112

    encoding_nr_bytes = {
        "accountID": 20,
        "sellTokenBalance": 32,
        "buyToken": 2,
        "sellToken": 2,
        "validFrom": 4,
        "validUntil": 4,
        "priceNumerator": 16,
        "priceDenominator": 16,
        "remainingAmount": 16,
    }

    order = {}
    i = 0
    for attr, n in encoding_nr_bytes.items():

        _bytes = order_bytes[i:i + n]

        if attr == "accountID":
            order[attr] = "0x" + _bytes.hex()
        else:
            order[attr] = int.from_bytes(_bytes, "big")

        i += n

    return order
