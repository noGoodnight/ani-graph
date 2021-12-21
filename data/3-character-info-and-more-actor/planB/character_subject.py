import json
import time

import bs4
import requests
import re
import sys
from bs4 import BeautifulSoup

sys.path.append("..")
# from json2mysql.mysql_connector import db

line_separator = '\r'
character_actor_relation_file = open("character_subject_txt.json", "r", encoding="utf8")
lines = character_actor_relation_file.readlines()
start = len(lines)
character_actor_relation_file.close()
character_actor_relation_file = open("character_subject_txt.json", "a", encoding="utf8")

# cursor = db.cursor()
# select_character_sql = """select id from `entity` where id like concat('2', '%')"""
# cursor.execute(select_character_sql)
character_list = eval(open("character_list.txt", "r", encoding="utf8").read())
subject_list = eval(open("subject_list.txt", "r", encoding="utf8").read())

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
while i < len(character_list):
    try:
        c_id = character_list[i]
        url = "https://bgm.tv/character/" + str(c_id)[1:]
        response = requests.request("GET", url=url, headers=headers, data=payload)
        info = response.content.decode("utf8")
        soup = BeautifulSoup(info, "html.parser")
        subjects = soup.select("div.innerLeftItem")
        relations = []

        for subject in subjects:
            subject_id = subject.select("a.subjectCover")
            if len(subject_id) > 0:
                subject_id = int(subject_id[0].attrs["href"].split("/subject/")[1])
                if subject_id in subject_list:
                    relation_name = subject.select("span.badge_job")[0].contents[0]
                    relations.append({
                        "source": c_id,
                        "target": int("1" + str(subject_id)),
                        "name": relation_name,
                        "type": "perform"
                    })
        character_actor_relation_file.write(json.dumps(relations, ensure_ascii=False))
        character_actor_relation_file.write("\r")
        print(i)
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
character_actor_relation_file.close()
