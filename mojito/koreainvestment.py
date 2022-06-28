'''
한국투자증권 python wrapper
'''
import json
import asyncio
from base64 import b64decode
from multiprocessing import Process, Queue
import datetime
import requests
import websockets
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

EXCHANGE_CODE = {
    "홍콩": "HKS",
    "뉴욕": "NYS",
    "나스닥": "NAS",
    "아멕스": "AMS",
    "도쿄": "TSE",
    "상해": "SHS",
    "심천": "SZS",
    "상해지수": "SHI",
    "심천지수": "SZI",
    "호치민": "HSX",
    "하노이": "HNX"
}

# 해외주식 주문
# 해외주식 잔고
EXCHANGE_CODE2 = {
    "나스닥": "NASD",
    "뉴욕": "NYSE",
    "아멕스": "AMEX",
    "홍콩": "SEHK",
    "상해": "SHAA",
    "심천": "SZAA",
    "도쿄": "TKSE"
}

CURRENCY_CODE = {
    "나스닥": "USD",
    "뉴욕": "USD",
    "아멕스": "USD",
    "홍콩": "HKD",
    "상해": "CNY",
    "심천": "CNY",
    "도쿄": "JPY"
}

execution_items = [
    "유가증권단축종목코드", "주식체결시간", "주식현재가", "전일대비부호", "전일대비",
    "전일대비율", "가중평균주식가격", "주식시가", "주식최고가", "주식최저가",
    "매도호가1", "매수호가1", "체결거래량", "누적거래량", "누적거래대금",
    "매도체결건수", "매수체결건수", "순매수체결건수", "체결강도", "총매도수량",
    "총매수수량", "체결구분", "매수비율", "전일거래량대비등락율", "시가시간",
    "시가대비구분", "시가대비", "최고가시간", "고가대비구분", "고가대비",
    "최저가시간", "저가대비구분", "저가대비", "영업일자", "신장운영구분코드",
    "거래정지여부", "매도호가잔량", "매수호가잔량", "총매도호가잔량", "총매수호가잔량",
    "거래량회전율", "전일동시간누적거래량", "전일동시간누적거래량비율", "시간구분코드",
    "임의종료구분코드", "정적VI발동기준가"
]

orderbook_items = [
    "유가증권 단축 종목코드",
    "영업시간",
    "시간구분코드",
    "매도호가01",
    "매도호가02",
    "매도호가03",
    "매도호가04",
    "매도호가05",
    "매도호가06",
    "매도호가07",
    "매도호가08",
    "매도호가09",
    "매도호가10",
    "매수호가01",
    "매수호가02",
    "매수호가03",
    "매수호가04",
    "매수호가05",
    "매수호가06",
    "매수호가07",
    "매수호가08",
    "매수호가09",
    "매수호가10",
    "매도호가잔량01",
    "매도호가잔량02",
    "매도호가잔량03",
    "매도호가잔량04",
    "매도호가잔량05",
    "매도호가잔량06",
    "매도호가잔량07",
    "매도호가잔량08",
    "매도호가잔량09",
    "매도호가잔량10",
    "매수호가잔량01",
    "매수호가잔량02",
    "매수호가잔량03",
    "매수호가잔량04",
    "매수호가잔량05",
    "매수호가잔량06",
    "매수호가잔량07",
    "매수호가잔량08",
    "매수호가잔량09",
    "매수호가잔량10",
    "총매도호가 잔량", # 43
    "총매수호가 잔량",
    "시간외 총매도호가 잔량",
    "시간외 총매수호가 증감",
    "예상 체결가",
    "예상 체결량",
    "예상 거래량",
    "예상체결 대비",
    "부호",
    "예상체결 전일대비율",
    "누적거래량",
    "총매도호가 잔량 증감",
    "총매수호가 잔량 증감",
    "시간외 총매도호가 잔량",
    "시간외 총매수호가 증감",
    "주식매매 구분코드"
]

notice_items = [
    "고객ID", "계좌번호", "주문번호", "원주문번호", "매도매수구분", "정정구분", "주문종류",
    "주문조건", "주식단축종목코드", "체결수량", "체결단가", "주식체결시간", "거부여부",
    "체결여부", "접수여부", "지점번호", "주문수량", "계좌명", "체결종목명", "신용구분",
    "신용대출일자", "체결종목명40", "주문가격"
]


class KoreaInvestment:
    '''
    한국투자증권 REST API
    '''
    def __init__(self, api_key: str, api_secret: str, exchange: str = "서울"):
        """생성자
        Args:
            api_key (str): 발급받은 API key
            api_secret (str): 발급받은 API secret
            exchange (str): "나스닥", "뉴욕", "아멕스", "홍콩", "상해", "심천", "도쿄",
                            "하노이", "호치민"
        """
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.api_key = api_key
        self.api_secret = api_secret

        self.exchange = exchange
        assert self.exchange == "아멕스"

        self.access_token = None
        self.issue_access_token()

    def issue_access_token(self):
        """접근토큰발급
        """
        path = "oauth2/tokenP"
        url = f"{self.base_url}/{path}"
        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        self.access_token = f'Bearer {resp.json()["access_token"]}'

    def issue_hashkey(self, data: dict):
        """해쉬키 발급
        Args:
            data (dict): POST 요청 데이터
        Returns:
            _type_: _description_
        """
        path = "uapi/hashkey"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        haskkey = resp.json()["HASH"]
        return haskkey

