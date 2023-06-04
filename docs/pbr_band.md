# KOSPI PBR 밴드 그리기

## KOSPI PBR 다운로드
* 현재 2004-01 ~ 2023-04 다운로드
* https://kosis.kr/statHtml/statHtml.do?orgId=343&tblId=DT_343_2010_S0034
```
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

kospi_pbr = pd.read_csv("data/kospi_PBR.csv", encoding="cp949").T[1:]
kospi_pbr.columns = ['PBR']
kospi_pbr.index.name = 'Date'
kospi_pbr.reset_index(inplace=True)
kospi_pbr['Date'] = pd.to_datetime(kospi_pbr['Date']).apply(lambda x: x.strftime('%Y-%m'))
kospi_pbr.set_index('Date', inplace=True)
kospi_pbr.head()

kospi_price = yf.download('^KS11', start="2004-01-01")[['Close']]
kospi_price = kospi_price.resample('M').last()
kospi_price.reset_index(inplace=True)
kospi_price['Date'] = pd.to_datetime(kospi_price['Date']).apply(lambda x: x.strftime('%Y-%m'))
kospi_price.set_index('Date', inplace=True)
kospi_price.head()

# data = kospi_price.copy()
# data['year'] = data.index.year
# data['month'] = data.index.month
# data.drop(['year', 'month'], axis=1, inplace=True)


kospi_bind = pd.merge(kospi_pbr, kospi_price, left_index=True, right_index=True, how="left")
kospi_bind.head()

kospi_bind['BPS'] = kospi_bind['Close']/kospi_bind['PBR'] 

base = 0.8
inc = 0.2
loop = 6

for i in range(loop):
  kospi_bind['PBRx'+str(base+inc*i)] = kospi_bind['BPS'] * (base+inc*i) 

kospi_bind.loc[:, (kospi_bind.columns != 'PBR') & (kospi_bind.columns != 'BPS')].plot()

plt.show()
```