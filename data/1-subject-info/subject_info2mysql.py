import copy
import json
import pymysql
import sys

sys.path.append("..")
from json2mysql.mysql_connector import db


def get_alias(alias) -> str:
    res = ""
    aliases = []
    if type(alias) is list:
        aliases = alias
    elif type(alias) is dict:
        aliases = list(alias.values())
    elif type(alias) is str:
        aliases.append(alias)
    for a in aliases:
        res += a
        res += ";"
    res = res[:len(res) - 1]
    return res


def insert_relation(relation: dict, cursor: pymysql.connections.Cursor):
    relation_search_sql = """
    select count(*) from `relation` where source = '%s' and target = '%s'
    """ % (relation["source"], relation["target"])
    cursor.execute(relation_search_sql)
    res = cursor.fetchall()[0][0]
    if res != 0:
        return False
    relation_sql = """
    INSERT INTO `relation`(source,target,name,type)
    VALUES (%s,%s,%s,%s)
    """
    r_values = (relation["source"], relation["target"], relation["name"], relation["type"])
    cursor.execute(relation_sql, r_values)
    return True


def insert_subject(subject: dict, cursor: pymysql.connections.Cursor):
    # id前缀1代表动漫
    id = int("1" + str(subject.get("id")))
    subject_search_sql = """select count(*) from `entity` where id = '%s'""" % (id)
    cursor.execute(subject_search_sql)
    res = cursor.fetchall()[0][0]
    if res != 0:
        return False
    url = subject.get('url')
    name = subject.get('name')
    name_cn = subject.get('name_cn')
    summary = subject.get('summary')
    images = subject.get('images')
    image = None
    image_grid = None
    if images:
        image = images.get('large')
        image_grid = images.get('grid')
        if not image:
            image = images.get('common')
        if not image:
            image = images.get('medium')
        if not image:
            image = images.get('small')
        if not image:
            image = images.get('grid')
    air_date = subject.get('air_date')
    if air_date == "0000-00-00":
        air_date = None
    ep_num = subject.get("eps")

    subject_sql = """
    INSERT INTO `entity`(id,url,name,name_cn,summary,image,image_grid,air_date,ep_num)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    values = (id, url, name, name_cn, summary, image, image_grid, air_date, ep_num)
    cursor.execute(subject_sql, values)
    print(id)
    return True


def insert_character(character: dict, cursor: pymysql.connections.Cursor):
    # id前缀2代表角色
    c_id = int("2" + str(character.get("id")))
    character_search_sql = """select count(*) from `entity` where id = '%s'""" % (c_id)
    cursor.execute(character_search_sql)
    res = cursor.fetchall()[0][0]
    if res != 0:
        return False
    c_url = character.get("url")
    c_name = character.get("name")
    c_name_cn = character.get("name_cn")
    c_images = character.get("images")
    c_image = None
    c_image_grid = None
    if c_images:
        c_image = c_images.get('large')
        c_image_grid = c_images.get('grid')
        if not c_image:
            c_image = c_images.get('common')
        if not c_image:
            c_image = c_images.get('medium')
        if not c_image:
            c_image = c_images.get('small')
        if not c_image:
            c_image = c_images.get('grid')
    c_alias = ""
    if character.get("info") is not None and character.get("info").get("alias") is not None:
        c_alias = get_alias(character.get("info").get("alias"))

    character_sql = """
    INSERT INTO `entity`(id,url,name,name_cn,image,image_grid,alias)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    c_values = (c_id, c_url, c_name, c_name_cn, c_image, c_image_grid, c_alias)
    cursor.execute(character_sql, c_values)
    return True


def insert_actor(actor: dict, cursor: pymysql.connections.Cursor):
    a_id = int("3" + str(actor.get("id")))
    actor_search_sql = """select count(*) from `entity` where id = '%s'""" % (a_id)
    cursor.execute(actor_search_sql)
    res = cursor.fetchall()[0][0]
    if res != 0:
        return False
    a_url = actor.get("url")
    a_name = actor.get("name")
    a_images = actor.get("images")
    a_image = None
    a_image_grid = None
    if a_images:
        a_image = a_images.get('large')
        a_image_grid = a_images.get('grid')
        if not a_image:
            a_image = a_images.get('common')
        if not a_image:
            a_image = a_images.get('medium')
        if not a_image:
            a_image = a_images.get('small')
        if not a_image:
            a_image = a_images.get('grid')

    actor_sql = """
    INSERT INTO `entity`(id,url,name,image,image_grid)
    VALUES (%s,%s,%s,%s,%s)
    """
    a_values = (a_id, a_url, a_name, a_image, a_image_grid)
    cursor.execute(actor_sql, a_values)
    # print(a_id)
    return True


