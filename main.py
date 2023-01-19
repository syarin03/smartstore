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

from pyqt5_plugins.examplebuttonplugin import QtGui

# path = os.getcwd()
# font_path = path + "\Pretendard-Light.otf"
# font = font_manager.FontProperties(fname=font_path).get_name()

form_class = uic.loadUiType("mainUI.ui")[0]


# 메인 윈도우
class WindowClass(QMainWindow, form_class):
    user = None
    today = datetime.now().date().strftime('%Y-%m-%d')

    HOST = '10.10.21.110'
    PORT = 3306
    USER = 'user_t'
    PASSWORD = 'xlavmfhwprxm9'

    product = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.id_bool = False  # ID가 중복인지 확인하는 값
        self.loginbool = False  # 로그인 유무 확인 값

        # 초기 화면 설정
        self.Page.setCurrentWidget(self.p_intro)
        self.Page.setCurrentWidget(self.p_main)
        self.page_login.setCurrentWidget(self.pl_01)
        self.Menu.setCurrentWidget(self.p_stock)
        self.product_listup()

        # 로그인 / 로그아웃
        self.btn_login.clicked.connect(self.login)
        self.btn_join.clicked.connect(self.into_join)
        self.btn_check.clicked.connect(self.idcheck)
        self.btn_newuser.clicked.connect(self.signup)
        self.btn_gomain.clicked.connect(self.gohome)

        # 상품추가
        self.btn_add.clicked.connect(self.new_recipe_plus)
        self.btn_del.clicked.connect(self.new_recipe_minus)
        input_rule = QRegExp("[0-9]{0,6}")  # 0부터 9까지의 숫자 길이 제한 없음
        self.in_cost.setValidator(QRegExpValidator(input_rule, self))

    def login(self):
        print('로그인 함수')
        id = self.in_id_login.text()  # id에 입력한 아이디 대입
        pw = self.in_pw_login.text()
        con = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
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
            self.label_loginid.setText(self.member_info[0][3])

    def logout(self):
        print('로그아웃 함수')

    def gohome(self):
        self.Page.setCurrentWidget(self.p_intro)

    def into_join(self):
        print('회원가입 페이지 이동')
        self.Page.setCurrentWidget(self.p_join)

    def idcheck(self):  # id 중복체크 함수
        id = self.in_id.text()  # id에 입력한 아이디 대입
        print(id)

        con = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
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

        con = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
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


    def product_listup(self):
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        with conn.cursor() as cur:
            sql = f"SELECT * FROM smart.product"
            cur.execute(sql)
            products = cur.fetchall()

        self.table_product.setRowCount(len(products))
        # btn = lambda x : '판매 중지' if x == True else '판매 등록'
        status = lambda x : '판매중' if x == True else '대기중'

        col = 0
        self.product = [] # 초기화
        for row in products:
            self.table_product.setItem(col, 0, QTableWidgetItem(row[1]))
            # self.product에 상품명을 추가
            self.product.append(row[1])
            self.table_product.setItem(col, 1, QTableWidgetItem(str(row[2])))
            self.table_product.setItem(col, 2,  QTableWidgetItem(status(row[3])))

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
        print(f'@ {item} - 재료표시')
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
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

        val = lambda x : x.text() if x is not None else ''

        # 행 값 읽어서 리스트에 저장
        rowList = []
        for row in range(rowCnt):

            col1 = val(self.table_new_recipe.item(row, 0))
            col2 = val(self.table_new_recipe.item(row, 1))

            print(f'{row}번 행 | {col1} | {col2}')
            rowList.append([row, col1, col2])

        rowList.pop(select) # 선택된 행의 값 리스트에서 삭제

        # 행 수 변경
        rowCnt = rowCnt- 1
        self.table_new_recipe.setRowCount(rowCnt)

        # 셀에 리스트 값 할당
        for row in range(len(rowList)):
            if row >= select:
                self.table_new_recipe.setItem(row, 0, QTableWidgetItem(rowList[row][1]))
                self.table_new_recipe.setItem(row, 1, QTableWidgetItem(rowList[row][2]))

    def add_product(self):
        if self.in_new_item is not None :
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
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
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
                elif check(row[1]) == None :
                    QMessageBox.warning(self, '알림', '분량을 바르게 입력해주세요')
                    return
                else: # 모두 바르게 입력한 경우, 레시피 리스트에 추가
                    recipeList.append([int(ingre[0]), int(row[1])]) # 재료번호, 재료분량

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

        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
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
