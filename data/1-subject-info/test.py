import html
import json


def txt2json():
    txt_file = open("subject_info_txt.json", "r", encoding="utf8")
    json_file = open("subject_info.json", "w", encoding="utf8")
    json_file.write("[\r")
    lines = txt_file.readlines()
    for i in range(0, len(lines)):
        line = lines[i]
        contents = line.split("\"eps\"")
        contents_2 = contents[1].split("\"air_date\"")
        line = contents[0] + "\"eps\": " + str(contents_2[0].count("id")) + ", \"air_date\""+contents_2[1]
        json_file.write(html.unescape(line[:len(line) - 1]))
        if i == len(lines)-1:
            json_file.write("\r")
        else:
            json_file.write(",\r")
    json_file.write("]\r")
    txt_file.close()
    json_file.close()


if __name__ == '__main__':
    lines = open("subject_summary.json","r",encoding="utf8").readlines()
    result = []
    for line in lines:
        info = json.loads(line)
        if info["id"] not in result:
            result.append(info["id"])
        else:
            print(info["id"])
    print(len(result))
