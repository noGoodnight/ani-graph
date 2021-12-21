import html
import json


def txt2json():
    txt_file = open("actor_info_txt.json", "r", encoding="utf8")
    json_file = open("actor_info.json", "w", encoding="utf8")
    json_file.write("[\r")
    lines = txt_file.readlines()
    for i in range(0, len(lines)):
        line = lines[i]
        json_file.write(html.unescape(line[:len(line) - 1]))
        if i == len(lines) - 1:
            json_file.write("\r")
        else:
            json_file.write(",\r")
    json_file.write("]\r")
    txt_file.close()
    json_file.close()


if __name__ == '__main__':
    txt2json()
