import html
import json
import re
import time
import unicodedata

import requests

offset = len(open("actor_info_txt.json", "r", encoding="utf8").readlines())
file = open("actor_info_txt.json", "a", encoding="utf8")

actor_list = json.loads(open("actor_list.txt", "r", encoding="utf8").read())

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
while i < 2000:
    try:
        actor = actor_list[i]
        a_id = actor["id"]
        a_url = actor["url"]

        if a_url is not None:
            url = a_url
        else:
            url = "https://bgm.tv/person/" + str(a_id)[1:]
        response = requests.request("GET", url=url, headers=headers, data=payload)
        info = response.content.decode("utf8")
        unicodedata.normalize("NFKC", info)
        info = html.unescape(info)
        # 中文名
        a_name = ""
        a_name_cn = ""
        try:
            re_names_finder = re.compile(r'<h1 class="nameSingle">\n([\s\S]*)</h1>\n<div class="subjectNav">')
            names = re_names_finder.findall(info)[0]
            names = names.replace("<br />", "\r\n")
            re_name_finder = re.compile(r'>([\s\S]*)</a>')
            a_name = re_name_finder.findall(names)[0]
        except IndexError as e:
            continue
        re_name_cn_finder = re.compile(r'<small class="grey">([\s\S]*)</small>')
        a_name_cn = re_name_cn_finder.findall(names)
        if len(a_name_cn) == 0:
            a_name_cn = a_name
        else:
            a_name_cn = re_name_cn_finder.findall(names)[0]
        # 简介
        try:
            a_summary = ""
            if info.find("""div class="detail">""") > -1:
                detail = re.findall(r'<div class="detail">([\s\S]*)</div>\n<div class="section_line clear">', info)
                a_summary = detail[0].replace("<br />", "\r\n")
                summary_lines = a_summary.split("\r\n")
                summary_lines = list(map(lambda x: x.strip(), summary_lines))
                a_summary = "\r\n".join(summary_lines)
        except IndexError:
            continue
        # 别名
        a_alias = ""
        aliases = []
        left_limit = 0
        while True:
            left_index = info[left_limit:].find("别名: </span>") + left_limit
            if left_index == left_limit - 1:
                break
            else:
                right_index = left_index + info[left_index:].find("</li>")
                a_alias += info[left_index + 11:right_index]
                a_alias += ";"
                left_limit = right_index
        if a_alias != "":
            a_alias = a_alias[:len(a_alias) - 1]

        if a_url is None:
            a_url = url
            re_image_finder = re.compile(r'<div class="infobox">\n([\s\S]*)\n<ul id="infobox">')
            image_text = re_image_finder.findall(info)
            if len(image_text) == 0:
                a_image = None
                a_image_grid = None
            else:
                image_text = image_text[0]
                re_image_finder = re.compile(r'<a href="([\s\S]*)" class="cover thickbox"')
                a_image = re_image_finder.findall(image_text)[0]
                a_image = "http://lain.bgm.tv/pic/crt/l" + a_image.split("pic/crt/")[1][1:].split("jpg")[0] + "jpg"
                a_image_grid = "http://lain.bgm.tv/pic/crt/g" + a_image.split("http://lain.bgm.tv/pic/crt/l")[1]
            actor_info = {
                "id": a_id,
                "url": a_url,
                "name": a_name,
                "name_cn": a_name_cn,
                "summary": a_summary,
                "image": a_image,
                "image_grid": a_image_grid,
                "alias": a_alias,
            }
        else:
            actor_info = {
                "id": a_id,
                "name_cn": a_name_cn,
                "summary": a_summary,
                "alias": a_alias,
            }
        file.write(json.dumps(actor_info, ensure_ascii=False))
        file.write("\r")
        print(i)
        print(actor_info)
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
file.close()
