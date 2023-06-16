import time
from tqdm import tqdm
import naver
import krx
import wiseindex
import fnguide
import factor
import repository

if __name__ == '__main__':
    biz_date = naver.biz_date()
    print(f'biz date : {biz_date}')

    # ticker 크롤링
    print('\n--- ticker 크롤링 start ---')
    kor_ticker = krx.get_ticker(biz_date)
    repository.save_ticker(kor_ticker)

    # sector 크롤링
    print('\n--- sector 크롤링 start ---')
    kor_sector = wiseindex.get_sector(biz_date)
    repository.save_sector(kor_sector)

    # ticker 획득
    ticker_list = repository.get_ticker_list()

    # 주가 크롤링
    print('\n--- price 크롤링 start ---')
    for i in tqdm(range(0, len(ticker_list))):
        price = naver.get_price(ticker_list['종목코드'][i])
        repository.save_price(price)
        time.sleep(1)

    # 재무제표 크롤링
    print('\n--- fs 크롤링 start ---')
    for i in tqdm(range(0, len(ticker_list))):
        fs = fnguide.get_fs(ticker_list['종목코드'][i])
        repository.save_fs(fs)
        time.sleep(1)

    # 팩터 업데이트
    print('\n--- factor update ---')
    fs_q = repository.get_fs_q()
    factors = factor.calculate(ticker_list, fs_q)
    repository.save_factor(factors)
