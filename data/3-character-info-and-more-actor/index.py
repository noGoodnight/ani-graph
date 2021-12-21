# 写了没跑，用的planB

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
character_info_file = open("character_info_and_actor_txt.json", "r", encoding="utf8")
lines = character_info_file.readlines()
offset = len(lines)
character_info_file.close()
character_info_file = open("character_info_and_actor_txt.json", "a", encoding="utf8")

cursor = db.cursor()
select_character_sql = """select id, name from `entity` where id like concat('2', '%')"""
cursor.execute(select_character_sql)
character_list = cursor.fetchall()

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

i = offset + 0
while i < len(character_list):

    try:
        c_id = character_list[i][0]
        c_name = character_list[i][1]
        print(c_id, c_name)
        url = "https://bgm.tv/character/" + str(c_id)[1:]
        response = requests.request("GET", url=url, headers=headers, data=payload)
        info = response.content.decode("utf8")

        relations = {
            "actors":[],
            "relations":[],
        }
        # 声优
        re_actor_finder = re.compile(r'<a href="/person/(\d*)"')
        actors = re_actor_finder.findall(info)
        if len(actors) > 0:
            actors = list(set(map(lambda x: int(x), actors)))
            if len(actors) == 0:
                print("no actor", c_id)
                break
            for actor_id in actors:
                select_actor_sql = """select * from `entity` where id=%s"""
                cursor.execute(select_actor_sql, int("3" + str(actor_id)))
                select_actor_result = cursor.fetchall()
                if len(select_actor_result) == 0:
                    relations["actors"].append({"id": int("3" + str(actor_id))})
                    print("insert actor", int("3" + str(actor_id)))
                    select_actor_result = [[int("3" + str(actor_id))]]

                select_actor_relation_sql = """select * from `relation` where source=%s and target=%s"""
                cursor.execute(select_actor_relation_sql, (select_actor_result[0][0], c_id))
                select_actor_relation_result = cursor.fetchall()
                if len(select_actor_relation_result) > 0:
                    continue
                else:
                    actor_relation = {
                        "source": select_actor_result[0][0],
                        "target": c_id,
                        "name": "配音",
                        "type": "actor",
                    }
                    relations["relations"].append(actor_relation)
                    print("insert relation", actor_relation)

        # 简介
        if info.find("""div class="detail">""") > -1:
            detail = re.findall(r'<div class="detail">([\s\S]*)</div>\n<div class="section_line clear">', info)
            try:
                c_summary = detail[0].replace("<br />", "\r\n")
                unicodedata.normalize("NFKC", c_summary)
                c_summary = html.unescape(c_summary)
            except IndexError as e:
                continue
            summary_lines = c_summary.split("\r\n")
            summary_lines = list(map(lambda x: x.strip(), summary_lines))
            c_summary = "\r\n".join(summary_lines)
            # print(c_summary)
        else:
            c_summary = ""
        c_info = {}
        if c_name is not None:
            c_info = {
                "id": c_id,
                "summary": c_summary,
                "actors": relations["actors"],
                "relations":relations["relations"],
            }
        else:
            try:
                re_names_finder = re.compile(r'<h1 class="nameSingle">\n([\s\S]*)</h1>\n<div class="subjectNav">')
                names = re_names_finder.findall(info)[0]
                names = names.replace("<br />", "\r\n")
                unicodedata.normalize("NFKC", names)
                names = html.unescape(names)
                re_name_finder = re.compile(r'>([\s\S]*)</a>')
                c_name = re_name_finder.findall(names)[0]
            except IndexError as e:
                continue
            re_name_cn_finder = re.compile(r'<small class="grey">([\s\S]*)</small>')
            c_name_cn = re_name_cn_finder.findall(names)
            if len(c_name_cn) == 0:
                c_name_cn = c_name
            else:
                c_name_cn = re_name_cn_finder.findall(names)[0]
            aliases = []
            left_limit = 0
            while True:
                left_index = info[left_limit:].find("别名: </span>") + left_limit
                if left_index == left_limit - 1:
                    break
                else:
                    right_index = left_index + info[left_index:].find("</li>")
                    aliases.append(info[left_index + 11:right_index])
                    left_limit = right_index
            c_alias = ""
            for alias in aliases:
                c_alias += alias
                c_alias += ";"
            if c_alias != "":
                c_alias = c_alias[:len(c_alias) - 1]
            c_alias.replace("<br />", "\r\n")
            unicodedata.normalize("NFKC", c_alias)
            c_alias = html.unescape(c_alias)
            c_url = url
            re_image_finder = re.compile(r'<div class="infobox">\n([\s\S]*)\n<ul id="infobox">')
            image_text = re_image_finder.findall(info)
            if len(image_text) == 0:
                c_image = None
                c_image_grid = None
            else:
                image_text = image_text[0]
                re_image_finder = re.compile(r'<a href="([\s\S]*)" class="cover thickbox"')
                c_image = re_image_finder.findall(image_text)[0]
                c_image = "http://lain.bgm.tv/pic/crt/l" + c_image.split("pic/crt/")[1][1:].split("jpg")[0] + "jpg"
                c_image_grid = "http://lain.bgm.tv/pic/crt/g" + c_image.split("http://lain.bgm.tv/pic/crt/l")[1]
            c_info = {
                "id": c_id,
                "url": c_url,
                "name": c_name,
                "name_cn": c_name_cn,
                "summary": c_summary,
                "image": c_image,
                "image_grid": c_image_grid,
                "alias": c_alias,
                "actors": relations["actors"],
                "relations":relations["relations"],
            }
        character_info_file.write(json.dumps(c_info, ensure_ascii=False))
        character_info_file.write(line_separator)
        response.close()
        # time.sleep(0.5)
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
character_info_file.close()
