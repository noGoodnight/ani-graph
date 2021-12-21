import html
import json
import re
import time
import unicodedata

import requests

offset = len(open("staff_info_txt.json", "r", encoding="utf8").readlines())
file = open("staff_info_txt.json", "a", encoding="utf8")

staff_list = eval(open("staff_list.txt", "r", encoding="utf8").read())

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
while i < 4000:
    try:
        url = "https://bgm.tv/person/" + str(staff_list[i])[1:]
        response = requests.request("GET", url=url, headers=headers, data=payload)
        info = response.content.decode("utf8")
        unicodedata.normalize("NFKC", info)
        info = html.unescape(info)
        # 简介
        try:
            s_summary = ""
            if info.find("""div class="detail">""") > -1:
                detail = re.findall(r'<div class="detail">([\s\S]*)</div>\n<div class="section_line clear">', info)
                s_summary = detail[0].replace("<br />", "\r\n")
                summary_lines = s_summary.split("\r\n")
                summary_lines = list(map(lambda x: x.strip(), summary_lines))
                s_summary = "\r\n".join(summary_lines)
        except IndexError:
            continue
        staff_info = {
            "id": staff_list[i],
            "summary": s_summary,
        }
        file.write(json.dumps(staff_info, ensure_ascii=False))
        file.write("\r")
        print(i)
        print(staff_info)
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
