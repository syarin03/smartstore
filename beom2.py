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

# path = os.getcwd()
# font_path = path + "\Pretendard-Light.otf"
# font = font_manager.FontProperties(fname=font_path).get_name()

form_class = uic.loadUiType("mainUI.ui")[0]

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

        self.order_num = 1111 # 시작 주문번호



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
        con.close()
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
        self.now = datetime.now()
        self.retrun_hms = self.now.strftime('%H:%M:%S')
        self.retrun_YMD = self.now.strftime('%y/%m/%d')
        print("랜덤주문")

        ran2 = random.randint(1,3)  #주문자당 품목갯수 변수


        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        self.order_num += 1
        for i in range (0, ran2):
            ran = random.randint(1, 20)  # 품목 랜덤 설정 변수
            ran3 = random.randint(1, 4)  # 주문자의 품목당구매갯수 변수
            con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
            cur = con.cursor()  # db연결

            cur.execute(f"SELECT * \
                        from smart.product \
                            where prod_num = '{ran}';")  # 입력한id를 같은게있는지 db에서 검색

            self.retrun_hms = self.now.strftime('%H:%M:%S')
            self.retrun_YMD = self.now.strftime('%Y-%m-%d %H:%M:%S')


            self.order_info = cur.fetchall()
            print(type(self.order_num))
            print(type(self.retrun_YMD))
            print(type(self.order_info[0][0]))

            cur.execute(f"insert into smart.order (order_num, order_time, prod_num, quantity) \
                                                    values ('{self.order_num}', '{self.retrun_YMD}', '{int(self.order_info[0][0])}', '{int(ran3)}');")
            print(1)
            con.commit()
            con.close()








    
    def go_order_management(self):  ##주문관리 함수
        print("주문관리")
        self.Page.setCurrentWidget(self.p_order_management)
        self.table_order_management.setColumnCount(6)
        self.table_order_management2.setColumnCount(5)
        self.table_order_management.setHorizontalHeaderLabels(["연번","주문번호","주문시간","제품명","수량","금액"])
        self.table_order_management2.setHorizontalHeaderLabels(["제품명", "재료", "주문시간", "제품명", "수량"])



if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()