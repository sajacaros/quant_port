import time
import requests as rq
import pandas as pd
from tqdm import tqdm

sector_code = [
    'G25', 'G35', 'G50', 'G40', 'G10', 'G20', 'G55', 'G30', 'G15', 'G45'
]

def get_sector(biz_date):
    data_sector = []

    for i in tqdm(sector_code):
        url = f'''http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={biz_date}&sec_cd={i}'''
        data = rq.get(url).json()
        data_pd = pd.json_normalize(data['list'])

        data_sector.append(data_pd)

        time.sleep(2)

    kor_sector = pd.concat(data_sector, axis=0)
    kor_sector = kor_sector[['IDX_CD', 'CMP_CD', 'CMP_KOR', 'SEC_NM_KOR']]
    kor_sector['기준일'] = pd.to_datetime(biz_date)

    return kor_sector


