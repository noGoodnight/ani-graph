import sys
sys.path.append("..")
from json2mysql.mysql_connector import db
cursor = db.cursor()

select_actor_staff_sql = """
select actor.id as a_id, staff.id as s_id
from (
         select id, url
         from entity
         where id like concat('3', '%')
     ) actor,
     (
         select id, url
         from entity
         where id like concat('4', '%')
     ) staff
where actor.id < staff.id
  and actor.url = staff.url;
"""
cursor.execute(select_actor_staff_sql)
actor_staff_list = cursor.fetchall()

update_relation_sql = """update `relation` set `source`=%s where `source`=%s"""
delete_staff_sql = """delete from `entity` where `id`=%s"""

for pair in actor_staff_list:
    cursor.execute(update_relation_sql, (pair[0],pair[1]))
    cursor.execute(delete_staff_sql, pair[1])
    print(pair)
db.commit()
