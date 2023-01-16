import pymysql

HOST = '10.10.21.110'
PORT = 3306
USER = 'user_t'
PASSWORD = 'xlavmfhwprxm9'

conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')

## 연결 테스트문
if conn.open:
    with conn.cursor() as curs:
        print('connected')