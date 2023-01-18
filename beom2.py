import os
import sys
import time
import pymysql
from PyQt5 import uic
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QAbstractItemView, QMessageBox
from matplotlib import font_manager
from datetime import datetime, timedelta
import random
from PyQt5.QtCore import *

# path = os.getcwd()
# font_path = path + "\Pretendard-Light.otf"
# font = font_manager.FontProperties(fname=font_path).get_name()

form_class = uic.loadUiType("mainUI.ui")[0]


# QThread 클래스 선언하기, QThread 클래스를 쓰려면 QtCore 모듈을 import 해야함.

##자동주문 스레드 클래스
class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent



    def run(self):  ##랜덤주문 함수

        self.power = True
        while self.power == True:
            print(self.power)
            self.now = datetime.now()
            self.retrun_hms = self.now.strftime('%H:%M:%S')
            self.retrun_YMD = self.now.strftime('%y/%m/%d')
            print("랜덤주문")

            ran2 = random.randint(1, 3)  # 주문자당 품목갯수 변수

            HOST = '10.10.21.110'
            PORT = 3306
            USER = 'user_t'
            PASSWORD = 'xlavmfhwprxm9'

            con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
            cur = con.cursor()  # db연결

            cur.execute(f"select smart.order.order_num from smart.order order by order_num desc limit 1;")
            max_order_num = cur.fetchall()

            self.order_num = max_order_num[0][0] + 1

            for i in range(0, ran2):
                ran = random.randint(1, 20)  # 품목 랜덤 설정 변수
                ran3 = random.randint(1, 4)  # 주문자의 품목당구매갯수 변수

                HOST = '10.10.21.110'
                PORT = 3306
                USER = 'user_t'
                PASSWORD = 'xlavmfhwprxm9'

                con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
                cur = con.cursor()  # db연결


                cur.execute(f"SELECT * \
                            from smart.product \
                                where prod_num = '{ran}';")  # 제품테이블에서 랜덤으로 품목을 선택하는 쿼리문

                self.retrun_hms = self.now.strftime('%H:%M:%S')
                self.retrun_YMD = self.now.strftime('%Y-%m-%d %H:%M:%S')

                self.order_info = cur.fetchall()

                print(self.order_info[0])
                print(self.order_num)
                print(self.retrun_YMD)
                print(self.order_info[0][0])
                print(ran3)

                cur.execute(f"insert into smart.order (order_num, order_time, prod_num, quantity) \
                                                        values ('{self.order_num}', '{self.retrun_YMD}', '{int(self.order_info[0][0])}', '{int(ran3)}');")

                print(1)
                con.commit()
                con.close()
                self.parent.btn_auto_buy_stop.clicked.connect(self.stop)
            time.sleep(5)



    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self.power = False
        self.quit()


