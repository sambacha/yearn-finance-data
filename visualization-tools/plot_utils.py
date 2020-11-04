#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import math
from typing import List, Dict
from decimal import Decimal
import numpy as np
import networkx as nx
import matplotlib.cm
import plotly
import plotly.graph_objs as go

from util import EDGE_TYPE, NODE_TYPE


def plot_network(
    nodes: List[NODE_TYPE],
    edges: List[EDGE_TYPE],
    node_weights: Dict[NODE_TYPE, int],
    node_hovers: Dict[NODE_TYPE, str],
    node_labels: Dict[NODE_TYPE, str],
    edge_weights: Dict[EDGE_TYPE, int],
    edge_hovers: Dict[EDGE_TYPE, str],
    plot_title: str,
    output_dir: str = "./",
    ipython: bool = False,
    auto_open: bool = True,
):
    """Plot a given network of nodes and edges.

    Args:
        nodes: List of node names/indices.
        edges: List of tuples of node indices.
        node_weights: Dict of node index => node weight (determining node size in plot).
        node_hovers: Dict of node index => hover text.
        node_labels: Dict of node index => node label.
        edge_weights: Dict of edge => edge weight (determining edge width in plot).
        edge_hovers: Dict of edge => hover text.
        plot_title: Title of the plot.

    Kwargs:
        output_dir: Location for storing the plot.
        ipython: Running from IPython environment, or not.
        auto_open: Show plot in browser, or not.

    Returns:
        A plotly plot object.

    """
    # Compute node positions via networkx DiGraph.
    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    pos = {t: nx.circular_layout(G)[t] for t in nodes}
    nx.set_node_attributes(G, name="pos", values=pos)

    x = [G.nodes[nID]["pos"][0] for nID in G.nodes()]
    y = [G.nodes[nID]["pos"][1] for nID in G.nodes()]

    # Adjust node weights, if required.
    wmin, wmax = Decimal(5), Decimal(50)
    node_weights = {
        nID: node_weights[nID] if nID in node_weights else wmin for nID in nodes
    }

    if node_weights:
        if max(node_weights.values()) > wmax:
            node_weights = {
                nID: node_weights[nID] / max(node_weights.values()) * wmax
                for nID in nodes
            }

        if min(node_weights.values()) < wmin:
            node_weights = {
                nID: wmax
                - (wmax - node_weights[nID])
                / (wmax - min(node_weights.values()))
                * (wmax - wmin)
                for nID in nodes
            }

        assert min(node_weights.values()) >= wmin and max(node_weights.values()) <= wmax

    # Init node hovers, if required.
    node_hovers = {
        nID: node_hovers[nID] if nID in node_hovers else None for nID in nodes
    }

    # Init node labels, if required.
    node_labels = {
        nID: node_labels[nID] if nID in node_labels else str(nID) for nID in nodes
    }

    # Node information.
    node_trace = go.Scatter(
        x=x,
        y=y,
        mode="markers",
        text=list(node_hovers.values()),
        hoverinfo="text",
        marker=go.scatter.Marker(
            size=[node_weights[nID] for nID in nodes],
            sizemin=wmin,
            showscale=False,
            colorscale="Reds",
            reversescale=False,
            color=[node_weights[nID] for nID in nodes],
            opacity=1.0,
            cmin=0,
            cmax=max(node_weights.values() or [1]),
            # colorbar = dict( thickness = 15,
            #                 title = 'colorbartitle',
            #                 xanchor = 'left',
            #                 titleside = 'right' ),
            line=dict(width=2),
        ),
    )

    if not edges:
        edge_traces = []

    else:
        # Scale edge weights to some interval.
        wL, wU = (2.0, 20.0)
        if edge_weights is None:
            edge_weights = {}
        elif all(math.isnan(w) for w in edge_weights.values()):
            edge_weights = {eID: 0.5 * (wU + wL) for eID in edge_weights}
        edge_weights = {
            eID: float(edge_weights[eID]) if eID in edge_weights else wL
            for eID in edges
        }

        if max(edge_weights.values()) > wU:
            edge_weights = {
                eID: edge_weights[eID] / max(edge_weights.values()) * wU
                for eID in edges
            }
        if min(edge_weights.values()) < wL:
            edge_weights = {
                eID: wU
                - (wU - edge_weights[eID])
                / (wU - min(edge_weights.values()))
                * (wU - wL)
                for eID in edges
            }
        assert min(edge_weights.values()) >= wL and max(edge_weights.values()) <= wU

        # Init edge hovers, if required.
        if edge_hovers is None:
            edge_hovers = {}
        edge_hovers = {
            eID: edge_hovers[eID] if eID in edge_hovers else None for eID in edges
        }

        _x = {t: x[i] for i, t in enumerate(nodes)}
        _y = {t: y[i] for i, t in enumerate(nodes)}

        # Setup edge colors (get from colormap).
        viridis_cmap = matplotlib.cm.get_cmap("Blues")
        norm = matplotlib.colors.Normalize(vmin=0, vmax=max(edge_weights.values()))
        edge_colors = {}
        for eID, w in edge_weights.items():
            k = matplotlib.colors.colorConverter.to_rgb(viridis_cmap(norm(w)))
            edge_colors[eID] = "rgb(%s,%s,%s)" % (k[0], k[1], k[2])

        # Edge information.
        edge_traces = [
            go.Scatter(
                x=[_x[e[0]], _x[e[0]] + 0.55 * (_x[e[1]] - _x[e[0]]), _x[e[1]]],
                y=[_y[e[0]], _y[e[0]] + 0.55 * (_y[e[1]] - _y[e[0]]), _y[e[1]]],
                mode="lines",
                text=[None, edge_hovers[e], None],
                hoverinfo="text",
                line=go.scatter.Line(width=edge_weights[e], color=edge_colors[e]),
            )
            for e in edges
        ]

    # Prepare figure.
    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            title="<br>%s" % plot_title,
            titlefont=dict(size=16),
            showlegend=False,
            hovermode="closest",
            autosize=False,
            width=1000,
            height=900,
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    x=x[i],
                    y=y[i],
                    text="<b>" + node_labels[nID] + "</b>",
                    font=dict(size=18, color="#ffffff"),
                    align="center",
                    showarrow=True,
                    arrowhead=0,
                    arrowcolor="black",
                    arrowwidth=0.1,
                    arrowsize=0.3,
                    xref="x",
                    yref="y",
                    ax=30,
                    ay=20,
                    bgcolor="#20ade3",
                    bordercolor="black",
                    borderpad=5,
                )
                for i, nID in enumerate(nodes)
                if node_labels is not None
            ],
            xaxis=go.layout.XAxis(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=go.layout.YAxis(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor="white",
            plot_bgcolor="white",
        ),
    )

    # Set plot environment.
    plt = plotly.offline.iplot if ipython else plotly.offline.plot
    filename = os.path.join(output_dir, "%s.html" % plot_title)
    plt(fig, filename=filename, auto_open=auto_open)

    return


