import os
import re
import sys
import time
import pymysql
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QFontDatabase, QFont, QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox, QHeaderView, \
    QPushButton
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

                self.parent.btn_auto_buy_stop.clicked.connect(self.stop)
                time.sleep(5)

    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self.power = False
        self.quit()


class Thread2(QThread):
    # 초기화 메서드 구현
    def __init__(self, parent):  # parent는 WndowClass에서 전달하는 self이다.(WidnowClass의 인스턴스)
        super().__init__(parent)
        self.parent = parent  # self.parent를 사용하여 WindowClass 위젯을 제어할 수 있다.

    def run(self):  ##자동주문접수 함수
        self.power = True
        j=0
        while self.power == True:
            self.parent.btn_auto_order_receipt_stop.clicked.connect(self.stop)

            print("시작해보자")
            print(j)
            HOST = '10.10.21.110'
            PORT = 3306
            USER = 'user_t'
            PASSWORD = 'xlavmfhwprxm9'

            con = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db='smart', charset='utf8')
            cur = con.cursor()  # db연결

            cur.execute(f"SELECT * from smart.order \
                                    left join smart.product \
                                    ON smart.order.prod_num = smart.product.prod_num \
                                        where order_status = '{'접수대기'}';" )  # 오더테이블 과 프로덕트테이블 조인하여 주문상태가 접수대기중인것만 조회
            rows = cur.fetchall()

            ## rows[0][3] = 제붐번호 rows[0][4] = 수량
            ## rows2[0][3] ==소모량 rows2[0][7]= 전체잔량

            cur.execute(f"SELECT * \
                                    from smart.recipe left join smart.ingredients \
                                        ON smart.recipe.ingre_num = smart.ingredients.ingre_num \
                                        where smart.recipe.prod_num = '{rows[j][3]}';")  # 상품번호로 레시피와 재료테이블을 조인하여 조회
            rows2 = cur.fetchall()  # num





            cur.execute(f"SELECT count(smart.recipe.prod_num) \
                                from smart.recipe \
                                left join smart.product \
                                on smart.recipe.prod_num = smart.product.prod_num \
                                where smart.recipe.prod_num = '{rows[j][3]}';")  # 제품의 제조에 필요한 재료가 몇개인지 조회하는 쿼리문
            len = cur.fetchall()
            # rows3 = cur.fetchall()
            # print(rows[0])
            for i in range (0,len[0][0]):
                if int(rows2[i][7]) < int(rows2[i][3]*rows[i][4]):
                    print("부족해")
                    breakgab = False
                    break
                else:
                    breakgab = True
                    cur.execute(f"UPDATE smart.ingredients \
                                                SET stock = stock -  '{int(rows2[i][3]*rows[i][4])}' \
                                                WHERE smart.ingredients.ingre_num = '{rows2[i][2]}';")  ##재료테이블의 스톡을 해당 주문의 구매수량 X 소모량 만큼 빼주는 쿼리문
                #포문끝
            if breakgab == False:
                print("다시시작")
                j+=1
                continue

            cur.execute(f"UPDATE smart.order \
                        SET order_status = '{'접수,제작 완료'}' \
                        WHERE smart.order.num = '{rows[j][0]}';")  ##오더테이블의 num으로 조회하여 접수대기중을 접수,제작완료로 업데이트 해주는 쿼리문
            con.commit()


            self.parent.btn_auto_order_receipt_stop.clicked.connect(self.stop)
            # self.parent.go_order_management()

            cur.execute(f"SELECT * from smart.order \
                                                left join smart.product \
                                                ON smart.order.prod_num = smart.product.prod_num;")  # 오더테이블 과 프로덕트테이블 조인하여 조회
            newrows = cur.fetchall()

            cur.execute(f"SELECT count(num) from smart.order;")  # 주문 횟수가 얼마나 되는지 조회하는 쿼리문
            len2 = cur.fetchall()
            con.close()

            self.parent.table_order_management.setRowCount(len2[0][0])
            self.parent.table_order_management.setColumnCount(6)

            print(newrows[0][2])
            print(type(newrows[0][2]))

            col = 0
            for row in newrows:

                self.parent.table_order_management.setItem(col, 0, QTableWidgetItem(str(row[1])))
                self.parent.table_order_management.setItem(col, 1, QTableWidgetItem(str(row[2])))
                self.parent.table_order_management.setItem(col, 2, QTableWidgetItem(str(row[7])))
                self.parent.table_order_management.setItem(col, 3, QTableWidgetItem(str(row[4])))
                self.parent.table_order_management.setItem(col, 4, QTableWidgetItem(str((row[8] * row[4]))))  ## 총금액
                self.parent.table_order_management.setItem(col, 5, QTableWidgetItem(str(row[5])))

                col += 1
            j+=1
            time.sleep(5)
            # print(12121212)
            # print(rows2[0])
            # print(rows2[1])
            # print(len[0][0])


    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self.power = False
        self.quit()


