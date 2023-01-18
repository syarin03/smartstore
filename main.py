import sys
import re
import pymysql
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegExpValidator

# path = os.getcwd()
# font_path = path + "\Pretendard-Light.otf"
# font = font_manager.FontProperties(fname=font_path).get_name()

form_class = uic.loadUiType("main.ui")[0]


# 메인 윈도우
class WindowClass(QMainWindow, form_class):
    user = None
    today = datetime.now().date().strftime('%Y-%m-%d')

    HOST = '10.10.21.110'
    PORT = 3306
    USER = 'user_t'
    PASSWORD = 'xlavmfhwprxm9'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.toolBox.currentChanged.connect(self.page_changed)
        self.table_question.itemDoubleClicked.connect(self.view_question)

    def conn_fetch(self):
        con = pymysql.connect(host=self.HOST, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()
        return cur

    def conn_commit(self):
        con = pymysql.connect(host=self.HOST, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        return con

    def page_changed(self):
        self.table_question.setRowCount(0)
        if self.toolBox.currentIndex() == 1:
            self.search_question()

    def view_question(self):
        row = self.table_question.currentIndex().row()
        col = self.table_question.currentIndex().column()
        data = self.table_question.item(row, col)
        print(row, col, data.text())


    def search_question(self):
        sql = "SELECT a.num, b.prod_name, c.order_num, a.title, a.content, a.answer " \
              "FROM question a " \
              "LEFT JOIN product b ON a.prod_num = b.prod_num " \
              "LEFT JOIN `order` c ON a.order_num = c.order_num AND a.prod_num = c.prod_num"
        print(sql)
        with self.conn_fetch() as cur:
            cur.execute(sql)
            result = cur.fetchall()
            print(result)
            self.table_question.setRowCount(len(result))
            self.table_question.setColumnWidth(0, 100)
            self.table_question.setColumnWidth(1, 100)
            self.table_question.setColumnWidth(2, 100)
            self.table_question.setColumnWidth(3, 480)
            col = 0
            for i in result:
                self.table_question.setItem(col, 0, QTableWidgetItem(str(i[0])))
                self.table_question.setItem(col, 1, QTableWidgetItem(str(i[2])))
                self.table_question.setItem(col, 2, QTableWidgetItem(str(i[1])))
                self.table_question.setItem(col, 3, QTableWidgetItem(str(i[3])))
                col += 1


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
