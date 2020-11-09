import cufflinks as cf
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)


plot_list = ['share_price', 'fee', 'price', 'balance', 'price', 'share_price']
plot_titles = ['YFI Spliced', 'YFI Panama', 'YFI Continous',
               'YFI Continous', 'YFI Spliced', 'YFI Panama']
qf_list = []
for i, j in enumerate(plot_list):
    if i % 2 == 0:
        qf_list.append(cf.QuantFig(
            data_dict[j]['Front']['2020-07-30':'2021-11-17'],
            title=plot_titles[i],
            legend='top',
            name=plot_titles[i],
            datalegend=False,
            rangeselector=dict(steps=['Reset','2M','1M','14D'],
                                    bgcolor=('rgb(150, 200, 250)',.1),
                                    fontsize=12, fontfamily='monospace', x=0, y=1)
        ))
    else:
        qf_list.append(cf.QuantFig(
            data_dict[j]['2020-07-30':'2020-11-17'],
            title=plot_titles[i],
            legend='top',
            name=plot_titles[i],
            datalegend=False,
            rangeselector=dict(steps=['Reset','2M','1M','14D'],
                                    bgcolor=('rgb(150, 200, 250)',.1),
                                    fontsize=12, fontfamily='monospace', x=0, y=1)
        ))

def cf_objects(qf_list, expiry_dates):
    qf_list = qf_list
    plt_list = []
    expiry_dates = pd.read_excel(expiry_dates, header=None, index_col=0, squeeze=1)
    expiry_dates = pd.to_datetime(expiry_dates.values, dayfirst = True)
    for i, qf in enumerate(qf_list):
        for d in expiry_dates:
            qf.add_shapes(shapes=dict(kind='line', x0=d, x1=d, yref='paper', y0=0, y1=1,
                              color='grey', dash='dot'))
        qf.add_volume(colorchange=True)
        qf.add_macd(fast_period=12, slow_period=26, signal_period=9, name='MACD')
        qf.studies['macd']['display'].update(legendgroup=True)
        qf.data.update(showlegend=False)
        qf.add_ema(colors='brown', name='EMA')
        qf.add_bollinger_bands(periods=20, boll_std=2, colors=['magenta', 'grey'], name='BOLL')
        qf.add_rsi(periods=20, rsi_upper=70, rsi_lower=30, name='RSI')
        qf.data.update(showlegend=False)
        plt_list.append(qf_list[i].iplot(asFigure=True))
        dict(plt_list[i])['data'][1]['showlegend'] = False
        dict(plt_list[i])['data'][3]['name'] = 'EMA'
        dict(plt_list[i])['data'][7]['showlegend'] = False
        dict(plt_list[i])['data'][8]['showlegend'] = False
        dict(plt_list[i])['data'][9]['showlegend'] = False
        dict(plt_list[i])['data'][0]['showlegend'] = False
    return plt_list