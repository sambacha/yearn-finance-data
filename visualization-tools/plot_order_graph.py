#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Plot graph of tokens and orders.

Example call:
> python plot_order_graph.py data/dfusion_input.json
"""
import os
import argparse
import logging
from typing import Dict
import decimal
from decimal import Decimal
from plot_utils import plot_network
from contract_reader import ContractReader
import util
from util import EDGE_TYPE
import TokenInfo

# Set decimal precision.
decimal.getcontext().prec = 100


def generate_plot(
    nr_orders_tokenpair: Dict[EDGE_TYPE, int],
    output_dir: str = "./",
    ipython: bool = False,
    **kwargs
):
    """Generate a token-order-graph plot using plotly.

    Args:
        nr_orders_tokenpair: Dict of token pairs => number of orders.

    Kwargs:
        output_dir: Location for storing the plot.
        ipython: Running from IPython environment, or not.

    """
    # Extract set of tokens.
    tokens = sorted(list(set(sum(nr_orders_tokenpair.keys(), ()))))

    # Get number of orders per token.
    nr_orders_token = {t: 0 for t in tokens}
    for (t1, t2), nr_orders in nr_orders_tokenpair.items():
        nr_orders_token[t1] += nr_orders
        nr_orders_token[t2] += nr_orders

    # Set plot attributes.
    node_weights = {t: Decimal(n) for t, n in nr_orders_token.items()}

    node_labels = {t: t for t in tokens}

    node_hovers = {
        t: "=== %s ===<br># orders : %d" % (t, node_weights[t]) for t in node_weights
    }

    edge_weights = nr_orders_tokenpair

    edge_hovers = {
        (t1, t2): "=== %s/%s ===<br># orders : %d" % (t1, t2, edge_weights[t1, t2])
        for (t1, t2) in edge_weights
    }

    # Plot.
    plot_network(
        tokens,
        list(edge_weights.keys()),
        node_weights=node_weights,
        node_labels=node_labels,
        node_hovers=node_hovers,
        edge_weights=edge_weights,
        edge_hovers=edge_hovers,
        plot_title="token-order-graph",
        output_dir=output_dir,
        ipython=ipython,
        **kwargs
    )

    return


if __name__ == "__main__":
    """Main function."""

    # Process command line arguments.
    parser = argparse.ArgumentParser(
        description="Input file and output directory parser."
    )

    parser.add_argument(
        "--jsonFile",
        type=str,
        help="A JSON input file containing a batch auction instance.",
    )

    parser.add_argument(
        "--network",
        type=str,
        choices=["mainnet", "rinkeby"],
        default="mainnet",
        help="Choose one network (mainnet or rinkeby)",
    )

    parser.add_argument(
        "--logging",
        type=str.upper,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level.",
    )

    args = parser.parse_args()

    util.configure_logger(getattr(logging, args.logging))

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

    # Get number of orders per token pair.
    assert "orders" in inst
    nr_orders_tokenpair = util.get_nr_orders_tokenpair(inst["orders"])

    logging.info("=== NUMBER OF ORDERS ON TOKEN PAIRS ===")
    for (t1, t2), nr_orders in nr_orders_tokenpair.items():
        logging.info("%5s / %-5s : %3d" % (t1, t2, nr_orders))

    logging.info("=== ORDERS (%d) ===" % len(inst["orders"]))
    util.log_orders(inst["orders"])

    # Generate plot.
    generate_plot(nr_orders_tokenpair, output_dir)