# 메인 윈도우
class WindowClass(QMainWindow, form_class):
    user = None
    today = datetime.now().date().strftime('%Y-%m-%d')





    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.id_bool = False  #ID가 중복인지 확인하는 값
        self.loginbool = False #로그인 유무 확인 값
    # 초기 화면 설정
        self.Page.setCurrentWidget(self.p_intro)
        self.page_login.setCurrentWidget(self.pl_01)
    # 시간


    # 로그인 / 로그아웃
        self.btn_login.clicked.connect(self.login)
        # self.btn_logout.clicked.connect(self.logout) 로그아웃 아직 없음
        self.btn_join.clicked.connect(self.into_join)
        self.btn_check.clicked.connect(self.idcheck)
        self.btn_newuser.clicked.connect(self.signup)
        self.btn_gomain.clicked.connect(self.gohome)
        self.btn_logout.clicked.connect(self.logout)
        self.btn_buy_random.clicked.connect(self.buy_random)
        self.btn_order_management.clicked.connect(self.go_order_management)
        self.btn_go_loginmain.clicked.connect(self.gohome)
        self.table_order_management.cellClicked.connect(self.current_table_row_column)  ##주문관리 테이블위젯의 행,열을 받는 함수

        self.btn_order_receipt.clicked.connect(self.order_receipt)
        self.btn_auto_buy_start.clicked.connect(self.actionFunction1)  #자동주문 스레드 시작
        # self.btn_auto_buy_stop.clicked.connect(self.actionFunction2)

    def actionFunction1(self):
        h1 = Thread1(self)
        h1.start()

    def actionFunction2(self):
        h1 = Thread1(self)
        h1.stop()


    def login(self):
        print('로그인 함수')
        id = self.in_id_login.text()  # id에 입력한 아이디 대입
        pw = self.in_pw_login.text()

        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  # db연결

        cur.execute(f"select smart.member.num \
                               from smart.member \
                               where uid = '{id}' and upw = '{pw}';")  # 입력한id와 pw가 같은게있는지 db에서 검색

        rows = cur.fetchall()

        if id =='' or pw=='':
            QMessageBox.information(self, 'Information Title', '빈칸을 채워주세요')
        elif rows == ():
            QMessageBox.information(self, 'Information Title', '아이디 또는 비밀번호를 확인해주세요')
        else:
            self.key = rows[0][0]  #db검색에 쓸 num값 self.key에 대입
            cur.execute(f"select * from smart.member where smart.member.num = '{self.key}' ")
            self.member_info = cur.fetchall()  #num값으로 검색한 모든 칼럼갑을 self.member_info에 대입
            con.close()

            QMessageBox.information(self, 'Information Title', '로그인완료')
            self.loginbool = True
            self.page_login.setCurrentWidget(self.pl_02)  ##로그인후 화면으로 전환
            self.label_loginid.setText(self.member_info[0][3])

    def logout(self):
        print('로그아웃 함수')
        self.loginbool = False
        self.page_login.setCurrentWidget(self.pl_01)
    def gohome(self):
        self.Page.setCurrentWidget(self.p_intro)
    def into_join(self):
        print('회원가입 페이지 이동')
        self.Page.setCurrentWidget(self.p_join)

    def idcheck(self):   #id 중복체크 함수
        id = self.in_id.text() #id에 입력한 아이디 대입
        print(id)
        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  #db연결



        cur.execute(f"select smart.member.uid    \
                       from smart.member \
                       where uid = '{id}';") #입력한id를 같은게있는지 db에서 검색
        rows = cur.fetchall()
        con.close()

        if id == '':  #id가 공백인지 확인
            QMessageBox.information(self, 'Information Title', '아이디를 입력해주세요')

        elif rows == ():  #id를 db에서 검색한값이 없는지 확인
            QMessageBox.information(self, 'Information Title', '중복되지않습니다 사용해도되요')
            self.id_bool = True  #중복검사확인시 id.bool을 true로
        elif rows[0][0] == id: #id와 디비에서 검색한 값이 맞는지 확인
            QMessageBox.information(self, 'Information Title', '해당아이디는 중복입니다 다시입력')
            self.id_bool = False #중복일시 id.bool을 False(초기값도 False임)



    def signup(self):   #회원가입함수
        
        name = self.in_name.text()
        id = self.in_id.text()
        pw = self.in_pass.text()
        pw2 = self. in_pass_.text()  #이름,아이디,비번,비번확인 을 변수에 대입

        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  # db연결

        try:
            if pw == pw2 and self.id_bool == True:

                cur.execute(f"insert into smart.member (uid, upw, name) \
                                values ('{id}', '{pw}', '{name}');")  # 입력한id를 같은게있는지 db에서 검색
                rows = cur.fetchall()
                QMessageBox.information(self, 'Information Title', '가입완료')
                con.commit()
                con.close()
                self.Page.setCurrentWidget(self.p_intro)  #회원가입 완료후 메인화면으로
            elif self.id_bool == False:  #
                QMessageBox.information(self, 'Information Title', '아이디 중복 확인을 해주세요')
            elif pw != pw2:
                QMessageBox.information(self, 'Information Title', '비밀번호확인이 맞지않습니다')
        except:
            QMessageBox.information(self, 'Information Title', '뭔가오류')

    def buy_random(self):    ##랜덤주문 함수
        print(1)
        self.now = datetime.now()
        self.retrun_hms = self.now.strftime('%H:%M:%S')
        self.retrun_YMD = self.now.strftime('%y/%m/%d')
        print("랜덤주문")

        ran2 = random.randint(1,3)  #주문자당 품목갯수 변수


        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  # db연결
        cur.execute(f"select smart.order.order_num from smart.order order by order_num desc limit 1;")
        max_order_num = cur.fetchall()
        self.order_num = max_order_num[0][0] + 1



        for i in range (0, ran2):

            ran = random.randint(1, 20)  # 품목 랜덤 설정 변수
            ran3 = random.randint(1, 4)  # 주문자의 품목당구매갯수 변수

            HOST = '10.10.21.110'
            PORT = 3306
            USER = 'user_t'
            PASSWORD = 'xlavmfhwprxm9'

            con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
            cur = con.cursor()  # db연결


            cur.execute(f"SELECT * \
                        from smart.product \
                            where prod_num = '{ran}';")  # 제품테이블에서 랜덤으로 품목을 선택하는 쿼리문

            self.retrun_hms = self.now.strftime('%H:%M:%S')
            self.retrun_YMD = self.now.strftime('%Y-%m-%d %H:%M:%S')


            self.order_info = cur.fetchall()

            print(self.order_info[0])
            print(self.order_num)
            print(self.retrun_YMD)
            print(self.order_info[0][0])
            print(ran3)
            print(ran2)

            cur.execute(f"insert into smart.order (order_num, order_time, prod_num, quantity) \
                                                    values ('{self.order_num}', '{self.retrun_YMD}', '{int(self.order_info[0][0])}', '{int(ran3)}');")

            print("병신")
            con.commit()
            con.close()








    
    def go_order_management(self):  ##주문관리 함수
        print("주문관리")

        self.Page.setCurrentWidget(self.p_order_management)



        ## 주문목록 테이블위젯

        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  # db연결
        cur.execute(f"SELECT * from smart.order \
                        left join smart.product \
                        ON smart.order.prod_num = smart.product.prod_num;")  #오더테이블 과 프로덕트테이블 조인하여 조회
        rows = cur.fetchall()

        cur.execute(f"SELECT count(num) from smart.order;") #주문 횟수가 얼마나 되는지 조회하는 쿼리문
        len = cur.fetchall()


        self.table_order_management.setRowCount(len[0][0])
        self.table_order_management.setColumnCount(6)

        print(rows[0][2])
        print(type(rows[0][2]))
        con.close()
        col=0
        for row in rows:


            self.table_order_management.setItem(col, 0, QTableWidgetItem(str(row[1])))
            self.table_order_management.setItem(col, 1, QTableWidgetItem(str(row[2])))
            self.table_order_management.setItem(col, 2, QTableWidgetItem(str(row[7])))
            self.table_order_management.setItem(col, 3, QTableWidgetItem(str(row[4])))
            self.table_order_management.setItem(col, 4, QTableWidgetItem(str((row[8]*row[4]))))  ## 총금액
            self.table_order_management.setItem(col, 5, QTableWidgetItem(str(row[5])))

            col += 1



    def current_table_row_column(self):  #주문관리 테이블위젯의 행,열을 받고 자재관리 테이블위젯을 만들어주는 함수



        self.a = self.table_order_management.currentRow()
        self.b = self.table_order_management.currentColumn()
        self.order_prod_name = self.table_order_management.item(self.a,2)  #클릭한 행의 제품이름
        self.order_prod_quantity = self.table_order_management.item(self.a,3)   #클릭한 주문의 제품구매수량
        self.order_status = self.table_order_management.item(self.a,5)



        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  # db연결

        cur.execute(f"SELECT smart.product.prod_num \
                        from smart.product \
                        where prod_name = '{self.order_prod_name.text()}';") #테이블위젯에서 상품명을 받아와서 상품번호 조회
        prod_num = cur.fetchall()  #상품번호


        cur.execute(f"SELECT * \
                        from smart.recipe left join smart.ingredients \
                            ON smart.recipe.ingre_num = smart.ingredients.ingre_num \
                            where smart.recipe.prod_num = '{prod_num[0][0]}';")  # 상품번호로 레시피와 재료테이블을 조인하여 조회
        self.rows2 = cur.fetchall() #num
        self.possible_make =[]
        # print(self.possible_make[0])




        cur.execute(f"SELECT count(smart.recipe.prod_num) \
                    from smart.recipe \
                    left join smart.product \
                    on smart.recipe.prod_num = smart.product.prod_num \
                    where smart.recipe.prod_num = '{prod_num[0][0]}';")  #제품의 제조에 필요한 재료가 몇개인지 조회하는 쿼리문

        self.len = cur.fetchall()



        con.close()


        self.table_order_management2.setRowCount(self.len[0][0])
        self.table_order_management2.setColumnCount(4)


        col = 0

        for row in self.rows2:
            self.table_order_management2.setItem(col, 0, QTableWidgetItem(str(row[6])))
            self.table_order_management2.setItem(col, 1, QTableWidgetItem(str(int(row[3]))))
            self.table_order_management2.setItem(col, 2, QTableWidgetItem(str(int(row[7]))))
            self.table_order_management2.setItem(col, 3, QTableWidgetItem(str(int((row[7]/row[3])))))  ## 제조가능수량
            self.possible_make.append(int(row[7]/row[3]))

            col += 1
        print(min(self.possible_make))
    def order_receipt(self):

        if self.order_status.text() == '접수대기' and  min(self.possible_make) >= 1:
            if min(self.possible_make)<100:
                QMessageBox.information(self, 'Information Title', '해당주문 제품의 제작 가능 수량이 100개 미만입니다')

            HOST = '10.10.21.110'
            PORT = 3306
            USER = 'user_t'
            PASSWORD = 'xlavmfhwprxm9'

            con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
            cur = con.cursor()  # db연결
            print(self.rows2[0])
            for row in self.rows2:
                consum = row[3]* int(self.order_prod_quantity.text())
                cur.execute(f"UPDATE smart.ingredients \
                            SET stock = stock -  '{consum}' \
                            WHERE smart.ingredients.ingre_num = '{row[2]}';") ##주문접수 버튼을누르면 재료테이블의 스톡을 해당 주문의 구매수량 X 소모량 만큼 빼주는 쿼리문





            cur.execute(f"SELECT * from smart.order \
                                    left join smart.product \
                                    ON smart.order.prod_num = smart.product.prod_num;")  # 오더테이블 과 프로덕트테이블 조인하여 조회
            rows1 = cur.fetchall()

            cur.execute(f"UPDATE smart.order \
                                           SET order_status = '{'접수,제작 완료'}' \
                                           WHERE smart.order.num = '{rows1[self.a][0]}';")  ##오더테이블의 num으로 조회하여 접수대기중을 접수,제작완료로 업데이트 해주는 쿼리문

            con.commit()

            print(2222)
            cur.execute(f"SELECT * from smart.order \
                                           left join smart.product \
                                           ON smart.order.prod_num = smart.product.prod_num;")  # 오더테이블 과 프로덕트테이블 조인하여 조회
            rows = cur.fetchall()

            cur.execute(f"SELECT count(num) from smart.order;")  # 주문 횟수가 얼마나 되는지 조회하는 쿼리문
            len = cur.fetchall()

            self.table_order_management.setRowCount(len[0][0])
            self.table_order_management.setColumnCount(6)

            print(rows[0][5])

            con.close()
            col = 0
            for row in rows:
                self.table_order_management.setItem(col, 0, QTableWidgetItem(str(row[1])))
                self.table_order_management.setItem(col, 1, QTableWidgetItem(str(row[2])))
                self.table_order_management.setItem(col, 2, QTableWidgetItem(str(row[7])))
                self.table_order_management.setItem(col, 3, QTableWidgetItem(str(row[4])))
                self.table_order_management.setItem(col, 4, QTableWidgetItem(str((row[8] * row[4]))))  ## 총금액
                self.table_order_management.setItem(col, 5, QTableWidgetItem(str(row[5])))

                col += 1
        elif min(self.possible_make)<1:
            QMessageBox.information(self, 'Information Title', '자재가 부족합니다')
        else:
            QMessageBox.information(self, 'Information Title', '이미 완료된 주문입니다')


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()