import json
import sys

import pymysql

sys.path.append("..")
from json2mysql.mysql_connector import db

cursor = db.cursor()
infos = json.loads(open("subject_relation_and_character.json", "r", encoding="utf8").read())

for subject_info in infos:
    subject_id = subject_info["id"]
    relations = subject_info["relations"]
    characters = subject_info["characters"]
    alias = subject_info["alias"]
    insert_series_relation_sql = """
    insert into `relation` (source, target, name, type) values(%s,%s,%s,%s)
    """
    insert_character_sql = """
    insert into `entity` (id) values (%s)
    """
    update_subject_alias_sql = """
    update `entity` set alias=%s where id=%s
    """

    for relation in relations:
        # print(relation)
        try:
            cursor.execute(insert_series_relation_sql,
                       (relation["source"], relation["target"], relation["name"], relation["type"]))
        except pymysql.err.IntegrityError:
            continue
    for character in characters:
        # print(character)
        try:
            cursor.execute(insert_character_sql, character["id"])
        except pymysql.err.IntegrityError:
            continue
    cursor.execute(update_subject_alias_sql, (alias, subject_id))
    print(subject_id)
db.commit()
