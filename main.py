import os
import sys
import time

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QAbstractItemView, QMessageBox, QHeaderView
from matplotlib import font_manager
from datetime import datetime, timedelta

from YR import *

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

    # 초기 화면 설정
    #     self.Page.setCurrentWidget(self.p_intro)
        self.Page.setCurrentWidget(self.p_main)
        self.Menu.setCurrentWidget(self.p_stock)
        self.table_product()

    # 로그인 / 로그아웃
        self.btn_login.clicked.connect(self.login)
        # self.btn_logout.clicked.connect(self.logout) 로그아웃 아직 없음
        self.btn_join.clicked.connect(self.into_join)


    def login(self):
        print('로그인 함수')
    def logout(self):
        print('로그아웃 함수')
    def into_join(self):
        print('회원가입 페이지 이동')
        self.Page.setCurrentWidget(self.p_join)
    def table_product(self):
        print('테이블 표시')
        rows = product()
        self.product_table.setRowCount(len(rows))
        col = 0
        for row in rows:
            self.product_table.setItem(col, 0, QTableWidgetItem(row[1]))
            self.product_table.setItem(col, 1, QTableWidgetItem(str(row[2])))
            self.product_table.item(col, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col += 1

        # 테이블 헤더 폭 조정
        # self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setColumnWidth(0, 130)
        self.product_table.setColumnWidth(1, 100)


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()