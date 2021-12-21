import json
import sys

import pymysql.err

sys.path.append("../..")
from json2mysql.mysql_connector import db

cursor = db.cursor()
character_relation_completion_file = open("character_actor.json")
infos = json.loads(character_relation_completion_file.read())

for info in infos:
    for actor in info["actors"]:
        select_actor_sql = """select * from `entity` where id=%s""" % actor["id"]
        cursor.execute(select_actor_sql)
        if len(cursor.fetchall()) != 0:
            continue
        insert_actor_sql = """insert into `entity` (id) values (%s)""" % actor["id"]
        cursor.execute(insert_actor_sql)
        print("insert actor", actor["id"])
    for relation in info["relations"]:
        select_relation_sql = """select * from `relation` where source=%s and target=%s"""
        cursor.execute(select_relation_sql, (relation["source"], relation["target"]))
        if len(cursor.fetchall()) != 0:
            continue
        insert_relation_sql = """insert into `relation` (source, target, name, type) values (%s, %s, %s, %s)"""
        cursor.execute(insert_relation_sql,
                       (relation["source"], relation["target"], relation["name"], relation["type"]))
        print("insert relation", relation["source"], relation["target"])
cursor.close()
db.commit()
character_relation_completion_file.close()
