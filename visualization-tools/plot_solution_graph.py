#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Plot graph of tokens and orders.

Example call:
> python plot_solution_graph.py data/kraken_solution.json
"""
import os
import argparse
import logging
from typing import List, Dict
from decimal import Decimal

from plot_utils import plot_network
import util
from util import EDGE_TYPE, NODE_TYPE
import TokenInfo


def generate_plot(tokens: List[NODE_TYPE],
                  nr_exec_orders_tokenpair: Dict[EDGE_TYPE, int],
                  token_prices: Dict[NODE_TYPE, Decimal],
                  token_amounts_sold: Dict[NODE_TYPE, Decimal],
                  token_amounts_bought: Dict[NODE_TYPE, Decimal],
                  tokenpair_amounts_sold: Dict[EDGE_TYPE, Decimal],
                  tokenpair_amounts_bought: Dict[EDGE_TYPE, Decimal],
                  output_dir: str = "./",
                  ipython: bool = False,
                  **kwargs):
    """Generate a token-order-graph plot using plotly.

    Args:
        tokens: List of token names.
        nr_orders_tokenpair: Dict of token pairs => number of orders.
        nr_exec_orders_tokenpair: Dict of token pairs => number of executed orders.
        token_prices: Dict of tokens => token price.
        token_amounts_sold: Dict of tokens => amount of token sold.
        token_amounts_bought: Dict of tokens => amount of token bought.
        tokenpair_amounts_sold: Dict of token pairs => amount of tokens sold.
        tokenpair_amounts_bought: Dict of token pairs => amount of tokens bought.

    Kwargs:
        output_dir: Location for storing the plot.
        ipython: Running from IPython environment, or not.

    """
    # Extract set of tokens and token pairs.
    tokenpairs = nr_exec_orders_tokenpair.keys()

    trading_volume_tokens = {
        t: (token_amounts_sold.get(t, 0) * token_prices.get(t, 0) +
            token_amounts_bought.get(t, 0) * token_prices.get(t, 0))
        for t in tokens
    }

    trading_volume_tokenpairs = {(t1, t2):
                                 (tokenpair_amounts_sold.get(
                                     (t1, t2), 0) * token_prices.get(t1, 0) +
                                  tokenpair_amounts_bought.get(
                                      (t1, t2), 0) * token_prices.get(t1, 0) +
                                  tokenpair_amounts_bought.get(
                                      (t2, t1), 0) * token_prices.get(t2, 0) +
                                  tokenpair_amounts_bought.get(
                                      (t2, t1), 0) * token_prices.get(t2, 0))
                                 for t1, t2 in tokenpairs}

    xrates = {(t1, t2): token_prices[t1] / token_prices[t2] for t1 in tokens
              for t2 in tokens
              if token_prices.get(t1, 0) > 0 and token_prices.get(t2, 0) > 0 and
              t1 != t2}

    # Set plot attributes.
    node_weights = trading_volume_tokens

    node_labels = {t: t for t in tokens}

    node_hovers = {
        t: "=== %s ===<br>clearing price : %s<br>sold : %s<br>bought : %s" % (
            t,
            util.decimal_to_str(token_prices.get(t)),
            util.decimal_to_str(token_amounts_sold.get(t)),
            util.decimal_to_str(token_amounts_bought.get(t)),
        ) for t in tokens
    }

    edge_weights = {
        tp: v for (tp, v) in trading_volume_tokenpairs.items() if v > 0
    }

    edge_hovers = {(t1, t2): "=== %s/%s ===<br>"
                   "exchange rate : %s %s/%s <> %s %s/%s<br>"
                   "orders executed : %d<br>"
                   "# %s sold : %s<br># %s bought : %s<br>"
                   "# %s sold : %s<br># %s bought : %s" % (
                       t1,
                       t2,
                       util.decimal_to_str(xrates.get((t1, t2))),
                       t2,
                       t1,
                       util.decimal_to_str(xrates.get((t2, t1))),
                       t1,
                       t2,
                       (nr_exec_orders_tokenpair.get(
                           (t1, t2), 0) + nr_exec_orders_tokenpair.get(
                               (t2, t1), 0)),
                       t1,
                       util.decimal_to_str(
                           tokenpair_amounts_sold.get((t1, t2), Decimal("0"))),
                       t1,
                       util.decimal_to_str(
                           tokenpair_amounts_bought.get(
                               (t1, t2), Decimal("0"))),
                       t2,
                       util.decimal_to_str(
                           tokenpair_amounts_sold.get((t2, t1), Decimal("0"))),
                       t2,
                       util.decimal_to_str(
                           tokenpair_amounts_bought.get(
                               (t2, t1), Decimal("0"))),
                   ) for (t1, t2) in tokenpairs}

    # Plot.
    plot_network(nodes=tokens,
                 edges=list(edge_weights.keys()),
                 node_weights=node_weights,
                 node_labels=node_labels,
                 node_hovers=node_hovers,
                 edge_weights=edge_weights,
                 edge_hovers=edge_hovers,
                 plot_title="solution-graph",
                 output_dir=output_dir,
                 ipython=ipython,
                 **kwargs)

    return


if __name__ == "__main__":
    """Main function."""

    # Process command line arguments.
    parser = argparse.ArgumentParser(
        description="Input file and output directory parser.")

    parser.add_argument(
        "jsonFile",
        type=str,
        help="A JSON input file containing a batch auction instance.",
    )

    parser.add_argument(
        "--price",
        type=str,
        help="A token name used for denomination of the prices.")

    parser.add_argument(
        "--logging",
        type=str.upper,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level.",
    )

    args = parser.parse_args()

    util.configure_logger(getattr(logging, args.logging))

    assert os.path.isfile(args.jsonFile)
    output_dir = os.path.dirname(args.jsonFile)

    # Read input JSON.
    inst = util.read_instance_from_file(args.jsonFile)

    TokenInfo.update(inst["tokens"])

    # Get token prices (denominated in token specified).
    assert "prices" in inst
    token_prices = util.get_token_prices(inst["prices"])

    # Get list of tokens.
    tokens = token_prices.keys()

    if args.price is not None:
        p_ref = token_prices.get(args.price, Decimal(1))
        token_prices = {t: p / p_ref for t, p in token_prices.items()}

    # Get number of orders per token pair.
    assert "orders" in inst
    nr_orders_tokenpair = util.get_nr_orders_tokenpair(inst["orders"])
    traded_amounts = util.get_total_traded_amounts(inst["orders"])

    # Get traded amounts.
    token_amounts_sold = traded_amounts[0]
    token_amounts_bought = traded_amounts[1]
    tokenpair_amounts_sold = traded_amounts[2]
    tokenpair_amounts_bought = traded_amounts[3]
    nr_exec_orders_tokenpair = traded_amounts[4]

    logging.info("=== TOKEN PRICES ===")
    for t, p in token_prices.items():
        logging.info("%5s : %14s" %
                     (t, util.decimal_to_str(token_prices.get(t))))

    logging.info("=== EXECUTED ORDERS ===")
    for idx, o in enumerate(inst["orders"]):
        if o["execSellAmount"] > 0:
            tS, tB = o["sellToken"], o["buyToken"]
            aID = o.get("accountID", "")
            xS_exec = util.get_order_amount_scaled(o["execSellAmount"], tS)
            xB_exec = util.get_order_amount_scaled(o["execBuyAmount"], tB)
            logging.info("%5d : <%6s>  sold  %14s  %-5s  for  %14s  %-5s" % (
                idx,
                aID[:6],
                util.decimal_to_str(xS_exec),
                util.get_token_name(tS),
                util.decimal_to_str(xB_exec),
                util.get_token_name(tB),
            ))

    logging.info("=== TRADED TOKEN AMOUNTS ===")
    for t in set(token_amounts_sold.keys()) | set(token_amounts_bought.keys()):
        logging.info("%5s : sold %14s  //  bought %14s" % (
            t,
            util.decimal_to_str(token_amounts_sold.get(t, Decimal("0"))),
            util.decimal_to_str(token_amounts_bought.get(t, Decimal("0"))),
        ))

    logging.info("=== TRADE ON TOKEN PAIRS ===")
    for t1, t2 in nr_exec_orders_tokenpair.keys():
        logging.info("%5s-%-5s : %2d orders executed  //  "
                     "%5s sold %14s / bought %14s  //  "
                     "%5s sold %14s / bought %14s" % (
                         t1,
                         t2,
                         (nr_exec_orders_tokenpair.get(
                             (t1, t2), 0) + nr_exec_orders_tokenpair.get(
                                 (t2, t1), 0)),
                         t1,
                         util.decimal_to_str(
                             tokenpair_amounts_sold.get(
                                 (t1, t2), Decimal("0"))),
                         util.decimal_to_str(
                             tokenpair_amounts_bought.get(
                                 (t1, t2), Decimal("0"))),
                         t2,
                         util.decimal_to_str(
                             tokenpair_amounts_sold.get(
                                 (t2, t1), Decimal("0"))),
                         util.decimal_to_str(
                             tokenpair_amounts_bought.get(
                                 (t2, t1), Decimal("0"))),
                     ))

    # Plot.
    generate_plot(
        tokens,
        nr_exec_orders_tokenpair,
        token_prices,
        token_amounts_sold,
        token_amounts_bought,
        tokenpair_amounts_sold,
        tokenpair_amounts_bought,
        output_dir,
    )
