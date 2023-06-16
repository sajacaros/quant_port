import requests as rq
from io import BytesIO
import pandas as pd
import numpy as np

headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}

def get_sector_otp(mtk_id, biz_day):
    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    gen_otp_stk = {
        'mktId': mtk_id,
        'trdDd': biz_day,
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
    }

    return rq.post(gen_otp_url, gen_otp_stk, headers=headers).text

def get_factor_opt(biz_day):
    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    gen_otp_data = {
        'searchType': '1',
        'mktId': 'ALL',
        'trdDd': biz_day,
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03501'
    }
    return rq.post(gen_otp_url, gen_otp_data, headers=headers).text

def download(otp):
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_sector_stk = rq.post(down_url, {'code': otp}, headers=headers)
    return pd.read_csv(BytesIO(down_sector_stk.content), encoding='EUC-KR')

def get_sector(biz_day):
    kospi_otp = get_sector_otp('STK', biz_day)
    kospi_sector = download(kospi_otp)
    kosdaq_otp = get_sector_otp('KSQ', biz_day)
    kosdaq_sector = download(kosdaq_otp)

    krx_sector = pd.concat([kospi_sector, kosdaq_sector]).reset_index(drop=True)
    krx_sector['종목명'] = krx_sector['종목명'].str.strip()
    krx_sector['기준일'] = biz_day

    return krx_sector

def get_factor(biz_day):
    factor_opt = get_factor_opt(biz_day)
    krx_ind = download(factor_opt)

    krx_ind['종목명'] = krx_ind['종목명'].str.strip()
    krx_ind['기준일'] = biz_day

    return krx_ind


def get_ticker(biz_date):
    # 업종과 지표 통합
    krx_sector = get_sector(biz_date)
    krx_ind = get_factor(biz_date)
    kor_ticker = pd.merge(krx_sector,
                          krx_ind,
                          on=krx_sector.columns.intersection(
                              krx_ind.columns).tolist(),
                          how='outer')

    # 클렌징
    diff = list(set(krx_sector['종목명']).symmetric_difference(set(krx_ind['종목명'])))

    # 주식 분류
    kor_ticker['종목구분'] = np.where(kor_ticker['종목명'].str.contains('스팩|제[0-9]+호'), '스팩',
                                  np.where(kor_ticker['종목코드'].str[-1:] != '0', '우선주',
                                           np.where(kor_ticker['종목명'].str.endswith('리츠'), '리츠',
                                                    np.where(kor_ticker['종목명'].isin(diff), '기타',
                                                             '보통주'))))
    kor_ticker = kor_ticker.reset_index(drop=True)
    kor_ticker.columns = kor_ticker.columns.str.replace(' ', '')
    kor_ticker = kor_ticker[['종목코드', '종목명', '시장구분', '종가',
                             '시가총액', '기준일', 'EPS', '선행EPS', 'BPS', '주당배당금', '종목구분']]
    kor_ticker = kor_ticker.replace({np.nan: None})
    kor_ticker['기준일'] = pd.to_datetime(kor_ticker['기준일'])

    return kor_ticker