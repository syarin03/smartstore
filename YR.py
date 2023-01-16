import pymysql

HOST = '10.10.21.110'
PORT = 3306
USER = 'user_t'
PASSWORD = 'xlavmfhwprxm9'

conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
## 연결 테스트문
# if conn.open:
#     with conn.cursor() as curs:
#         print('connected')

def product():
    with conn.cursor() as cur:
        sql = f"SELECT * FROM smart.product"
        cur.execute(sql)
        products = cur.fetchall()

    for item in products:
        print(f'{item[0]}  - {item[1]} : {item[2]}원')

    return products
