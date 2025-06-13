import json
import os
import sys
import time
import traceback
from datetime import datetime

import oss2
import requests
from oss2.models import CnameInfo
from requests import HTTPError, Timeout, RequestException


def _request(method, url, retries=3, **kwargs):
    for attempt in range(retries):
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except (HTTPError, Timeout) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except RequestException as e:
            print(f"Request failed: {e}")
            break
    return None


class OSS:
    def __init__(self, access_key_id, access_key_secret, endpoint, bucket_name, region):
        self.auth = oss2.AuthV4(access_key_id, access_key_secret)
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.region = region
        self.bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name=self.bucket_name, region=self.region)

    def run_update(self, target_cname: str, private_key: str, certificate: str):
        cname_info = self._get_matched_cname(target_cname)
        if cname_info and private_key and certificate:
            self._update_cname(cname_info, private_key, certificate)
        else:
            print("未找到匹配的自定义域名或证书信息不完整")
            sys.exit(1)

    def _get_matched_cname(self, target_cname: str) -> CnameInfo | None:
        cname_list = self.get_cname_info()
        for c in cname_list:
            if c.domain == target_cname:
                return c
            else:
                return None

    def get_cname_info(self, isprint: bool = False) -> list:
        list_result = self.bucket.list_bucket_cname()
        if isprint:
            for c in list_result.cname:
                print(f"证书 ID ： {c.certificate.cert_id}")  # 打印证书ID
                print(f"自定义域名： {c.domain}")  # 打印自定义域名
                print(f"最后修改时间： {c.last_modified}")  # 打印绑定自定义域名的时间
        return list_result.cname

    def _update_cname(self, cname_info: CnameInfo, private_key: str, certificate: str):
        # 检查是否已绑定证书和证书是否过期
        create_new_cert = True  # 默认创建一个新的证书
        if cname_info.certificate:
            exp_date_obj = datetime.strptime(cname_info.certificate.valid_end_date, '%b %d %H:%M:%S %Y GMT')
            if exp_date_obj > datetime.utcnow():  # 证书未过期
                create_new_cert = False

        if create_new_cert:  # 如果没有绑定证书，直接传入证书内容，会创建一个新的证书
            print("证书已过期或未绑定证书，将创建新的证书")
            cert = oss2.models.CertInfo(certificate=certificate, private_key=private_key, force=True)
        else:  # 如果已经绑定了证书且证书未过期, 传入证书ID可以直接更新证书，避免创建一个新的
            print("证书未过期，将更新证书")
            cert = oss2.models.CertInfo(cert_id=cname_info.certificate.cert_id, certificate=certificate,
                                        private_key=private_key, force=True)

        input_ = oss2.models.PutBucketCnameRequest(cname_info.domain, cert)
        self.bucket.put_bucket_cname(input_)


if __name__ == '__main__':
    os.chdir(sys.path[0])

    try:
        # 读取配置文件
        with open("config.json", "r") as file:
            config = json.load(file)
        
        access_key_id = config['Auth']['alibaba_cloud_access_key_id']
        access_key_secret = config['Auth']['alibaba_cloud_access_key_secret']

        for each in config['OSS']:
            # 从配置文件中读取配置信息
            private_key_path = each['private_key_path']
            certificate_path = each['certificate_path']

            # 读取证书文件
            with open(private_key_path, 'r') as f:
                private_key_ = f.read()
            with open(certificate_path, 'r') as f:
                certificate_ = f.read()

            # 读取自定义域名
            target_cname_ = each['target_cname']

            o = OSS(
                access_key_id,
                access_key_secret,
                each['endpoint'],
                each['bucket_name'],
                each['region']
            )

            o.run_update(target_cname=target_cname_, private_key=private_key_, certificate=certificate_)

    except KeyboardInterrupt:
        print("程序已被用户终止")
    except Exception as e:
        print(traceback.format_exc())
        sys.exit(1)