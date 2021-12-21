import json
import sys

sys.path.append("..")
from json2mysql.mysql_connector import db

cursor = db.cursor()

actors = json.loads(open("actor_info.json", "r", encoding="utf8").read())
for actor in actors:
    if len(actor) == 4:
        update_actor_sql = """
        update `entity` set `name_cn`=%s, `summary`=%s, `alias`=%s where `id`=%s
        """
        cursor.execute(update_actor_sql, (actor["name_cn"], actor["summary"], actor["alias"], actor["id"]))
    else:
        update_actor_sql = """
        update `entity` set url=%s, name=%s, name_cn=%s, summary=%s, image=%s, image_grid=%s, alias=%s
        where id=%s
        """
        cursor.execute(update_actor_sql,
                       (actor["url"], actor["name"], actor["name_cn"], actor["summary"], actor["image"],
                        actor["image_grid"], actor["alias"], actor["id"]))
    print(actor)
db.commit()
