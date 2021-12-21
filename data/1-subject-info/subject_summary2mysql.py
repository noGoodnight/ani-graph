import json
import sys
import pymysql
sys.path.append("..")
from json2mysql.mysql_connector import db

cursor = db.cursor()

file = open("subject_summary.json", "r", encoding="utf8")

lines = file.readlines()

for i in range(0, len(lines)):
    line = lines[i]
    subject_summary_info = json.loads(line)
    subject_id = int("1" + str(subject_summary_info.get('id')))
    subject_summary = subject_summary_info.get('summary')

    subject_summary_sql = """
    update `entity` set `summary`=%s where `id`=%s
    """%(pymysql.converters.escape_str(subject_summary), subject_id)
    cursor.execute(subject_summary_sql)
db.commit()

