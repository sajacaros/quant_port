import requests as rq
from bs4 import BeautifulSoup
import re
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
from io import BytesIO

def biz_date():
    url = 'https://finance.naver.com/sise/sise_deposit.naver'
    data = rq.get(url)
    data_html = BeautifulSoup(data.content, features="html.parser")
    parse_day = data_html.select_one('div.subtop_sise_graph2 > ul.subtop_chart_note > li > span.tah').text

    biz_day = re.findall('[0-9]+', parse_day)
    biz_day = ''.join(biz_day)
    return biz_day


def get_price(ticker):
    # 시작일과 종료일
    fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d")
    to = (date.today()).strftime("%Y%m%d")

    # 오류 발생 시 이를 무시하고 다음 루프로 진행
    try:
        # url 생성
        url = f'''https://fchart.stock.naver.com/siseJson.naver?symbol={ticker}&requestType=1
            &startTime={fr}&endTime={to}&timeframe=day'''

        # 데이터 다운로드
        data = rq.get(url).content
        data_price = pd.read_csv(BytesIO(data))

        # 데이터 클렌징
        price = data_price.iloc[:, 0:6]
        price.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
        price = price.dropna()
        price['날짜'] = price['날짜'].str.extract('(\d+)')
        price['날짜'] = pd.to_datetime(price['날짜'])
        price['종목코드'] = ticker
    except:
        print(ticker)
    return price