def plot_orderbook(
    t1: str,
    t2: str,
    xrates: np.ndarray,
    cumulated_sell_amounts: Dict[str, np.ndarray],
    cumulated_buy_amounts: Dict[str, np.ndarray],
    plot_title: str,
    output_dir: str = "./",
    ipython: bool = False,
    auto_open: bool = True,
):
    """Plot the orderbook for a given pair of tokens.

    Args:
        t1: Name of token 1.
        t2: Name of token 2.
        xrates: Array of sampled exchange rates between t1/t2.
        cumulated_sell_amounts: Dict of token => cumulated sell amounts per xrate.
        cumulated_buy_amounts: Dict of token => cumulated buy amounts per xrate
        plot_title: Title of the plot.

    Kwargs:
        output_dir: Location for storing the plot.
        ipython: Running from IPython environment, or not.
        auto_open: Show plot in browser, or not.

    Returns:
        A plotly plot object.

    """
    # Define some colors.
    C0 = "#1f77b4"  # muted blue
    C1 = "#ff7f0e"  # safety orange
    C2 = "#2ca02c"  # cooked asparagus green
    # C3 = '#d62728'  # brick red

    # Init figure.
    fig = plotly.subplots.make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "buy/sell amount in %s" % t1,
            "buy/sell amount in %s" % t2,
            "net amount in %s" % t1,
            "net amount in %s" % t2,
        ),
        vertical_spacing=0.15,
        shared_xaxes=False,
    )

    _xS1 = cumulated_sell_amounts[t1]
    _xB1 = cumulated_buy_amounts[t1]
    _xS2 = cumulated_sell_amounts[t2]
    _xB2 = cumulated_buy_amounts[t2]

    _idx = range(len(xrates))
    xrate_hovers = ["rate: %.4f %s/%s" % (xrates[i], t1, t2) for i in _idx]

    # Create traces for order amounts and plot.
    trace_xS1 = go.Scatter(
        x=xrates,
        y=_xS1,
        name="sell %s" % t1,
        showlegend=False,
        hovertext=[
            xrate_hovers[i] + "<br>amount: %.4f %s" % (_xS1[i], t1) for i in _idx
        ],
        hoverinfo="text+name",
        fill=None,
        mode="lines",
        line={"color": C0, "width": 1},
    )

    trace_xB1 = go.Scatter(
        x=xrates,
        y=_xB1,
        name="buy %s" % t1,
        showlegend=False,
        hovertext=[
            xrate_hovers[i] + "<br>amount: %.4f %s" % (_xB1[i], t1) for i in _idx
        ],
        hoverinfo="text+name",
        fill=None,
        mode="lines",
        line={"color": C1, "width": 1},
    )

    trace_x1_min = go.Scatter(
        x=xrates,
        y=np.minimum(_xS1, _xB1),
        showlegend=False,
        hoverinfo="skip",
        fill="tozeroy",
        mode="lines",
        line={"color": "#bfbfbf", "width": 0},
    )

    trace_xS2 = go.Scatter(
        x=xrates,
        y=_xS2,
        name="sell %s" % t2,
        showlegend=False,
        hovertext=[
            xrate_hovers[i] + "<br>amount: %.4f %s" % (_xS2[i], t2) for i in _idx
        ],
        hoverinfo="text+name",
        fill=None,
        mode="lines",
        line={"color": C1, "width": 1},
    )

    trace_xB2 = go.Scatter(
        x=xrates,
        y=_xB2,
        name="buy %s" % t2,
        showlegend=False,
        hovertext=[
            xrate_hovers[i] + "<br>amount: %.4f %s" % (_xB2[i], t2) for i in _idx
        ],
        hoverinfo="text+name",
        fill=None,
        mode="lines",
        line={"color": C0, "width": 1},
    )

    trace_x2_min = go.Scatter(
        x=xrates,
        y=np.minimum(_xS2, _xB2),
        showlegend=False,
        hoverinfo="skip",
        fill="tozeroy",
        mode="lines",
        line={"color": "#bfbfbf", "width": 0},
    )

    trace_x1_net = go.Scatter(
        x=xrates,
        y=_xS1 - _xB1,
        name="net %s" % t1,
        showlegend=False,
        hovertext=[
            xrate_hovers[i] + "<br>amount: %.4f %s" % (_xS1[i] - _xB1[i], t1)
            for i in _idx
        ],
        hoverinfo="text+name",
        fill="tozeroy",
        mode="lines",
        line={"color": C2, "width": 1},
    )

    trace_x2_net = go.Scatter(
        x=xrates,
        y=_xS2 - _xB2,
        name="net %s" % t2,
        showlegend=False,
        hovertext=[
            xrate_hovers[i] + "<br>amount: %.4f %s" % (_xS2[i] - _xB2[i], t2)
            for i in _idx
        ],
        hoverinfo="text+name",
        fill="tozeroy",
        mode="lines",
        line={"color": C2, "width": 1},
    )

    fig.append_trace(trace_xB1, 1, 1)
    fig.append_trace(trace_xS1, 1, 1)
    fig.append_trace(trace_x1_min, 1, 1)
    fig.append_trace(trace_xB2, 1, 2)
    fig.append_trace(trace_xS2, 1, 2)
    fig.append_trace(trace_x2_min, 1, 2)
    fig.append_trace(trace_x1_net, 2, 1)
    fig.append_trace(trace_x2_net, 2, 2)

    # Set figure title.
    title = "<b>Orderbook %s / %s</b>" % (t1, t2)

    fig["layout"].update(
        height=1000,
        width=1000,
        paper_bgcolor="white",
        plot_bgcolor="white",
        title=title,
    )
    xaxis_title = "exchange rate %s/%s" % (t1, t2)
    for xaxis in ["xaxis1", "xaxis2", "xaxis3", "xaxis4"]:
        fig["layout"][xaxis].update(title=xaxis_title)

    # Set plot environment.
    plt = plotly.offline.iplot if ipython else plotly.offline.plot
    fn = os.path.join(output_dir, "orderbook_%s_%s.html" % (t1, t2))
    plt(fig, filename=fn, auto_open=auto_open)

    return
