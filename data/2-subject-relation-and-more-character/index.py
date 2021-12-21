import html
import json
import time
import unicodedata

import requests
import re
import sys
sys.path.append("..")
from json2mysql.mysql_connector import db

line_separator = '\r'
file = open("subject_relation_and_character_txt.json", "r", encoding="utf8")
offset = len(file.readlines())
file.close()
file = open("subject_relation_and_character_txt.json", "a", encoding="utf8")

cursor = db.cursor()
select_subject_sql = """select id from `entity` where id like concat('1', '%')"""
cursor.execute(select_subject_sql)
subject_list = cursor.fetchall()

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

i = 0
while i < len(subject_list):
    subject_id = subject_list[i][0]
    url_1 = "https://bgm.tv/subject/" + str(subject_id)[1:]
    url_2 = "https://bgm.tv/subject/" + str(subject_id)[1:] + "/characters"
    subject_result = {
        "id": subject_id,
        "relations": [],
        "characters": [],
        "alias": "",
    }

    try:
        response_1 = requests.request("GET", url=url_1, headers=headers, data=payload)
        info_1 = response_1.content.decode("utf8")
        unicodedata.normalize("NFKC", info_1)
        info_1 = html.unescape(info_1)

        # 别名补全
        subject_alias = ""
        left_limit = 0
        while True:
            left_index = info_1[left_limit:].find("别名: </span>") + left_limit
            if left_index == left_limit - 1:
                break
            else:
                right_index = left_index + info_1[left_index:].find("</li>")
                subject_alias += info_1[left_index + 11:right_index]
                subject_alias += ";"
                left_limit = right_index
        if subject_alias != "":
            subject_alias = subject_alias[:len(subject_alias) - 1]
            unicodedata.normalize("NFKC", subject_alias)
            subject_alias = html.unescape(subject_alias)
        subject_result["alias"] = subject_alias
        print(subject_id, subject_alias)

        # 关系补全
        infos = info_1.split("subject_section")
        info_1 = None
        for j in range(0, len(infos)):
            if infos[j].find("关联条目") > -1:
                info_1 = infos[j]
                break
        if info_1 is None:
            print("no 关联条目")
            file.close()
            break
        re_subject_finder = re.compile(r'<a href="/subject/(\d*)"')
        subjects = list(set(map(lambda x: int(x), re_subject_finder.findall(info_1))))
        for s_id in subjects:
            related_subject_id = int("1" + str(s_id))
            if related_subject_id != subject_id:
                select_entity_sql = """select id,name,name_cn from `entity` where id=%s""" % related_subject_id
                cursor.execute(select_entity_sql)
                result_1 = cursor.fetchall()
                if len(result_1) != 0:
                    select_series_relation_sql = """
                    select * from `relation` where source=%s and target=%s
                    """ % (min(subject_id, related_subject_id), max(subject_id, related_subject_id))
                    cursor.execute(select_series_relation_sql)
                    select_series_relation_result = cursor.fetchall()
                    if len(select_series_relation_result) == 0:
                        series_relation = {
                            "source": min(subject_id, related_subject_id),
                            "target": max(subject_id, related_subject_id),
                            "name": "系列",
                            "type": "series",
                        }
                        subject_result["relations"].append(series_relation)
                        print(result_1)
        response_1.close()

        # 角色补全
        response_2 = requests.request("GET", url=url_2, headers=headers, data=payload)
        info_2 = response_2.content.decode("utf8")
        unicodedata.normalize("NFKC", info_2)
        info_2 = html.unescape(info_2)

        re_character_id_finder = re.compile(r'<a href="/character/(\d*)"')
        characters = list(set(map(lambda x: int(x), re_character_id_finder.findall(info_2))))
        for c_id in characters:
            select_character_by_id_sql = """select id,name,name_cn from `entity` where id = %s""" % (
                int("2" + str(c_id)))
            cursor.execute(select_character_by_id_sql)
            result_2 = cursor.fetchall()
            if len(result_2) == 0:
                character = {
                    "id": int("2" + str(c_id))
                }
                subject_result["characters"].append(character)
                perform_relation = {
                    "source": int("2" + str(c_id)),
                    "target": subject_id,
                    "type": "perform",
                }
                print(result_2, "insert", c_id)
        response_2.close()

        file.write(json.dumps(subject_result, ensure_ascii=False))
        file.write("\r")
        i += 1
    except Exception as e:
        time.sleep(180)
    except KeyboardInterrupt:
        break
file.close()
