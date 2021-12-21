import json
import sys

sys.path.append("..")
from json2mysql.mysql_connector import db

cursor = db.cursor()

select_entity_sql = """
select `id`, `name` from `entity` where `name_cn`=''
"""
cursor.execute(select_entity_sql)
entity_list = cursor.fetchall()
update_entity_sql = """
update `entity` set `name_cn`=%s where `id`=%s
"""
for entity in entity_list:
    cursor.execute(update_entity_sql, (entity[1], entity[0]))
db.commit()
