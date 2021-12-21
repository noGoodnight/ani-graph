import json
import sys

sys.path.append("..")
from json2mysql.mysql_connector import db

cursor = db.cursor()

staffs = json.loads(open("staff_info.json", "r", encoding="utf8").read())
for staff in staffs:
    update_staff_sql = """
    update `entity` set `summary`=%s where `id`=%s
    """
    cursor.execute(update_staff_sql, (staff["summary"], staff["id"]))
db.commit()
