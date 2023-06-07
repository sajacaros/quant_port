# kospi sector
import requests as rq

gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
gen_otp_stk = {
    'mktId': 'STK',
    'trdDd': biz_day,
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
}
headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
otp_stk = rq.post(gen_otp_url, gen_otp_stk, headers=headers).text

print(otp_stk)

from io import BytesIO
import pandas as pd

down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
down_sector_stk = rq.post(down_url, {'code': otp_stk}, headers=headers)
print(down_sector_stk.content[:100])

sector_stk = pd.read_csv(BytesIO(down_sector_stk.content), encoding='EUC-KR')
sector_stk.head()

# kosdaq sector
import requests as rq

gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
gen_otp_ksq = {
    'mktId': 'KSQ',
    'trdDd': biz_day,
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
}
headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
otp_ksq = rq.post(gen_otp_url, gen_otp_ksq, headers=headers).text

from io import BytesIO
import pandas as pd

down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
down_sector_ksq = rq.post(down_url, {'code': otp_ksq}, headers=headers)
sector_ksq = pd.read_csv(BytesIO(down_sector_ksq.content), encoding='EUC-KR')
sector_ksq.head()

# 섹터 병합
krx_sector = pd.concat([sector_stk, sector_ksq]).reset_index(drop=True)
krx_sector['종목명'] = krx_sector['종목명'].str.strip()
krx_sector['기준일'] = biz_day

krx_sector.head()

# 지표 다운로드
import requests as rq
from io import BytesIO
import pandas as pd

gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
gen_otp_data = {
    'searchType': '1',
    'mktId': 'ALL',
    'trdDd': biz_day,
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03501'
}
headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
otp = rq.post(gen_otp_url, gen_otp_data, headers=headers).text

down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
krx_ind = rq.post(down_url, {'code': otp}, headers=headers)

krx_ind = pd.read_csv(BytesIO(krx_ind.content), encoding='EUC-KR')
krx_ind['종목명'] = krx_ind['종목명'].str.strip()
krx_ind['기준일'] = biz_day

krx_ind.head()

# 클렌징
diff = list(set(krx_sector['종목명']).symmetric_difference(set(krx_ind['종목명'])))

# 업종과 지표 통합
kor_ticker = pd.merge(krx_sector,
                      krx_ind,
                      on=krx_sector.columns.intersection(
                          krx_ind.columns).tolist(),
                      how='outer')

kor_ticker.head()

# 주식 분류
import numpy as np

kor_ticker['종목구분'] = np.where(kor_ticker['종목명'].str.contains('스팩|제[0-9]+호'), '스팩',
                              np.where(kor_ticker['종목코드'].str[-1:] != '0', '우선주',
                                       np.where(kor_ticker['종목명'].str.endswith('리츠'), '리츠',
                                                np.where(kor_ticker['종목명'].isin(diff),  '기타',
                                                '보통주'))))
kor_ticker = kor_ticker.reset_index(drop=True)
kor_ticker.columns = kor_ticker.columns.str.replace(' ', '')
kor_ticker = kor_ticker[['종목코드', '종목명', '시장구분', '종가',
                         '시가총액', '기준일', 'EPS', '선행EPS', 'BPS', '주당배당금', '종목구분']]
kor_ticker = kor_ticker.replace({np.nan: None})
kor_ticker['기준일'] = pd.to_datetime(kor_ticker['기준일'])

kor_ticker.head()

# db update
import pymysql

con = pymysql.connect(user='quantist',
                      passwd='quant!*#',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')

mycursor = con.cursor()
query = f"""
    insert into kor_ticker (종목코드,종목명,시장구분,종가,시가총액,기준일,EPS,선행EPS,BPS,주당배당금,종목구분)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    종목명=new.종목명,시장구분=new.시장구분,종가=new.종가,시가총액=new.시가총액,EPS=new.EPS,선행EPS=new.선행EPS,
    BPS=new.BPS,주당배당금=new.주당배당금,종목구분 = new.종목구분;
"""

args = kor_ticker.values.tolist()

mycursor.executemany(query, args)
con.commit()

con.close()

