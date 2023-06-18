import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import gridspec

def estrangement_ratio(close, window):
    price = close.copy()
    price['Ratio'] = price / price.rolling(window).mean() * 100
    return price.dropna()

def estrangement_plot(ratio, threshold=90, figsize=(10,6)):
    fig = plt.subplots(figsize=figsize, sharex=True)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])

    # 주가 나타내기
    ax1 = plt.subplot(gs[0])
    ax1 = ratio['Close'].plot()
    ax1.set_xlabel('')
    ax1.axes.xaxis.set_ticks([])

    # 이격도 나타내기
    ax2 = plt.subplot(gs[1])
    ax2 = ratio['Ratio'].plot(color='green', ylim=[ratio['Ratio'].min(),ratio['Ratio'].max()])
    ax2.axhline(y=threshold, color='r', linestyle='-')
    ax2.set_xlabel
    plt.subplots_adjust(wspace=0, hspace=0)

    plt.show()

kospi = yf.download('^KS11', start="2000-01-01")

ratio = estrangement_ratio(kospi[['Close']], 200) # 200일
estrangement_plot(ratio, 90)
estrangement_plot(ratio.loc['2019':], 90)

ratio = estrangement_ratio(kospi[['Close']], 20)
estrangement_plot(ratio.loc['2019':], 90)
