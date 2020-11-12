import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from typing import Union


def load_csv_dir(data_dir):
    """Reads a list of csv files from a directory
    and returns it as a single pandas dataframe."""
    try:
        return pd.concat(map(pd.read_csv, glob.glob(data_dir)))
    except:
        print(data_dir)


def time_range(df):
    time_fmt = "%H:%M"
    opening_hours = datetime.datetime.strptime("08:00", time_fmt)
    closing_hours = datetime.datetime.strptime("16:30", time_fmt)

    df["CalcDateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df.drop(columns=["Date", "Time"], inplace=True)

    df = df[(df.CalcDateTime >= opening_hours) & (df.CalcDateTime <= closing_hours)]
    return df


def read_date_range(start_date: str, end_date: str = None, mnemonic: str = None):
    """Loads csv files that falls between a date
    range and returns it as a single dataframe.
    The `mnemonic` option can be used to filter
    this dataframe to a specific stock."""
    if end_date is None:
        end_date = str(datetime.date.today())
    list_of_dirs = glob.glob("../data/deutsche-boerse-xetra-pds/*/")
    range_dirs = []
    for x in list_of_dirs:
        if (x.split("/")[-2] > start_date) and (x.split("/")[-2] < end_date):
            range_dirs.append(x)
    range_dirs.sort()
    df = load_csv_dir(range_dirs[0] + "*")
    # df = time_range(df)
    if mnemonic:
        df = df[df["Mnemonic"] == mnemonic]
    for dir_ in range_dirs[1:]:
        temp_df = load_csv_dir(dir_ + "*")
        # temp_df = time_range(temp_df)
        if mnemonic:
            temp_df = temp_df[temp_df["Mnemonic"] == mnemonic]
        df = pd.concat([df, temp_df])
    df["CalcDateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df.drop(columns=["Date", "Time"], inplace=True)
    df[["TradedVolume", "NumberOfTrades"]] = df[
        ["TradedVolume", "NumberOfTrades"]
    ].astype("float")
    df.sort_values(["CalcDateTime", "Mnemonic"], inplace=True)
    if mnemonic:
        df.set_index("CalcDateTime", drop=True, inplace=True)
    return df


def plot_security(
    df: pd.DataFrame,
    mnemonic: str,
    metric: Union[str, dict],
    kind: str = ["line", "ohlc", "candlestick"],
    resample_freq: str = "1Min",
    volume: bool = False,
):
    """Plots charts by filtering on Stocks"""
    if mnemonic is None:
        mnemonic = df["Mnemonic"].unique()[0]
        selected = df[df.Mnemonic == mnemonic].copy()
    else:
        selected = df[df.Mnemonic == mnemonic].copy()
    if "CalcDateTime" in selected.columns:
        selected.set_index("CalcDateTime", drop=True, inplace=True)

    ohlcv_dict = {
        "StartPrice": "first",
        "MaxPrice": "max",
        "MinPrice": "min",
        "EndPrice": "last",
        "TradedVolume": "sum",
        "NumberOfTrades": "sum",
    }

    if type(metric) == dict:
        ohlcv_dict = {**ohlcv_dict, **metric}
        metric = list(metric.keys())[0]

    selected = selected.resample(resample_freq).apply(ohlcv_dict)
    selected.dropna(inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if kind == "line":
        trace1 = go.Scatter(x=selected.index, y=selected[metric], name=metric)

    elif kind == "ohlc":
        trace1 = go.Ohlc(
            x=selected.index,
            open=selected["StartPrice"],
            high=selected["MaxPrice"],
            low=selected["MinPrice"],
            close=selected["EndPrice"],
            name=kind,
        )

    elif kind == "candlestick":
        trace1 = go.Candlestick(
            x=selected.index,
            open=selected["StartPrice"],
            high=selected["MaxPrice"],
            low=selected["MinPrice"],
            close=selected["EndPrice"],
            name=kind,
        )

    else:
        raise ValueError("Enter a valid kind!")

    trace2 = go.Bar(
        x=selected.index,
        y=selected["TradedVolume"],
        name="Volume",
        opacity=0.3,
        marker={"color": "blue"},
    )

    fig.add_trace(trace1)
    fig.add_trace(trace2, secondary_y=True)
    fig.update_layout(title=mnemonic + f", sampled {resample_freq}")
    fig.show()


def plot_moving_averages(
    df,
    mnemonic,
    smas: list = None,
    emas: list = None,
    crossover: list = None,
    metric: str = "StartPrice",
):
    """Plots various kinds of moving averages.
    Has an option to plot crossover points. To
    specify series to calculate crossover on,
    specify the type of series first, an underscore
    and the val of the type. Eg: ['ema_.3', 'sma_30'].
    To use the default series, use 'org_{any_number}'.
    Warning: for SMA and EMA, only specify those values
    which you have already specifiend in their
    respective lists for calculation above."""
    selected = df[df.Mnemonic == mnemonic].copy()
    selected.set_index("CalcDateTime", inplace=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=selected.index, y=selected[metric], name=metric))
    if smas:
        sma = {}
        for p in smas:
            sma[p] = selected.rolling(p, min_periods=1).mean()
            fig.add_trace(go.Scatter(x=sma[p].index, y=sma[p][metric], name=f"SMA {p}"))
    if emas:
        ema = {}
        for a in emas:
            ema[a] = selected.ewm(alpha=a).mean()
            fig.add_trace(go.Scatter(x=ema[a].index, y=ema[a][metric], name=f"EMA {a}"))
    if crossover:
        series = {}
        c_list = [(s.split("_")[0], float(s.split("_")[1])) for s in crossover]
        for itr, (type_, val) in enumerate(c_list):
            if type_ == "sma":
                series[itr] = sma[val]
            elif type_ == "ema":
                series[itr] = ema[val]
            elif type_ == "org":
                series[itr] = selected
            else:
                raise ValueError("Enter the list properly!")
        crossovers = crossover_shift(series[0], series[1], metric)
        fig = plot_crossovers(fig, selected, metric, crossovers)
    fig.update_layout(title=f"{mnemonic} Moving Averages")
    fig.show()
