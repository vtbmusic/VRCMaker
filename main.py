#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import re
import json
import requests
from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtGui
from PyQt5.uic import loadUi

NCMLyricApi = 'http://music.163.com/api/song/lyric?lv=-1&tv=-1&id='
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


def getNCMLyric(data):
    isUrl = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', data)

    try:
        if(isUrl[0] == "http://music.163.com" or isUrl[0] == "https://music.163.com"):
            pattern = re.compile(r"^http[s]?://.*[^\w]+id=(\d*).*")
            matches = pattern.findall(data)
            id = matches[0]
            res = json.loads(requests.get(url=NCMLyricApi + id, headers=headers).text)
        else:
            res = json.loads(requests.get(url=NCMLyricApi + data, headers=headers).text)
        return res
    except IndexError:
        pass

def convert(ori_txt):
    vrc_obj = {
        'karaoke': False,
        'scrollDisabled': False,
        'origin': {
            'version': 2,
            'text': ''
        },
        'translate': {
            'version': 2,
            'text': ''
        }
    }

    pattern = re.compile(r'(\[.*?\])\s*([^\[\]]*)\s*')
    matches = pattern.findall(ori_txt)
    for time_stamp, lrc in matches:
        lrc = lrc.strip().split('\n')
        vrc_obj['origin']['text'] += time_stamp + lrc[0] + '\n'
        if len(lrc) > 1:
            vrc_obj['translate']['text'] += time_stamp + lrc[1] + '\n'

    return vrc_obj


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self.set_ui()
    
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '退出',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def set_ui(self):
        loadUi('assets/index.ui', self)
        print(dir(self))

        # 菜单项操作
        self.action_4.triggered.connect(self.close) # 退出
        self.action_VRC_3.triggered.connect(self.impotVrc) # 导入VRC
        self.action_LRC_2.triggered.connect(lambda: self.impotLrc(0)) # 导入歌词到原文
        self.action_LRC_3.triggered.connect(lambda: self.impotLrc(2)) # 导入歌词到翻译
        self.action_LRC_4.triggered.connect(self.impotMixLrc) # 导入双语LRC
        self.action_VRC_2.triggered.connect(self.vrcSave) # 导出VRC
        self.action_LRC.triggered.connect(self.originLrcSave) # 导出原文LRC
        self.action_out_LRC2.triggered.connect(self.translateLrcSave) # 导出翻译LRC
        self.action_VtuberMusic.triggered.connect(self.about) # 关于

        # 按钮项操作
        self.toolButton.clicked.connect(lambda: self.impotLrc(0))  # 导入LRC到原歌词
        self.toolButton_2.clicked.connect(
            lambda: self.impotLrc(2))  # 导入LRC到翻译歌词
        self.toolButton_9.clicked.connect(self.impotVrc)  # 导入VRC
        self.toolButton_3.clicked.connect(self.impotMixLrc) # 导入双语LRC
        self.toolButton_7.clicked.connect(self.vrcSave) # 导出VRC
        self.toolButton_8.clicked.connect(self.originLrcSave) # 导出原文LRC
        self.toolButton_11.clicked.connect(self.translateLrcSave) # 导出翻译LRC
        self.toolButton_12.clicked.connect(self.impotNetease) # 抓取网易云音乐歌词

    # 关于
    def about(self):
        text = "VRC Maker 是由我们研发的自用歌词工具，\n同时支持LRC和我们(VtuberMusic开发组)自用的VRC格式歌词的导出。\n\n开发：\nKurokitu\nLovEver\n协力/图标：\nbyoukinn"

        QMessageBox.information(self, '关于', text, QMessageBox.Yes)

    # 导入网易云音乐歌词
    def impotNetease(self):
        num, ok = QInputDialog.getText(self, '抓取网易云音乐歌词', '输入网易云音乐歌曲链接或ID：')
        if ok and num:
            try:
                data = getNCMLyric(num)
            
                if(data['lrc']['lyric']):
                        ori = data['lrc']['lyric']
                        trans = data['tlyric']['lyric']

                        self.textEdit.setText(ori)
                        self.textEdit_2.setText(trans)
            except (UnicodeDecodeError, json.decoder.JSONDecodeError, KeyError, TypeError):
                QMessageBox.warning(self, '提示', '获取网易云歌词失败', QMessageBox.Cancel)
                pass

    # 打开LRC文件
    def impotLrc(self, num):
        fname = QFileDialog.getOpenFileName(
            self, '打开文件', ".", "All Files (*);;Text Files (*.txt);;Lrc Files (*.lrc)")
        if fname[0]:
            for enc in ['utf8', 'utf-16-le', 'gbk', 'ANSI', 'utf-8-sig']:
                try:
                    with open(fname[0], 'r', encoding=enc) as f:
                        data = f.read()
                        if(num != 2):
                            self.textEdit.setText(data)
                        else:
                            self.textEdit_2.setText(data)
                    decoded = True
                except OSError:
                    QMessageBox.warning(self, '提示', '导入失败, 发生错误', QMessageBox.Cancel)
                except UnicodeDecodeError:
                    pass

    # 打开VRC文件
    def impotVrc(self):
        fname = QFileDialog.getOpenFileName(
            self, '打开文件', ".", "Vrc Files (*.vrc);;All Files (*)")
        if fname[0]:
            for enc in ['utf-8-sig', 'utf8', 'utf-16-le', 'gbk', 'ANSI']:
                try:
                    with open(fname[0], 'r', encoding=enc) as f:
                        data = json.load(f)

                        self.textEdit.setText(data["origin"]["text"])
                        if(data["translated"] == True):
                            self.textEdit_2.setText(data["translate"]["text"])
                        else:
                            self.textEdit_2.setText("")
                except (UnicodeDecodeError, json.decoder.JSONDecodeError, OSError, UnboundLocalError):
                    #QMessageBox.warning(self, '提示', '导入失败, 发生错误', QMessageBox.Cancel)
                    pass

    # 导入双语LRC文件
    def impotMixLrc(self):
        fname = QFileDialog.getOpenFileName(
            self, '打开文件', ".", "All Files (*);;Text Files (*.txt);;Lrc Files (*.lrc)")
        if fname[0]:
            for enc in ['utf-8-sig', 'utf8', 'utf-16-le', 'gbk', 'ANSI']:
                try:
                    with open(fname[0], 'r', encoding=enc) as f:
                        data = f.read()

                        newobj = convert(data)

                        self.textEdit.setText(newobj["origin"]["text"])
                        self.textEdit_2.setText(newobj["translate"]["text"])

                    decoded = True
                except OSError:
                    QMessageBox.warning(self, '提示', '导入失败, 发生错误', QMessageBox.Cancel)
                except UnicodeDecodeError:
                    pass

    # 导出VRC
    def vrcSave(self):
        try:
            if(len(self.textEdit.toPlainText()) < 1):
                    QMessageBox.information(self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
            else:
                filename = QFileDialog.getSaveFileName(
                    self, '保存', '.', "Vrc Files (*.vrc);;All Files (*)")

                origin = self.textEdit.toPlainText()
                translate = self.textEdit_2.toPlainText()

                vrc_obj = {
                    'karaoke': False,
                    'scrollDisabled': False,
                }

                with open(filename[0], 'w', encoding = 'utf-8') as f:
                    
                    if(len(translate) < 1):
                        vrc_obj["translated"] = False
                        vrc_obj["origin"] = {}
                        vrc_obj["origin"]["version"] = 2
                        vrc_obj["origin"]["text"] = origin
                    else:
                        vrc_obj["translated"] = True
                        vrc_obj["origin"] = {}
                        vrc_obj["origin"]["version"] = 2
                        vrc_obj["origin"]["text"] = origin
                        vrc_obj["translate"] = {}
                        vrc_obj["translate"]["version"] = 2
                        vrc_obj["translate"]["text"] = translate
                    state = json.dump(vrc_obj, f, ensure_ascii=False, indent=2)
                    if(state == None):
                        QMessageBox.information(self, '提示', '导出成功', QMessageBox.Cancel)
                    else:
                        QMessageBox.warning(self, '提示', '导出失败', QMessageBox.Cancel)
        except FileNotFoundError:
            pass

    # 导出原文LRC
    def originLrcSave(self):
        try:
            origin = self.textEdit.toPlainText()

            if(len(origin) > 0):
                filename = QFileDialog.getSaveFileName(
                self, '保存', '.', "Lrc Files (*.lrc);;Text Files (*.txt);;All Files (*)")
                with open(filename[0], 'w', encoding = 'utf-8') as f:
                    f.write(origin)
                    f.close()
            else:
                QMessageBox.information(self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
        except FileNotFoundError:
            pass

    # 导出原文LRC
    def translateLrcSave(self):
        try:
            translate = self.textEdit_2.toPlainText()

            if(len(translate) > 0):
                filename = QFileDialog.getSaveFileName(
                self, '保存', '.', "Lrc Files (*.lrc);;Text Files (*.txt);;All Files (*)")
                with open(filename[0], 'w', encoding = 'utf-8') as f:
                    f.write(translate)
                    f.close()
            else:
                QMessageBox.information(self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
        except FileNotFoundError:
            pass
        
            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建启动界面，支持png透明图片
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap('assets/images/splash.png'))
    splash.show()

    # 可以显示启动信息
    splash.showMessage('正在加载……')

    # 关闭启动画面
    splash.close()

    window = Window()
    window.show()
    sys.exit(app.exec_())