# 메인 윈도우
class WindowClass(QMainWindow, form_class):
    user = None
    today = datetime.now().date().strftime('%Y-%m-%d')
    prod_dic = dict()

    HOST = '10.10.21.110'
    PORT = 3306
    USER = 'user_t'
    PASSWORD = 'xlavmfhwprxm9'

    product = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.label_qna_num.setVisible(False)
        self.id_bool = False  # ID가 중복인지 확인하는 값
        self.loginbool = False  # 로그인 유무 확인 값

        # 초기 화면 설정
        self.main_menu.hide() # 메인 메뉴 숨김
        self.Page.setCurrentWidget(self.p_intro)
        self.page_login.setCurrentWidget(self.pl_01)
        self.main_menu.setCurrentIndex(0)
        self.product_listup()

        # 가미버튼
        self.main_menu.currentChanged.connect(self.page_changed)
        self.page_qna.currentChanged.connect(self.page_changed)  # 문제의 그 구간
        self.table_qna.itemDoubleClicked.connect(self.view_question)
        # self.btn_go_qna_manage.clicked.connect(self.go_qna)
        # self.btn_answer_to_qna.clicked.connect(self.go_qna)
        self.btn_go_qna_add.clicked.connect(self.go_question)
        # self.btn_qna_to_main.clicked.connect(self.go_main)
        # self.btn_question_to_main.clicked.connect(self.go_main)
        self.btn_question.clicked.connect(self.question)
        self.btn_answer.clicked.connect(self.answer)


        # 로그인 / 로그아웃
        self.btn_login.clicked.connect(self.login)
        self.btn_logout.clicked.connect(self.logout)

        self.btn_join.clicked.connect(self.into_join)
        self.btn_check.clicked.connect(self.idcheck)
        self.btn_newuser.clicked.connect(self.signup)
        self.btn_gomain.clicked.connect(self.gohome)

        #
        self.btn_buy_random.clicked.connect(self.buy_random)
        self.btn_order_management.clicked.connect(self.go_order_management)

        # 주문 관리 테이블위젯의 행,열을 받는 함수
        self.table_order_management.cellClicked.connect(self.current_table_row_column)
        # 테이블 헤더 폭 조정 :
        self.table_order_management.setColumnWidth(0, 60)
        self.table_order_management.setColumnWidth(1, 130)
        self.table_order_management.setColumnWidth(2, 135)
        self.table_order_management.setColumnWidth(3, 10)
        self.table_order_management.setColumnWidth(4, 70)

        self.btn_order_receipt.clicked.connect(self.order_receipt)
        self.btn_auto_buy_start.clicked.connect(self.actionFunction1)  # 자동주문 스레드 시작
        self.btn_auto_order_receip_start.clicked.connect(self.actionFunction3)  # 자동주문 스레드 시작

        # 상품추가
        self.btn_add.clicked.connect(self.new_recipe_plus)
        self.btn_del.clicked.connect(self.new_recipe_minus)
        input_rule = QRegExp("[0-9]{0,6}")  # 0부터 9까지의 숫자 길이 제한 없음
        self.in_cost.setValidator(QRegExpValidator(input_rule, self))


    def go_qna(self):
        sql = "SELECT a.num, b.prod_name, c.order_num, a.title, a.content, a.answer " \
              "FROM question a " \
              "LEFT JOIN product b ON a.prod_num = b.prod_num " \
              "LEFT JOIN `order` c ON a.order_num = c.order_num AND a.prod_num = c.prod_num"
        print(sql)
        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            print(result)
            self.table_qna.setRowCount(len(result))
            self.table_qna.setColumnWidth(0, 30)
            self.table_qna.setColumnWidth(1, 80)
            self.table_qna.setColumnWidth(2, 190)
            self.table_qna.setColumnWidth(3, 400)
            self.table_qna.setColumnWidth(4, 70)
            col = 0
            for i in result:
                self.table_qna.setItem(col, 0, QTableWidgetItem(str(i[0])))
                if i[2] is None:
                    self.table_qna.setItem(col, 1, QTableWidgetItem(''))
                else:
                    self.table_qna.setItem(col, 1, QTableWidgetItem(str(i[2])))
                if i[1] is None:
                    self.table_qna.setItem(col, 2, QTableWidgetItem(''))
                else:
                    self.table_qna.setItem(col, 2, QTableWidgetItem(str(i[1])))
                self.table_qna.setItem(col, 3, QTableWidgetItem(str(i[3])))
                if i[5] is None:
                    self.table_qna.setItem(col, 4, QTableWidgetItem('대기'))
                else:
                    self.table_qna.setItem(col, 4, QTableWidgetItem('완료'))
                col += 1

    def go_question(self):
        self.page_qna.setCurrentWidget(self.stack_add_question)
        sql = "SELECT prod_num, prod_name FROM product"
        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            for i in result:
                self.prod_dic[i[1]] = i[0]

        self.combo_question_prod.addItem('선택 안 함')
        self.combo_question_prod.addItems(self.prod_dic.keys())
        print(self.prod_dic.keys())

    def answer(self):
        answer_str = self.edit_answer.toPlainText()
        sql = f"UPDATE question SET answer = '{answer_str}' WHERE num = {self.label_qna_num.text()}"
        print(sql)
        with self.conn_commit() as con:
            with con.cursor() as cur:
                cur.execute(sql)
                con.commit()
                QMessageBox.information(self, '알림', '답변이 저장되었습니다')
                self.page_qna.setCurrentWidget(self.stack_qna)
                self.go_qna()

    def question(self):
        q_title = self.edit_question_title.text()
        q_prod = self.combo_question_prod.currentText()
        q_order = self.edit_question_order.text()
        q_content = self.edit_question_content.toPlainText()

        if q_title == '' or q_content == '':
            QMessageBox.warning(self, '경고', '제목과 내용 입력란을 확인해주세요')
            return

        if q_prod in self.prod_dic.keys():
            q_prod_num = self.prod_dic[q_prod]
            if q_order == '':
                sql = f"INSERT INTO question (prod_num, title, content) VALUES " \
                      f"({q_prod_num}, '{q_title}', '{q_content}')"
            else:
                sql = f"INSERT INTO question (prod_num, order_num, title, content) VALUES " \
                      f"({q_prod_num}, {q_order}, '{q_title}', '{q_content}')"
        else:
            if q_order == '':
                sql = f"INSERT INTO question (title, content) VALUES " \
                      f"('{q_title}', '{q_content}')"
            else:
                sql = f"INSERT INTO question (order_num, title, content) VALUES " \
                      f"({q_order}, '{q_title}', '{q_content}')"
        print(sql)

        with self.conn_commit() as con:
            with con.cursor() as cur:
                cur.execute(sql)
                con.commit()
                QMessageBox.information(self, '알림', '문의가 등록되었습니다')
                self.page_qna.setCurrentWidget(self.stack_main)

    def page_changed(self):
        send = self.sender()
        if send == self.main_menu:
            self.page_qna.setCurrentWidget(self.stack_qna)
        self.table_qna.setRowCount(0)
        self.edit_question_content.clear()
        self.edit_question_order.clear()
        self.edit_question_title.clear()
        # self.page_qna.setCurrentWidget(self.stack_qna)
        self.go_qna()

    def view_question(self):
        row = self.table_qna.currentIndex().row()
        col = self.table_qna.currentIndex().column()
        print(row, col)
        data = self.table_qna.item(row, 3)
        print(row, col, data.text())
        sql = f"SELECT * FROM question WHERE title = '{data.text()}'"
        print(sql)
        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            print(result)
            self.label_question_title.setText(str(result[0][3]))
            self.browser_question_content.setPlainText(str(result[0][4]))
            if result[0][5] is None:
                self.label_answer_status.setText('대기')
                self.edit_answer.setPlainText('')
            else:
                self.label_answer_status.setText('완료')
                self.edit_answer.setPlainText(str(result[0][5]))
            self.label_qna_num.setText(str(result[0][0]))
        self.page_qna.setCurrentWidget(self.stack_qna_detail)


    def conn_fetch(self):
        con = pymysql.connect(host=self.HOST, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()
        return cur

    def conn_commit(self):
        con = pymysql.connect(host=self.HOST, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        return con


    def actionFunction1(self):  ##자동주문 쓰레드 시작
        h1 = Thread1(self)
        h1.start()

    def actionFunction3(self):
        h1 = Thread2(self)
        h1.start()

    def login(self):
        print('로그인 함수')
        id = self.in_id_login.text()  # id에 입력한 아이디 대입
        pw = self.in_pw_login.text()
        con = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                              charset='utf8')
        cur = con.cursor()  # db연결

        cur.execute(f"select smart.member.num \
                               from smart.member \
                               where uid = '{id}' and upw = '{pw}';")  # 입력한 id와 pw가 같은게있는지 db에서 검색
        rows = cur.fetchall()

        if id == '' or pw == '':
            QMessageBox.information(self, '로그인', '아이디와 비밀번호를 입력해주세요')
        elif rows == ():
            QMessageBox.information(self, '로그인', '아이디 또는 비밀번호를 확인해주세요')
        else:
            self.key = rows[0][0]  # db검색에 쓸 num값 self.key에 대입
            cur.execute(f"select * from smart.member where smart.member.num = '{self.key}' ")
            self.member_info = cur.fetchall()  # num값으로 검색한 모든 칼럼갑을 self.member_info에 대입
            con.close()

            QMessageBox.information(self, '로그인', '로그인되었습니다')
            self.loginbool = True
            self.page_login.setCurrentWidget(self.pl_02)
            self.label_welcome.setText(f'{self.member_info[0][3]}님 환영합니다.')
            self.main_menu.show()

    def logout(self):
        print('로그아웃 함수')
        self.loginbool = False
        self.page_login.setCurrentWidget(self.pl_01)
        self.main_menu.hide()
        self.in_pw_login.setText('')

    def gohome(self):
        self.Page.setCurrentWidget(self.p_intro)

    def into_join(self):
        print('회원가입 페이지 이동')
        self.Page.setCurrentWidget(self.p_join)

    def idcheck(self):  # id 중복체크 함수
        id = self.in_id.text()  # id에 입력한 아이디 대입
        print(id)

        con = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                              charset='utf8')
        cur = con.cursor()  # db연결

        cur.execute(f"select smart.member.uid    \
                       from smart.member \
                       where uid = '{id}';")  # 입력한id를 같은게있는지 db에서 검색
        rows = cur.fetchall()

        if id == '':  # id가 공백인지 확인
            QMessageBox.information(self, '회원가입', '아이디를 입력해주세요')

        elif rows == ():  # id를 db에서 검색한값이 없는지 확인
            QMessageBox.information(self, '회원가입', '사용 가능한 아이디입니다')
            self.id_bool = True  # 중복검사확인시 id.bool을 true로
        elif rows[0][0] == id:  # id와 디비에서 검색한 값이 맞는지 확인
            QMessageBox.information(self, '회원가입', '이미 사용중인 아이디입니다')
            self.id_bool = False  # 중복일시 id.bool을 False(초기값도 False임)

    def signup(self):  # 회원가입함수

        name = self.in_name.text()
        id = self.in_id.text()
        pw = self.in_pass.text()
        pw2 = self.in_pass_.text()  # 이름,아이디,비번,비번확인 을 변수에 대입

        con = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                              charset='utf8')
        cur = con.cursor()  # db연결

        try:
            if pw == pw2 and self.id_bool == True:

                cur.execute(f"insert into smart.member (uid, upw, name) \
                                values ('{id}', '{pw}', '{name}');")
                QMessageBox.information(self, '회원가입', '가입 완료되었습니다')
                con.commit()
                self.Page.setCurrentWidget(self.p_intro)  # 회원 가입 완료 후 메인화면으로
            elif self.id_bool == False:  #
                QMessageBox.information(self, '회원가입', '아이디 중복 확인을 해주세요')
            elif pw != pw2:
                QMessageBox.information(self, '회원가입', '비밀번호가 일치하지 않습니다')
        except:
            QMessageBox.information(self, '회원가입', '오류')

    def buy_random(self):  ##랜덤주문 함수
        self.now = datetime.now()
        self.retrun_hms = self.now.strftime('%H:%M:%S')
        self.retrun_YMD = self.now.strftime('%y/%m/%d')
        print("랜덤주문")

        ran2 = random.randint(1, 3)  # 주문자당 품목갯수 변수

        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        cur = conn.cursor()  # db연결
        cur.execute(f"select smart.order.order_num from smart.order order by order_num desc limit 1;")
        max_order_num = cur.fetchall()
        self.order_num = max_order_num[0][0] + 1

        for i in range(0, ran2):
            ran = random.randint(1, 20)  # 품목 랜덤 설정 변수
            ran3 = random.randint(1, 4)  # 주문자의 품목당 구매갯수 변수

            conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                                   charset='utf8')
            cur = conn.cursor()  # db연결

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

            conn.commit()
            conn.close()

    def go_order_management(self):  ##주문관리 함수
        print("주문관리")

        ## 주문목록 테이블위젯
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        cur = conn.cursor()  # db연결
        cur.execute(f"SELECT * from smart.order \
                        left join smart.product \
                        ON smart.order.prod_num = smart.product.prod_num;")  # 오더테이블 과 프로덕트테이블 조인하여 조회
        self.rows = cur.fetchall()

        cur.execute(f"SELECT count(num) from smart.order;")  # 주문 횟수가 얼마나 되는지 조회하는 쿼리문
        len = cur.fetchall()

        self.table_order_management.setRowCount(len[0][0])
        self.table_order_management.setColumnCount(6)

        print(self.rows[0][2])
        print(type(self.rows[0][2]))
        conn.close()
        col = 0
        for row in self.rows:
            self.table_order_management.setItem(col, 0, QTableWidgetItem(str(row[1])))
            self.table_order_management.setItem(col, 1, QTableWidgetItem(str(row[2])))
            self.table_order_management.setItem(col, 2, QTableWidgetItem(str(row[7])))
            self.table_order_management.setItem(col, 3, QTableWidgetItem(str(row[4])))
            self.table_order_management.setItem(col, 4, QTableWidgetItem(str((row[8] * row[4]))))  ## 총금액
            self.table_order_management.setItem(col, 5, QTableWidgetItem(str(row[5])))

            # 테이블 데이터 정렬 -- 오류
            # self.table_order_management(col, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            # self.table_order_management(col, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # self.table_order_management(col, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col += 1

    def current_table_row_column(self):  # 주문관리 테이블위젯의 행,열을 받고 자재관리 테이블위젯을 만들어주는 함수

        self.a = self.table_order_management.currentRow()
        self.b = self.table_order_management.currentColumn()
        self.order_prod_name = self.table_order_management.item(self.a, 2)  # 클릭한 행의 제품이름
        self.order_prod_quantity = self.table_order_management.item(self.a, 3)  # 클릭한 주문의 제품구매수량
        self.order_status = self.table_order_management.item(self.a, 5)

        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        cur = conn.cursor()  # db연결
        cur.execute(f"SELECT smart.product.prod_num \
                        from smart.product \
                        where prod_name = '{self.order_prod_name.text()}';")  # 테이블위젯에서 상품명을 받아와서 상품번호 조회
        prod_num = cur.fetchall()  # 상품번호

        cur.execute(f"SELECT * \
                        from smart.recipe left join smart.ingredients \
                            ON smart.recipe.ingre_num = smart.ingredients.ingre_num \
                            where smart.recipe.prod_num = '{prod_num[0][0]}';")  # 상품번호로 레시피와 재료테이블을 조인하여 조회
        self.rows2 = cur.fetchall()  # num
        self.possible_make = []
        # print(self.possible_make[0])

        cur.execute(f"SELECT count(smart.recipe.prod_num) \
                    from smart.recipe \
                    left join smart.product \
                    on smart.recipe.prod_num = smart.product.prod_num \
                    where smart.recipe.prod_num = '{prod_num[0][0]}';")  # 제품의 제조에 필요한 재료가 몇개인지 조회하는 쿼리문

        self.len = cur.fetchall()
        conn.close()

        self.table_order_management2.setRowCount(self.len[0][0])
        self.table_order_management2.setColumnCount(4)

        col = 0

        for row in self.rows2:
            self.table_order_management2.setItem(col, 0, QTableWidgetItem(str(row[6])))
            self.table_order_management2.setItem(col, 1, QTableWidgetItem(str(int(row[3]))))
            self.table_order_management2.setItem(col, 2, QTableWidgetItem(str(int(row[7]))))
            self.table_order_management2.setItem(col, 3, QTableWidgetItem(str(int((row[7] / row[3])))))  ## 제조가능수량
            self.possible_make.append(int(row[7] / row[3]))

            col += 1
        print(min(self.possible_make))

    def order_receipt(self):

        if self.order_status.text() == '접수대기' and min(self.possible_make) >= 1:
            if min(self.possible_make) < 100:
                QMessageBox.information(self, 'Information Title', '해당주문 제품의 제작 가능 수량이 100개 미만입니다')

            conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                                   charset='utf8')
            cur = conn.cursor()  # db연결
            print(self.rows2[0])
            for row in self.rows2:
                consum = row[3] * int(self.order_prod_quantity.text())
                cur.execute(f"UPDATE smart.ingredients \
                            SET stock = stock -  '{consum}' \
                            WHERE smart.ingredients.ingre_num = '{row[2]}';")  ##주문접수 버튼을누르면 재료테이블의 스톡을 해당 주문의 구매수량 X 소모량 만큼 빼주는 쿼리문

            cur.execute(f"SELECT * from smart.order \
                                    left join smart.product \
                                    ON smart.order.prod_num = smart.product.prod_num;")  # 오더테이블 과 프로덕트테이블 조인하여 조회
            rows1 = cur.fetchall()

            cur.execute(f"UPDATE smart.order \
                                           SET order_status = '{'접수,제작 완료'}' \
                                           WHERE smart.order.num = '{rows1[self.a][0]}';")  ##오더테이블의 num으로 조회하여 접수대기중을 접수,제작완료로 업데이트 해주는 쿼리문

            conn.commit()

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

            conn.close()
            col = 0
            for row in rows:
                self.table_order_management.setItem(col, 0, QTableWidgetItem(str(row[1])))
                self.table_order_management.setItem(col, 1, QTableWidgetItem(str(row[2])))
                self.table_order_management.setItem(col, 2, QTableWidgetItem(str(row[7])))
                self.table_order_management.setItem(col, 3, QTableWidgetItem(str(row[4])))
                self.table_order_management.setItem(col, 4, QTableWidgetItem(str((row[8] * row[4]))))  ## 총금액
                self.table_order_management.setItem(col, 5, QTableWidgetItem(str(row[5])))

                col += 1
        elif min(self.possible_make) < 1:
            QMessageBox.information(self, '알림', '자재가 부족합니다')
        else:
            QMessageBox.information(self, '알림', '이미 완료된 주문입니다')

    def product_listup(self):
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        with conn.cursor() as cur:
            sql = f"SELECT * FROM smart.product"
            cur.execute(sql)
            products = cur.fetchall()

        self.table_product.setRowCount(len(products))
        # btn = lambda x : '판매 중지' if x == True else '판매 등록'
        status = lambda x: '판매중' if x == True else '대기중'

        col = 0
        self.product = []  # 초기화
        for row in products:
            self.table_product.setItem(col, 0, QTableWidgetItem(row[1]))
            # self.product에 상품명을 추가
            self.product.append(row[1])
            self.table_product.setItem(col, 1, QTableWidgetItem(str(row[2])))
            self.table_product.setItem(col, 2, QTableWidgetItem(status(row[3])))

            self.table_product.item(col, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.table_product.item(col, 1).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_product.item(col, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col += 1

        # 테이블 헤더 폭 조정 : 합쳐서 300
        # self.table_product.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_product.setColumnWidth(0, 145)
        self.table_product.setColumnWidth(1, 75)
        self.table_product.setColumnWidth(2, 80)

        # 테이블 이벤트
        self.table_product.cellClicked.connect(self.product_matter)
        self.btn_addProduct.clicked.connect(self.add_product)

    def product_matter(self, row):
        item = self.table_product.item(row, 0)
        item = item.text()
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        with conn.cursor() as cur:
            # 특정 메뉴의 레시피 (재료, 분량, 남은 재고)
            sql = f"SELECT A.ingre_name, B.consum, A.stock  FROM ingredients A " \
                  f"LEFT JOIN recipe B ON A.ingre_num = B.ingre_num " \
                  f"WHERE prod_num = (SELECT prod_num FROM product WHERE prod_name = '{item}');"
            cur.execute(sql)
            ingre = cur.fetchall()

        self.table_ingredient.setRowCount(len(ingre))

        col = 0
        for row in ingre:
            self.table_ingredient.setItem(col, 0, QTableWidgetItem(row[0]))
            self.table_ingredient.setItem(col, 1, QTableWidgetItem(str(row[1])))
            self.table_ingredient.setItem(col, 2, QTableWidgetItem(str(row[2])))

            self.table_ingredient.item(col, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.table_ingredient.item(col, 1).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_ingredient.item(col, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            col += 1
        self.table_ingredient.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def new_recipe_plus(self):
        row = self.table_new_recipe.rowCount() + 1
        self.table_new_recipe.setRowCount(row)

    def new_recipe_minus(self):
        rowCnt = self.table_new_recipe.rowCount()
        select = self.table_new_recipe.currentRow()
        print(f'상품재료 {select}행 삭제')

        val = lambda x: x.text() if x is not None else ''

        # 행 값 읽어서 리스트에 저장
        rowList = []
        for row in range(rowCnt):
            col1 = val(self.table_new_recipe.item(row, 0))
            col2 = val(self.table_new_recipe.item(row, 1))

            print(f'{row}번 행 | {col1} | {col2}')
            rowList.append([row, col1, col2])

        rowList.pop(select)  # 선택된 행의 값 리스트에서 삭제

        # 행 수 변경
        rowCnt = rowCnt - 1
        self.table_new_recipe.setRowCount(rowCnt)

        # 셀에 리스트 값 할당
        for row in range(len(rowList)):
            if row >= select:
                self.table_new_recipe.setItem(row, 0, QTableWidgetItem(rowList[row][1]))
                self.table_new_recipe.setItem(row, 1, QTableWidgetItem(rowList[row][2]))

    def add_product(self):
        if self.in_new_item is not None:
            product = self.in_new_item.text()
            # 상품이 이미 등록 되어 있는지 확인
            if product in self.product:
                QMessageBox.warning(self, '알림', '이미 등록된 상품입니다.')
                return
        print(f'@ 상품 {product} 추가')

        # 행 값 읽어서 리스트에 저장
        rowCnt = self.table_new_recipe.rowCount()
        # 행이 하나도 없다면 종료
        if rowCnt == 0:
            QMessageBox.warning(self, '알림', '최소 1개의 레시피를 등록해주세요')
            return

        rowList = []
        val = lambda x: x.text() if x is not None else ''
        for row in range(rowCnt):
            col1 = val(self.table_new_recipe.item(row, 0))
            col2 = val(self.table_new_recipe.item(row, 1))

            if col1 != '' and col2 != '':
                rowList.append([col1, col2])

            # table_new_recipe에 비어있는 셀이 있다면
            else:
                QMessageBox.warning(self, '알림', '모든 셀의 내용을 입력해주세요')
                return
        print(f'이미 등록된 상품 아님, 비어있는 행 없음, 최소 1개의 레시피 : \n {rowList}')

        # 숫자 정규식
        isint = re.compile('[0-9]')
        check = lambda x: x if isint.match(x) != None else None

        # 재료 번호 조회
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        recipeList = []
        with conn.cursor() as cur:
            for row in rowList:
                sql = f"SELECT ingre_num FROM ingredients WHERE ingre_name = '{str(row[0])}';"
                cur.execute(sql)
                ingre = cur.fetchone()
                # 기존에 없던 재료 -- 추가 불가
                if ingre == None:
                    QMessageBox.warning(self, '알림', '존재하지 않는 재료입니다')
                    return
                # 분량이 숫자가 아닐 때 -- 추가 불가
                elif check(row[1]) == None:
                    QMessageBox.warning(self, '알림', '분량을 바르게 입력해주세요')
                    return
                else:  # 모두 바르게 입력한 경우, 레시피 리스트에 추가
                    recipeList.append([int(ingre[0]), int(row[1])])  # 재료번호, 재료분량

        # 가격 확인
        print(self.in_cost.text())
        cost = self.in_cost.text()

        # Q메시지 박스 - 상품명: {product}, 레시피 : {재료1}-{분량} / ... ... 추가하시겠습니까?
        message = f'상품명: {product} \n가격: {cost}원. \n---------레시피'
        for row in rowList:
            message = message + f'\n {str(row[0])} - {str(row[1])}ml'
        message = message + f'\n상품 목록에 추가하시겠습니까?'
        reply = QMessageBox.question(self, '상품 추가', message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # NO를 선택하면 종료
        if reply == QMessageBox.No:
            print('NO를 선택')
            return

        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart',
                               charset='utf8')
        with conn.cursor() as cur:
            # 상품 테이블에 product 추가 --
            sql = f'INSERT INTO product (prod_name, cost, pro_status)' \
                  f'VALUES(%s, %s, %s);'
            val = [product, cost, 'FALSE']
            cur.execute(sql, val)
            conn.commit()
            print(f'@{product} 추가 완료')

            # 상품 번호 가져옴 --
            sql = f"SELECT prod_num FROM product WHERE prod_name = '{product}'"
            cur.execute(sql)
            prod_num = int(cur.fetchone()[0])
            print(f'@상품번호 {prod_num}')

            # 레시피 리스트 제일 앞에 prod_num 추가
            for data in recipeList:
                data.insert(0, prod_num)
                print(f'재료 : {data}')
            print(f'레시피 : {recipeList}')

            # 레시피 테이블에 상품번호 -- 재료번호 -- 분량 추가
            sql = f"INSERT INTO recipe (prod_num, ingre_num, consum)" \
                  f"VALUES(%s, %s, %s)"
            val = recipeList
            cur.executemany(sql, val)
            conn.commit()
        QMessageBox.information(self, '상품 추가', '추가되었습니다.')

        # 상품 목록 새로 읽기
        self.product_listup()


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
