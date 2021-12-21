import html
import json
import time
import unicodedata

import requests
import sys

sys.path.append("..")
from json2mysql.mysql_connector import db

line_separator = '\r'
subject_info_file = open("subject_info_txt.json", "r", encoding="utf8")
lines = subject_info_file.readlines()
start = len(lines)
subject_info_file.close()
subject_info_file = open("subject_info_txt.json", "a", encoding="utf8")

subject_list_file = open("subject_list.txt","r",encoding="utf8")
subject_list = eval(subject_list_file.read())

payload = {}
headers = {
    'authority': 'api.bgm.tv',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'chii_sec_id=VvpJJxi7axf0zlCLPiffPVvtt5j19NNnM8Bd; chii_cookietime=2592000; chii_auth=VfMfIB28aRPkyB%2BdPSDVQxuJysiIp5QWKs1d9KSf98F%2BvIe6oJXrp9ZZhY3rm8b3sepTc6r9qD7J7n0dsjr7HJQ5wr50fdmdMcl5; chii_sid=eSSgPK; chii_sid=a44xT6; chii_sec_id=qETt46HnpNxGm2k2x%2Buh9pPDUVFCie5fIG41; chii_sid=2v0rvV; chii_sec_id=qES6v6Xg9dRGm2k2x%2Buh9pPDUVFC%2BOxNaHFf; chii_sid=PAm8U8',
}

i = start
while i < len(subject_list):
    try:
        subject_id = subject_list[i]
        url = "https://api.bgm.tv/subject/" + str(subject_id) + "?responseGroup=large"
        response = requests.request("GET", url=url, headers=headers, data=payload)
        info = json.loads(response.content.decode("utf8"))
        info = {
            "id": info["id"],
            "url": info["url"],
            "name": info["name"],
            "name_cn": info["name_cn"],
            "summary": info["summary"],
            "eps": info["eps"],
            "air_date": info["air_date"],
            "images": info["images"],
            "crt": info["crt"],
            "staff": info["staff"]
        }
        info = json.dumps(info, ensure_ascii=False)
        unicodedata.normalize("NFKC", info)
        info = html.unescape(info)
        subject_info_file.write(info)
        subject_info_file.write(line_separator)
        response.close()
        print(subject_id)
        i += 1
    except requests.exceptions.ProxyError as e:
        print(e)
        time.sleep(180)
        continue
    except requests.exceptions.SSLError as e:
        print(e)
        time.sleep(180)
        continue
    except requests.exceptions.ConnectionError as e:
        print(e)
        time.sleep(180)
        continue
    except KeyboardInterrupt as e:
        break
subject_info_file.close()
