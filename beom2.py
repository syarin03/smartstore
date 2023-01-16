import os
import sys
import time
import pymysql
from PyQt5 import uic
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QAbstractItemView, QMessageBox
from matplotlib import font_manager
from datetime import datetime, timedelta

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
    # 초기 화면 설정
        self.Page.setCurrentWidget(self.p_intro)

    # 로그인 / 로그아웃
        self.btn_login.clicked.connect(self.login)
        # self.btn_logout.clicked.connect(self.logout) 로그아웃 아직 없음
        self.btn_join.clicked.connect(self.into_join)
        self.btn_check.clicked.connect(self.idcheck)
        self.btn_newuser.clicked.connect(self.signup)


    def login(self):
        print('로그인 함수')
    def logout(self):
        print('로그아웃 함수')

    def into_join(self):
        print('회원가입 페이지 이동')
        self.Page.setCurrentWidget(self.p_join)

    def idcheck(self):
        id = self.in_id.text() #id에 입력한 아이디 대입
        print(id)
        HOST = '10.10.21.110'
        PORT = 3306
        USER = 'user_t'
        PASSWORD = 'xlavmfhwprxm9'

        con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()  #db연결



        cur.execute(f"select smart.member_table.mb_id \
                       from member_table \
                       where mb_id = '{id}';") #입력한id를 같은게있는지 db에서 검색
        rows = cur.fetchall()


        if id == '':  #id가 공백인지 확인
            QMessageBox.information(self, 'Information Title', '아이디를 입력해주세요')

        elif rows == ():  #id를 db에서 검색한값이 없는지 확인
            QMessageBox.information(self, 'Information Title', '중복되지않습니다 사용해도되요')
            self.id_bool = True
        elif rows[0][0] == id: #id와 디비에서 검색한 값이 맞는지 확인
            QMessageBox.information(self, 'Information Title', '해당아이디는 중복입니다 다시입력')
            self.id_bool = False



    def signup(self):
        
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

                cur.execute(f"insert into smart.member_table (mb_id, mb_pw) \
                                values ('{id}', '{pw}');")  # 입력한id를 같은게있는지 db에서 검색
                rows = cur.fetchall()
                QMessageBox.information(self, 'Information Title', '가입완료')
                con.commit()
            elif self.id_bool == False:
                QMessageBox.information(self, 'Information Title', '아이디 중복 확인을 해주세요')
            elif pw != pw2:
                QMessageBox.information(self, 'Information Title', '비밀번호확인이 맞지않습니다')
        except:
            QMessageBox.information(self, 'Information Title', '뭔가오류')




if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()