def insert_staff(staff: dict, cursor: pymysql.connections.Cursor):
    s_id = int("4" + str(staff.get("id")))
    staff_search_sql = """select count(*) from `entity` where id = '%s'""" % (s_id)
    cursor.execute(staff_search_sql)
    res = cursor.fetchall()[0][0]
    if res != 0:
        return False
    s_url = staff.get("url")
    s_name = staff.get("name")
    s_name_cn = staff.get("name_cn")
    s_images = staff.get("images")
    s_image = None
    s_image_grid = None
    if s_images:
        s_image = s_images.get('large')
        s_image_grid = s_images.get('grid')
        if not s_image:
            s_image = s_images.get('common')
        if not s_image:
            s_image = s_images.get('medium')
        if not s_image:
            s_image = s_images.get('small')
        if not s_image:
            s_image = s_images.get('grid')
    s_alias = ""
    if staff.get("info") is not None and staff.get("info").get("alias") is not None:
        s_alias = get_alias(staff.get("info").get("alias"))

    staff_sql = """
    INSERT INTO `entity`(id,url,name,name_cn,image,image_grid,alias)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    s_values = (s_id, s_url, s_name, s_name_cn, s_image, s_image_grid, s_alias)
    cursor.execute(staff_sql, s_values)
    # print(s_id)
    return True


if __name__ == '__main__':
    line_separator = "\r"
    cursor = db.cursor()

    file = open("subject_info.json", "r", encoding="utf8")
    content = file.read()
    file.close()

    while True:
        try:
            subject_infos = json.loads(content)
            break
        except json.decoder.JSONDecodeError as e:
            print(e.lineno)
            index = e.pos - 1
            db_qoute_index = []
            tmp_doc = copy.copy(e.doc)
            while tmp_doc[index] != ":":
                # print(tmp_doc[index], tmp_doc[index - 1])
                if tmp_doc[index] == "\"" and tmp_doc[index - 1] != "\\" and not (
                        tmp_doc[index - 2:index] == ": " or tmp_doc[index - 3:index] == ": [" or tmp_doc[
                                                                                                 index - 3:index] == ": {"):
                    tmp_doc = tmp_doc[:index] + "\\\"" + tmp_doc[index + 1:]
                index -= 1
            content = tmp_doc

    # file = open("subject_info.json", "w", encoding="utf8")
    # file.write(content)
    # file.close()

    # subject_infos = json.loads(content)
    for subject_info in subject_infos:
        try:
            insert_subject(subject_info, cursor)

            characters = subject_info.get("crt") if subject_info.get("crt") is not None else []
            for character_info in characters:
                insert_character(character_info, cursor)

                perform_relation = {
                    "source": int("2" + str(character_info.get("id"))),
                    "target": int("1" + str(subject_info.get("id"))),
                    "name": character_info.get("role_name"),
                    "type": "perform",
                }
                insert_relation(perform_relation, cursor)

                actors = character_info.get("actors") if character_info.get("actors") is not None else []
                for actor_info in actors:
                    insert_actor(actor_info, cursor)

                    actor_relation = {
                        "source": int("3" + str(actor_info.get("id"))),
                        "target": int("2" + str(character_info.get("id"))),
                        "name": "配音",
                        "type": "actor",
                    }
                    insert_relation(actor_relation, cursor)

            staffs = subject_info.get("staff") if subject_info.get("staff") is not None else []
            for staff_info in staffs:
                insert_staff(staff_info, cursor)

                s_job = ""
                for job in staff_info.get("jobs"):
                    s_job += job
                    s_job += ","
                s_job = s_job[:len(s_job) - 1]
                job_relation = {
                    "source": int("4" + str(staff_info.get("id"))),
                    "target": int("1" + str(subject_info.get("id"))),
                    "name": s_job,
                    "type": "job",
                }
                insert_relation(job_relation, cursor)
        except Exception as e:
            print(type(e))
            break
    cursor.close()
    db.commit()
