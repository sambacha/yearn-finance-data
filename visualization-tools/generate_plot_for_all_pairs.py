#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import util
import contract_reader
from plot_orderbook_tokenpair import generate_plot
from pathlib import Path
import argparse
from multiprocessing import Pool, cpu_count
from contract_reader import ContractReader
from functools import partial

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

    args = parser.parse_args()
    contract_reader = ContractReader(args.network)

    batch_ID = contract_reader.get_current_batch_id()
    output_dir = "./orderbook_plots_" + str(batch_ID)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if args.jsonFile is not None:
        # Read input JSON.
        assert os.path.isfile(args.jsonFile)
        inst = util.read_instance_from_file(args.jsonFile)
    else:
        # Get instance from blockchain.
        inst = util.read_instance_from_blockchain(contract_reader)

    # Get max token ID
    # Todo: This can be automatized, but then also the TokenInfo.py must be generated automatically
    max_token_id = 16

    # Plot.
    plot_args = [
        ("token" + str(t1), "token" + str(t2))
        for t1 in range(0, max_token_id)
        for t2 in range(0, max_token_id)
        if t1 != t2
    ]

    def plot(args):
        generate_plot(*args, inst["orders"], output_dir, False, auto_open=False)

    num_cores = cpu_count()
    with Pool(num_cores) as pool:
        pool.map(plot, plot_args)
