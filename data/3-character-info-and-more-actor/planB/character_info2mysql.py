import json
import sys

sys.path.append("../..")
from json2mysql.mysql_connector import db

character_info_file = open("character_info.json", "r", encoding="utf8")
content = character_info_file.read()
character_infos = json.loads(content)
cursor = db.cursor()

for character_info in character_infos:
    print(character_info["id"])
    if len(character_info) == 2:
        insert_character_info_sql = """
        update `entity` set summary=%s
        where id=%s
        """
        character_info_values = (
            character_info.get("summary"),
            character_info.get("id")
        )
        cursor.execute(insert_character_info_sql, character_info_values)
    else:
        insert_character_info_sql = """
        update `entity` set url=%s, name=%s, name_cn=%s, summary=%s, image=%s, image_grid=%s, alias=%s
        where id=%s
        """
        character_info_values = (
            character_info.get("url"),
            character_info.get("name"),
            character_info.get("name_cn"),
            character_info.get("summary"),
            character_info.get("image"),
            character_info.get("image_grid"),
            character_info.get("alias"),
            character_info.get("id")
        )
        cursor.execute(insert_character_info_sql, character_info_values)
db.commit()
character_info_file.close()
