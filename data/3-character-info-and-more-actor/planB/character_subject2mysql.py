import json
import sys

sys.path.append("../..")
from json2mysql.mysql_connector import db

character_info_file = open("character_subject.json", "r", encoding="utf8")
content = character_info_file.read()
character_infos = json.loads(content)
cursor = db.cursor()

for character_relations in character_infos:
    for relation in character_relations:
        select_relation_sql = """
        select * from `relation` where source=%s and target=%s;
        """
        insert_relation_sql = """
        insert into `relation` (source, target, name, type) values (%s,%s,%s,%s)
        """
        cursor.execute(select_relation_sql, (relation["source"], relation["target"]))
        if len(cursor.fetchall()) > 0:
            continue
        cursor.execute(insert_relation_sql,
                       (relation["source"], relation["target"], relation["name"], relation["type"]))
        print((relation["source"], relation["target"]))
db.commit()
character_info_file.close()