################################################################################

    def fetch_price(self, ticker: str) -> dict:
        """해외주식 현재체결가
        Args:
            ticker (str): 종목코드
        Returns:
            dict: API 개발 가이드 참조
        """
        path = "uapi/overseas-price/v1/quotations/price"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHDFS00000300"
        }

        exchange_code = EXCHANGE_CODE[self.exchange]
        params = {
            "AUTH": "",
            "EXCD": exchange_code,
            "SYMB": ticker
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_balance(self, acc_no: str) -> dict:
        """해외주식 잔고조회
        Args:
            acc_no (str): 계좌번호 앞8자리
        Returns:
            dict: _description_
        """
        path = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
        url = f"{self.base_url}/{path}"

        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "CTRP6504R"
        }

        params = {
            'CANO': acc_no,
            'ACNT_PRDT_CD': '01',
            "WCRC_FRCR_DVSN_CD": "02",
            "NATN_CD": "840",
            "TR_MKET_CD": "00",
            "INQR_DVSN_CD": "00"
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def create_limit_buy_order(self, acc_no: str, ticker: str, price: int, quantity: int) -> dict:
        """지정가 매수

        Args:
            acc_no (str): 계좌번호
            ticker (str): 종목코드
            price (int): 가격
            quantity (int): 수량

        Returns:
            dict: _description_
        """
        resp = self.create_oversea_order("buy", acc_no, ticker, price, quantity, "00")
        return resp

    def create_limit_sell_order(self, acc_no: str, ticker: str, price: int, quantity: int) -> dict:
        """지정가 매도

        Args:
            acc_no (str): _description_
            ticker (str): _description_
            price (int): _description_
            quantity (int): _description_

        Returns:
            dict: _description_
        """
        resp = self.create_oversea_order("sell", acc_no, ticker, price, quantity, "00")
        return resp

    def cancel_order(self, acc_no: str, ticker: str, order_id: str,
                     quantity: int) -> dict:
        """주문 취소

        Args:
            acc_no (str): _description_
            order_code (str): _description_
            order_id (str): _description_
            order_type (str): _description_
            price (int): _description_
            quantity (int): _description_

        Returns:
            _type_: _description_
        """
        resp = self.update_oversea_order(acc_no, ticker, order_id, 0, quantity, False)
        return resp

    def fetch_open_order(self, acc_no: str) -> dict:
        """_summary_

        Args:
            acc_no (str): _description_

        Returns:
            dict: _description_
        """
        path = "uapi/overseas-stock/v1/trading/inquire-nccs"
        url = f"{self.base_url}/{path}"

        headers = {
            "content-type": "application/json",
            "authorization": self.access_token,
            "appKey": self.api_key,
            "appSecret": self.api_secret,
            "tr_id": "JTTT3018R"
        }

        exchange_cd = EXCHANGE_CODE2[self.exchange]
        params = {
            "CANO": acc_no,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": exchange_cd,
            "SORT_SQN": "DS",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": ""
        }

        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def create_oversea_order(self, side: str, acc_no: str, ticker: str, price: int,
                             quantity: int, order_type: str) -> dict:
        """_summary_

        Args:
            side (str): _description_
            acc_no (str): _description_
            ticker (str): _description_
            price (int): _description_
            quantity (int): _description_
            order_type (str): _description_

        Returns:
            dict: _description_
        """
        path = "uapi/overseas-stock/v1/trading/order"
        url = f"{self.base_url}/{path}"

        if side == "buy":
            tr_id = "JTTT1002U"
        else:
            tr_id = "JTTT1006U"

        exchange_cd = EXCHANGE_CODE2[self.exchange]
        data = {
            "CANO": acc_no,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": exchange_cd,
            "PDNO": ticker,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": order_type
        }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": tr_id,
           "hashkey": hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def update_oversea_order(self, acc_no: str, ticker: str, order_id: str,
                             price: int, quantity: int, is_change: bool = True):
        """_summary_

        Args:
            acc_no (str): _description_
            ticker (str): _description_
            order_id (str): _description_
            price (int): _description_
            quantity (int): _description_
            is_change (bool): _description_

        Returns:
            dict: _desciption_
        """
        path = "uapi/overseas-stock/v1/trading/order-rvsecncl"
        url = f"{self.base_url}/{path}"
        param = "01" if is_change else "02"
        exchange_cd = EXCHANGE_CODE2[self.exchange]
        data = {
            "CANO": acc_no,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": exchange_cd,
            "PDNO": ticker,
            "ORGN_ODNO": order_id,
            "RVSE_CNCL_DVSN_CD": param,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": "",
            "CTAC_TLNO": "",
            "MGCO_APTM_ODNO": "",
            "ORD_SVR_DVSN_CD": "0"
        }
        hashkey = self.issue_hashkey(data)
        headers = {
            "content-type": "application/json",
            "authorization": self.access_token,
            "appKey": self.api_key,
            "appSecret": self.api_secret,
            "tr_id": "JTTT1004U",
            "hashkey": hashkey
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

