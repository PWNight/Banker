import pymysql
connection = pymysql.connect(
  host='mysql3.joinserver.xyz',
  port=3306,
  user='u79998_28B2CZ61g1',
  password='J9^E5=d^Xl.dyO@Fy4@LYi1f',
  database='s79998_foxecosystem',
  cursorclass=pymysql.cursors.DictCursor
)    
def get_info_by_id(id):
    global connection
    with connection.cursor() as cursor:
      cursor.execute(f"SELECT * FROM `bank_cards` WHERE id = {id}")
      result = cursor.fetchall()
      return result
def get_info_by_ownerid(id):
    global connection
    with connection.cursor() as cursor:
      cursor.execute(f"SELECT * FROM `bank_cards` WHERE owner_id = {id}")
      result = cursor.fetchall()
      return result
def send(result):
    global connection
    cursor = connection.cursor()
    cursor.execute(result)
    connection.commit()
    return result