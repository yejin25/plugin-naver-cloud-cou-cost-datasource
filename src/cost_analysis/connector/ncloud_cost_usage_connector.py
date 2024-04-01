import requests
import time
import base64
import hmac
import hashlib
import logging
from urllib import parse
from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger("cloudforet")

class NCloudCostUsageConnector(BaseConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret_data = kwargs['secret_data']  # secret_data를 클래스 속성으로 저장
        self.BASE_URL = "https://billingapi.apigw.ntruss.com"

    def make_signature(self, method, uri):
        timestamp = int(time.time() * 1000)
        timestamp = str(timestamp)

        access_key = self.secret_data['ncloud_access_key_id']  # 클래스 속성에서 access key id를 가져옴
        secret_key = self.secret_data['ncloud_secret_key']  # 클래스 속성에서 secret key를 가져옴
        secret_key = bytes(secret_key, 'UTF-8')

        message = method + " " + uri + "\n" + timestamp + "\n" + access_key
        message = bytes(message, 'UTF-8')
        signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

        return signingKey, timestamp, access_key


    def create_connection(self, method, uri, paramDict):
        query_string = parse.urlencode(paramDict, doseq=True)
        custom_uri = uri + '?' + query_string

        signingKey, timestamp, access_key = self.make_signature(method, custom_uri)

        headerDict = {}
        headerDict.setdefault('x-ncp-apigw-signature-v2', signingKey)
        headerDict.setdefault('x-ncp-apigw-timestamp', timestamp)
        headerDict.setdefault('x-ncp-iam-access-key', access_key)

        try:
            api_url = self.BASE_URL + uri
            response = requests.get(api_url, params=paramDict, headers=headerDict)
            return response.json()  # 연결에 성공하면 데이터 반환
        except requests.exceptions.RequestException as e:
            print(f"API 연결에 실패했습니다: {e}")
            return None  # 연결에 문제가 있으면 오류 메시지 출력

    def list_demand_cost(self):
        # demand_cost = []
        method = "GET"
        uri = "/billing/v1/cost/getDemandCostList"

        paramDict = {}
        paramDict.setdefault('startMonth', '202402')  # yyyyMM 형식
        paramDict.setdefault('endMonth', '202403')  # yyyyMM 형식
        paramDict.setdefault('responseFormatType', 'json')

        response = self.create_connection(method, uri, paramDict)

        data = response

        return data


