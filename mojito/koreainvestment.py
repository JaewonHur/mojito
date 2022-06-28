'''
한국투자증권 python wrapper
'''
import json
import requests

class KoreaInvestment:
    '''
    KoreaInvestment REST API
    '''
    def __init__(self, api_key: str, api_secret: str):
        """
        Args:
            api_key (str): API key
            api_secret (str): API secret
        """
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.api_key = api_key
        self.api_secret = api_secret

        self.exchange = "AMEX"

        self.access_token = None
        self.issue_access_token()

    def issue_access_token(self):
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
        """
        Args:
            data (dict): Data to post
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
        """
        Args:
            ticker (str): code
        Returns:
            dict: see api document
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

        exchange_code = "AMS"
        params = {
            "AUTH": "",
            "EXCD": exchange_code,
            "SYMB": ticker
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_balance(self, acc_no: str) -> dict:
        """
        Args:
            acc_no (str): account number
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
        """

        Args:
            acc_no (str): account number
            ticker (str): code
            price (int): price
            quantity (int): quantity

        Returns:
            dict: _description_
        """
        resp = self.create_oversea_order("buy", acc_no, ticker, price, quantity, "00")
        return resp

    def create_limit_sell_order(self, acc_no: str, ticker: str, price: int, quantity: int) -> dict:
        """

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
        """

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

        params = {
            "CANO": acc_no,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": self.exchange,
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

        data = {
            "CANO": acc_no,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": self.exchange,
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
        data = {
            "CANO": acc_no,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": self.exchange,
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

