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
    prod_dic = dict()

    HOST = '10.10.21.110'
    PORT = 3306
    USER = 'user_t'
    PASSWORD = 'xlavmfhwprxm9'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.label_qna_num.setVisible(False)

        self.stackedWidget.setCurrentWidget(self.stack_main)
        self.stackedWidget.currentChanged.connect(self.page_changed)
        self.table_qna.itemDoubleClicked.connect(self.view_question)
        self.btn_go_qna_manage.clicked.connect(self.go_qna)
        self.btn_answer_to_qna.clicked.connect(self.go_qna)
        self.btn_go_qna_add.clicked.connect(self.go_question)
        self.btn_qna_to_main.clicked.connect(self.go_main)
        self.btn_question_to_main.clicked.connect(self.go_main)
        self.btn_question.clicked.connect(self.question)
        self.btn_answer.clicked.connect(self.answer)

    def conn_fetch(self):
        con = pymysql.connect(host=self.HOST, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        cur = con.cursor()
        return cur

    def conn_commit(self):
        con = pymysql.connect(host=self.HOST, user=self.USER, password=self.PASSWORD, db='smart', charset='utf8')
        return con

    def go_main(self):
        self.stackedWidget.setCurrentWidget(self.stack_main)

    def go_qna(self):
        self.stackedWidget.setCurrentWidget(self.stack_qna)
        sql = "SELECT a.num, b.prod_name, c.order_num, a.title, a.content, a.answer " \
              "FROM question a " \
              "LEFT JOIN product b ON a.prod_num = b.prod_num " \
              "LEFT JOIN `order` c ON a.order_num = c.order_num"
              # "LEFT JOIN `order` c ON a.order_num = c.order_num AND a.prod_num = c.prod_num"
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
        self.stackedWidget.setCurrentWidget(self.stack_add_question)
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
                self.stackedWidget.setCurrentWidget(self.stack_qna)
                self.go_qna()

    def question(self):
        q_title = self.edit_question_title.text()
        q_prod = self.combo_question_prod.currentText()
        q_order = self.edit_question_order.text()
        q_content = self.edit_question_content.toPlainText()

        if q_title == '' or q_content == '':
            QMessageBox.warning(self, '경고', '제목과 내용 입력란을 확인해주세요')
            return

        if q_order != '':
            sql = f"SELECT order_num FROM `order` WHERE order_num = {q_order}"
            print(sql)
            with self.conn_fetch() as cur:
                cur.execute(sql)
                result = cur.fetchall()
                print(result)
                print(result[0])
                print(int(q_order) in result[0])
                if int(q_order) not in result[0]:
                    QMessageBox.warning(self, '경고', '입력하신 주문번호가 존재하지 않습니다')
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
                self.stackedWidget.setCurrentWidget(self.stack_main)

    def page_changed(self):
        self.table_qna.setRowCount(0)
        self.edit_question_content.clear()
        self.edit_question_order.clear()
        self.edit_question_title.clear()

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
        self.stackedWidget.setCurrentWidget(self.stack_qna_detail)


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # WindowClass의 인스턴스 생성
    mainWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    mainWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
