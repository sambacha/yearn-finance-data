# DEX visualizations

## Usage via docker:

Checkout this repo and then build the docker and run it

```
docker build -t order_book_printer .
docker run -it -v ~/PATH_TO_FOLDER/dex-visualization-tools/:/app/ order_book_printer
```

Inside the docker, you can visualize the orderbook:

```
python3 plot_orderbook_tokenpair.py PAX WETH
```

or generate all orderbook plots for all tokens from a json:

```
python3 generate_plot_for_all_pairs.py --jsonFile data/dfusion_input.json
```

or visualize a solution:

```
python3 plot_solution_graph.py data/kraken_solution.json
```

## Installation

- Create virtual Python 3.6 environment: `virtualenv --python=/usr/bin/python3.6 venv`
- Activate virtual environment: `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

## Run

- Instance plots (tokens/orders): `python plot_order_graph.py [--jsonFile INSTANCE_JSON]`
- Solution plots (execution details): `python plot_solution_graph.py [SOLUTION_JSON]`
- Orderbook plots (buy and sell amounts for token pairs): `python plot_orderbook_tokenpair.py [TOKEN1] [TOKEN2] [--jsonFile INSTANCE_JSON]`

If no JSON file is provided for `plot_order_graph.py` and `plot_orderbook_tokenpair.py`, the script will fetch the data directly from the Gnosis Protocol smart contract.

## Example data

in `data/`:

- `kraken_{instance|solution}.json` - instance and solution from Kraken exchange
- `dfusion_{instance|solution}.json` - instance and solution from Gnosis Protocol PoC

example runs:

- `python plot_order_graph.py --jsonFile data/dfusion_input.json`
- `python plot_solution_graph.py data/kraken_solution.json`
- `python plot_orderbook_tokenpair.py PAX WETH`

additionally, the network ('mainnet' or 'rinkeby') for the token pair can be defined as well via the network parameter:

- `python plot_orderbook_tokenpair.py PAX WETH --network=rinkeby`
