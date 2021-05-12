import os
import datetime
import sys
sys.path.append('./ui')

from PyQt5.QtWidgets import *
# from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from basic import Ui_MainWindow


def search(dirname, subfolder=False):
    filenames = os.listdir(dirname)
    files = []
    for filename in filenames:
        if os.path.isfile(os.path.join(dirname, filename)):
            files.append(os.path.join(dirname, filename))
        if subfolder is True and os.path.isdir(os.path.join(dirname, filename)):
            files.extend(search(os.path.join(dirname, filename), subfolder=True))
    return files


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_signal()
        self.period_or_date = 1
        self.now = datetime.datetime.now().date()
        self.dateEdit.setDate(self.now)
        self.subfolder = False

    def init_signal(self):
        self.selectButton.clicked.connect(self.select_dir)
        self.deleteButton.clicked.connect(self.delete_dir)
        self.allDeleteButton.clicked.connect(self.all_delete_dir)
        self.startButton.clicked.connect(self.start)
        self.dateButton.clicked.connect(self.check_period_or_date)
        self.periodButton.clicked.connect(self.check_period_or_date)
        self.checkBox.stateChanged.connect(self.check_subfolder)

    @pyqtSlot()
    def check_subfolder(self):
        if self.checkBox.isChecked():
            self.subfolder = True
        else:
            self.subfolder = False

    @pyqtSlot()
    def select_dir(self):
        fpath = QFileDialog.getExistingDirectory(self, '')
        dirs = [str(self.listWidget.item(i).text()) for i in range(self.listWidget.count())]
        if fpath not in dirs:
            self.listWidget.addItem(fpath)

    @pyqtSlot()
    def delete_dir(self):
        now = self.listWidget.currentRow()
        self.listWidget.takeItem(now)

    @pyqtSlot()
    def all_delete_dir(self):
        self.listWidget.clear()

    @pyqtSlot()
    def check_period_or_date(self):
        self.dateButton.setCheckable(True)
        self.periodButton.setCheckable(True)
        if self.dateButton.isChecked():
            self.periodButton.setChecked(False)
            self.periodButton.setCheckable(True)
            self.period_or_date = 1
        elif self.periodButton.isChecked():
            self.dateButton.setChecked(False)
            self.dateButton.setCheckable(True)
            self.period_or_date = 0

    @pyqtSlot()
    def start(self):
        dirs = [str(self.listWidget.item(i).text()) for i in range(self.listWidget.count())]
        if not dirs:
            self.append_log(f'폴더를 선택해주세요.')
            return
        self.append_log(f'파일 제거를 실시합니다.')
        for idx, dir in enumerate(dirs):
            if self.subfolder == True:
                files = search(dir, subfolder=True)
            else:
                files = search(dir, subfolder=False)
            setting_date = self.dateEdit.date()
            setting_date = setting_date.toPyDate()
            setting_period = self.periodEdit.value()
            now = datetime.datetime.now().date()
            delta = now - datetime.timedelta(days=setting_period)

            for file in files:
                mtime = os.path.getmtime(file)
                mtime = datetime.date.fromtimestamp(mtime)
                if self.period_or_date == 1:
                    if setting_date >= mtime:
                        os.remove(file)
                        self.append_log(f'-{file} 삭제 완료')
                elif self.period_or_date == 0:
                    if delta >= mtime:
                        os.remove(file)
                        self.append_log(f'-{file} 삭제 완료')
            self.listWidget.takeItem(0)
            self.append_log(f'{dir} 폴더 내 파일 삭제 완료 {idx+1}/{len(dirs)}')

    @pyqtSlot()
    def append_log(self, act):
        now = datetime.datetime.now()
        now_date_time = now.strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f' -{act} ({now_date_time})'
        self.plainTextEdit.appendPlainText(log_msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()


