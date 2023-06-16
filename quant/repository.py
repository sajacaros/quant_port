import pymysql
import pandas as pd
from sqlalchemy import create_engine


def create_connection():
    return pymysql.connect(user='quantist',
                           passwd='quant!*#',
                           host='127.0.0.1',
                           db='stock_db',
                           charset='utf8')


def create_alchemy_engine():
    return create_engine('mysql+pymysql://quantist:quant!*#@127.0.0.1:3306/stock_db')


def get_ticker_list():
    engine = create_alchemy_engine()
    return pd.read_sql("""
        select * from kor_ticker
        where 기준일 = (select max(기준일) from kor_ticker) 
    	and 종목구분 = '보통주';
    """, con=engine)


def get_fs_q():
    engine = create_alchemy_engine()
    # 분기 재무제표 불러오기
    return pd.read_sql("""
        select * from kor_fs
        where 공시구분 = 'q'
        and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
    """, con=engine)


def save_ticker(ticker):
    query = f"""
                insert into kor_ticker (종목코드,종목명,시장구분,종가,시가총액,기준일,EPS,선행EPS,BPS,주당배당금,종목구분)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) as new
                on duplicate key update
                종목명=new.종목명,시장구분=new.시장구분,종가=new.종가,시가총액=new.시가총액,EPS=new.EPS,선행EPS=new.선행EPS,
                BPS=new.BPS,주당배당금=new.주당배당금,종목구분 = new.종목구분;
            """
    args = ticker.values.tolist()
    execute_save_query(query, args)


def save_sector(sector):
    query = f"""
                insert into kor_sector (IDX_CD, CMP_CD, CMP_KOR, SEC_NM_KOR, 기준일)
                values (%s,%s,%s,%s,%s) as new
                on duplicate key update
                IDX_CD = new.IDX_CD, CMP_KOR = new.CMP_KOR, SEC_NM_KOR = new.SEC_NM_KOR
            """
    args = sector.values.tolist()
    execute_save_query(query, args)


def save_price(price):
    query = """
                insert into kor_price (날짜, 시가, 고가, 저가, 종가, 거래량, 종목코드)
                values (%s,%s,%s,%s,%s,%s,%s) as new
                on duplicate key update
                시가 = new.시가, 고가 = new.고가, 저가 = new.저가,
                종가 = new.종가, 거래량 = new.거래량;
            """
    args = price.values.tolist()
    execute_save_query(query, args)


def save_fs(fs):
    query = """
                insert into kor_fs (계정, 기준일, 값, 종목코드, 공시구분)
                values (%s,%s,%s,%s,%s) as new
                on duplicate key update
                값=new.값
            """
    args = fs.values.tolist()
    execute_save_query(query, args)


def save_factor(factors):
    query = """
                insert into kor_value (종목코드, 기준일, 지표, 값)
                values (%s,%s,%s,%s) as new
                on duplicate key update
                값=new.값
            """
    args = factors.values.tolist()
    execute_save_query(query, args)


def execute_save_query(query, args):
    with create_connection() as con:
        with con.cursor() as cursor:
            cursor.executemany(query, args)
        con.commit()
