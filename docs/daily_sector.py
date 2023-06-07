import time
import json
import requests as rq
import pandas as pd
from tqdm import tqdm

sector_code = [
    'G25', 'G35', 'G50', 'G40', 'G10', 'G20', 'G55', 'G30', 'G15', 'G45'
]

data_sector = []

for i in tqdm(sector_code):
    url = f'''http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={biz_day}&sec_cd={i}'''
    data = rq.get(url).json()
    data_pd = pd.json_normalize(data['list'])

    data_sector.append(data_pd)

    time.sleep(2)

kor_sector = pd.concat(data_sector, axis = 0)
kor_sector = kor_sector[['IDX_CD', 'CMP_CD', 'CMP_KOR', 'SEC_NM_KOR']]
kor_sector['기준일'] = biz_day
kor_sector['기준일'] = pd.to_datetime(kor_sector['기준일'])

import pymysql

con = pymysql.connect(user='quantist',
                      passwd='quant!*#',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')

mycursor = con.cursor()
query = f"""
    insert into kor_sector (IDX_CD, CMP_CD, CMP_KOR, SEC_NM_KOR, 기준일)
    values (%s,%s,%s,%s,%s) as new
    on duplicate key update
    IDX_CD = new.IDX_CD, CMP_KOR = new.CMP_KOR, SEC_NM_KOR = new.SEC_NM_KOR
"""

args = kor_sector.values.tolist()

mycursor.executemany(query, args)
con.commit()

con.close()