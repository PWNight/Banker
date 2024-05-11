import pymysql

def conn():
  connection = pymysql.connect(
  host='mysql3.joinserver.xyz',
  port=3306,
  user='u79998_28B2CZ61g1',
  password='J9^E5=d^Xl.dyO@Fy4@LYi1f',
  database= 's79998_foxecosystem',
  cursorclass=pymysql.cursors.DictCursor
)
  return connection

def send(result):
  connection = conn()
  cursor = connection.cursor()
  cursor.execute(result)
  connection.commit() 
  connection.close()
def request_one(result):
  connection = conn()
  cursor = connection.cursor()
  cursor.execute(result)
  result = cursor.fetchone()
  connection.close()
  return result
def request_all(result):
  connection = conn()
  cursor = connection.cursor()
  cursor.execute(result)
  result = cursor.fetchall()
  connection.close()
  return result