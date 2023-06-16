# 패키지 불러오기
import pandas as pd
import numpy as np

def calculate(ticker_list, kor_fs):
    # TTM 구하기
    kor_fs = kor_fs.sort_values(['종목코드', '계정', '기준일'])
    kor_fs['ttm'] = kor_fs.groupby(['종목코드', '계정'], as_index=False)['값'].rolling(
        window=4, min_periods=4).sum()['값']

    # 자본은 평균 구하기
    kor_fs['ttm'] = np.where(kor_fs['계정'] == '자본', kor_fs['ttm'] / 4,
                             kor_fs['ttm'])
    kor_fs = kor_fs.groupby(['계정', '종목코드']).tail(1)

    # 지표 계산하기
    kor_fs_merge = kor_fs[['계정', '종목코드',
                           'ttm']].merge(ticker_list[['종목코드', '시가총액', '기준일']],
                                         on='종목코드')
    kor_fs_merge['시가총액'] = kor_fs_merge['시가총액'] / 100000000

    kor_fs_merge['value'] = kor_fs_merge['시가총액'] / kor_fs_merge['ttm']
    kor_fs_merge['value'] = kor_fs_merge['value'].round(4)
    kor_fs_merge['지표'] = np.where(
        kor_fs_merge['계정'] == '매출액', 'PSR',
        np.where(
            kor_fs_merge['계정'] == '영업활동으로인한현금흐름', 'PCR',
            np.where(kor_fs_merge['계정'] == '자본', 'PBR',
                     np.where(kor_fs_merge['계정'] == '당기순이익', 'PER', None))))

    kor_fs_merge.rename(columns={'value': '값'}, inplace=True)
    kor_fs_merge = kor_fs_merge[['종목코드', '기준일', '지표', '값']]
    kor_fs_merge = kor_fs_merge.replace([np.inf, -np.inf, np.nan], None)

    # 배당수익률 계산
    ticker_list['값'] = ticker_list['주당배당금'] / ticker_list['종가']
    ticker_list['값'] = ticker_list['값'].round(4)
    ticker_list['지표'] = 'DY'
    dy_list = ticker_list[['종목코드', '기준일', '지표', '값']]
    dy_list = dy_list.replace([np.inf, -np.inf, np.nan], None)
    dy_list = dy_list[dy_list['값'] != 0]

    return pd.concat([kor_fs_merge, dy_list])