#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Plot orderbook for pair of given tokens.

Example call:
> python plot_orderbook_tokenpair.py data/kraken_input.json USD XBT
> python plot_orderbook_tokenpair.py data/dfusion_input.json TUSD PAX
"""
import os
import argparse
import logging
from typing import List, Dict
from decimal import Decimal
import numpy as np

from plot_utils import plot_orderbook
from contract_reader import ContractReader
import util
import TokenInfo


def generate_plot(
    t1: str,
    t2: str,
    orders: List[Dict],
    output_dir: str = "./",
    ipython: bool = False,
    **kwargs
):
    """Generate a token-order-graph plot using plotly.

    Args:
        t1: ID of token 1.
        t2: ID of token 2.
        orders: List of orders.

    Kwargs:
        output_dir: Location for storing the plot.
        ipython: Running from IPython environment, or not.

    """
    # Init dicts for cumulated order data for given tokens.
    total_amounts = {t1: Decimal(0), t2: Decimal(0)}
    sell_limits_amounts = {t1: [], t2: []}

    for o in orders:
        tS, tB = o["sellToken"], o["buyToken"]
        if set([tS, tB]) != set([t1, t2]):
            continue

        # Get amounts scaled to human-readable values.
        sell_amount = Decimal(o["sellAmount"]) / Decimal(
            10 ** util.get_token_decimals(tS)
        )
        buy_amount = Decimal(o["buyAmount"]) / Decimal(
            10 ** util.get_token_decimals(tB)
        )
        if buy_amount != 0:
            total_amounts[tB] += buy_amount
            total_amounts[tS] += sell_amount

            sell_limits_amounts[tS].append((sell_amount / buy_amount, sell_amount))

    # Skip, if no orders for given token pair.
    if len(sell_limits_amounts) == 0:
        logging.warning("No orders given for token pair %s <> %s!" % (t1, t2))
        return

    # Estimate exchange rate from order data.
    if total_amounts[t2] == 0:
        estimated_xrate = 1
    else:
        estimated_xrate = total_amounts[t1] / total_amounts[t2]

    # Generate exchange rate sample points.
    xrate_LB = float(estimated_xrate / Decimal("1.5"))
    xrate_UB = float(estimated_xrate * Decimal("1.5"))

    # Add fees to the orderbook.
    fee_percentage = Decimal("0.001")
    fee_multiplier = 1 + fee_percentage

    # No optimization: Plot over linear space
    # xrates = np.linspace(xrate_LB, xrate_UB, 1000)

    # Optimization: Plot points only around the corners
    eps_corner = (xrate_UB - xrate_LB) / 10000

    def corner(f):
        return [f - eps_corner, f, f + eps_corner]

    xrates = np.clip(
        sum([corner(float(s[0] / fee_multiplier)) for s in sell_limits_amounts[t1]], [])
        + sum(
            [corner(float(fee_multiplier / s[0])) for s in sell_limits_amounts[t2]], []
        ),
        xrate_LB,
        xrate_UB,
    )
    # Add some extra points (otherwise there would be only straight lines) and
    # make sure endpoints are included.
    xrates = np.union1d(xrates, np.linspace(xrate_LB, xrate_UB, 100))

    # Get token names, if available.
    t1_name = util.get_token_name(t1)
    t2_name = util.get_token_name(t2)

    # Compute cumulated sell/buy amounts on token pair per xrate sample point.
    cumulated_sell_amounts = {t: np.zeros(len(xrates)) for t in [t1_name, t2_name]}

    for (limit, sell_amount) in sell_limits_amounts[t1]:
        _executable = np.where(xrates <= limit / fee_multiplier, 1, 0)
        cumulated_sell_amounts[t1_name] += float(sell_amount) * _executable

    for (limit, sell_amount) in sell_limits_amounts[t2]:
        _executable = np.where(xrates >= fee_multiplier * (1 / limit), 1, 0)
        cumulated_sell_amounts[t2_name] += float(sell_amount) * _executable

    cumulated_buy_amounts = {
        t1_name: cumulated_sell_amounts[t2_name] * xrates,
        t2_name: cumulated_sell_amounts[t1_name] / xrates,
    }

    # Plot.
    plot_orderbook(
        t1_name,
        t2_name,
        xrates,
        cumulated_sell_amounts,
        cumulated_buy_amounts,
        plot_title="orderbook-%s-%s" % (t1_name, t2_name),
        output_dir=output_dir,
        ipython=ipython,
        **kwargs
    )

    return


if __name__ == "__main__":
    """Main function."""

    util.configure_logger(logging.INFO)

    # Process command line arguments.
    parser = argparse.ArgumentParser(
        description="Input file and output directory parser."
    )

    parser.add_argument("t1", type=str, help="The name of the first token.")

    parser.add_argument("t2", type=str, help="The name of the second token.")

    parser.add_argument(
        "--jsonFile",
        type=str,
        help="A JSON input file containing a batch auction instance.",
    )

    parser.add_argument(
        "--show",
        dest="show",
        action="store_true",
        help="Show the output picture in the browser.",
    )

    parser.add_argument(
        "--network",
        type=str,
        choices=["mainnet", "rinkeby"],
        default="mainnet",
        help="Choose one network (mainnet or rinkeby)",
    )

    parser.add_argument(
        "--no-show",
        dest="show",
        action="store_false",
        help="Do not show the output picture in the browser.",
    )

    parser.set_defaults(show=True)

    args = parser.parse_args()

    if args.jsonFile is not None:
        # Read input JSON.
        assert os.path.isfile(args.jsonFile)
        output_dir = os.path.dirname(args.jsonFile)
        inst = util.read_instance_from_file(args.jsonFile)
    else:
        # Get instance from blockchain.
        output_dir = "./"
        contract_reader = ContractReader(args.network)
        inst = util.read_instance_from_blockchain(contract_reader)

    TokenInfo.update(inst["tokens"])

    # Get token IDs.
    t1 = util.get_token_ID(args.t1)
    t2 = util.get_token_ID(args.t2)
    orders = [o for o in inst["orders"] if {t1, t2} == {o["sellToken"], o["buyToken"]}]
    logging.info("=== ORDERS (%d) ===" % len(orders))
    util.log_orders(orders)

    # Plot.
    generate_plot(t1, t2, orders, output_dir, auto_open=args.show)
