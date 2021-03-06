#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import json
import time
import base64
from PyQt5.Qt import QMainWindow, QApplication, QMessageBox, QInputDialog, QFileDialog
from PyQt5 import QtWidgets, QtGui, QtMultimedia, QtCore
from PyQt5.uic import loadUi
from function.NetEase.Lyric import getNCMLyric
from function.QQMusic.Lyric import getQQMLyric
from function.LyricConvert.convert import mlrc2vrc, lrcs2mlrc
from function.LyricConvert.fixaxis import fixlrcs


def NopenArgv(data):
    if (data):
        decoded = False
        for enc in ['utf-8-sig', 'utf-8', 'utf-16-le', 'gbk']:
            try:
                with open(data, 'r', encoding=enc) as f:
                    data = f.read()
                decoded = True
                break
            except OSError:
                return False, None
            except UnicodeDecodeError:
                pass
        if not decoded:
            return False, None
        else:
            return True, data
    else:
        return False, None


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self.set_ui()

        self.loadargv()
        self.textsoll(self.checkBox.checkState())

        self.checkBox.stateChanged.connect(
            lambda: self.textsoll(self.checkBox.checkState()))

    def textsoll(self, num):
        if num == 2:
            self.textEdit.horizontalScrollBar().valueChanged.connect(
                self.textEdit_2.horizontalScrollBar().setValue)
            self.textEdit.verticalScrollBar().valueChanged.connect(
                self.textEdit_2.verticalScrollBar().setValue)
            self.textEdit_2.horizontalScrollBar().valueChanged.connect(
                self.textEdit.horizontalScrollBar().setValue)
            self.textEdit_2.verticalScrollBar().valueChanged.connect(
                self.textEdit.verticalScrollBar().setValue)
        else:
            self.textEdit.horizontalScrollBar().valueChanged.disconnect(
                self.textEdit_2.horizontalScrollBar().setValue)
            self.textEdit.verticalScrollBar().valueChanged.disconnect(
                self.textEdit_2.verticalScrollBar().setValue)
            self.textEdit_2.horizontalScrollBar().valueChanged.disconnect(
                self.textEdit.horizontalScrollBar().setValue)
            self.textEdit_2.verticalScrollBar().valueChanged.disconnect(
                self.textEdit.verticalScrollBar().setValue)

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
        if len(sys.argv) > 1 and sys.argv[1] == '-t':
            loadUi('assets/index.ui', self)
        else:
            loadUi(sys.path[1] + '/assets/index.ui', self)

        # 菜单项操作
        self.action_4.triggered.connect(self.close)  # 退出
        self.action_VRC_3.triggered.connect(self.impotVrc)  # 导入VRC
        self.action_LRC_2.triggered.connect(
            lambda: self.impotLrc(0))  # 导入歌词到原文
        self.action_LRC_3.triggered.connect(
            lambda: self.impotLrc(2))  # 导入歌词到翻译
        self.action_LRC_4.triggered.connect(self.impotMixLrc)  # 导入双语LRC
        self.action_VRC_2.triggered.connect(self.vrcSave)  # 导出VRC
        self.action_LRC.triggered.connect(self.originLrcSave)  # 导出原文LRC
        self.action_out_LRC2.triggered.connect(
            self.translateLrcSave)  # 导出翻译LRC
        self.action_VtuberMusic.triggered.connect(self.about)  # 关于
        self.action_LRC_5.triggered.connect(self.output2mixlrc)  # 导出双语LRC

        # 按钮项操作
        self.toolButton.clicked.connect(lambda: self.impotLrc(0))  # 导入LRC到原歌词
        self.toolButton_2.clicked.connect(
            lambda: self.impotLrc(2))  # 导入LRC到翻译歌词
        self.toolButton_9.clicked.connect(self.impotVrc)  # 导入VRC
        self.toolButton_3.clicked.connect(self.impotMixLrc)  # 导入双语LRC
        self.toolButton_7.clicked.connect(self.vrcSave)  # 导出VRC
        self.toolButton_8.clicked.connect(self.originLrcSave)  # 导出原文LRC
        self.toolButton_11.clicked.connect(self.translateLrcSave)  # 导出翻译LRC
        self.toolButton_12.clicked.connect(self.impotNetease)  # 抓取网易云音乐歌词
        self.toolButton_10.clicked.connect(self.output2mixlrc)  # 导出双语LRC
        self.toolButton_13.clicked.connect(self.impotQQMusic)  # 导入QQ音乐歌词

    # 双击路径导入
    def loadargv(self):
        if len(sys.argv) > 1 and sys.argv[1] != '-t':
            try:
                success, data = NopenArgv(sys.argv[1])
                if success:
                    data = json.loads(data)
                    self.textEdit.setText(data["origin"]["text"])
                    
                    if "translated" not in data:
                        if "translate" in data and data["translate"]["text"] != "":
                            data["translated"] = True
                        else:
                            data["translated"] = False
                    
                    if data["translated"] == True:
                        self.textEdit_2.setText(data["translate"]["text"])
                    else:
                        self.textEdit_2.setText("")
            except (json.decoder.JSONDecodeError):
                QMessageBox.information(
                    self, '提示', '打开的不是标准的VRC格式文件', QMessageBox.Cancel)
                pass

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

                    if 'lyric' in data['tlyric'] and data['tlyric']['lyric']:
                        trans = data['tlyric']['lyric']
                        ori, trans = fixlrcs(ori, trans)
                        self.textEdit_2.setText(trans)
                    else:
                        self.textEdit_2.setText("")

                    self.textEdit.setText(ori)

            except (UnicodeDecodeError, json.decoder.JSONDecodeError, KeyError, TypeError):
                QMessageBox.warning(
                    self, '提示', '获取网易云歌词失败', QMessageBox.Cancel)
                pass

    # 导入QQ音乐歌词

    def impotQQMusic(self):
        num, ok = QInputDialog.getText(self, '抓取QQ音乐歌词', '输入QQ音乐歌曲链接：')
        if ok and num:
            try:
                data = getQQMLyric(num)

                if(data['lyric']):
                    ori = base64.b64decode(data['lyric']).decode('utf8')

                    if 'trans' in data and len(data['trans']) > 1:
                        trans = base64.b64decode(data['trans']).decode('utf8')
                        ori, trans = fixlrcs(ori, trans)
                        self.textEdit_2.setText(trans)
                    else:
                        self.textEdit_2.setText("")

                    self.textEdit.setText(ori)

            except (UnicodeDecodeError, json.decoder.JSONDecodeError, KeyError, TypeError):
                QMessageBox.warning(
                    self, '提示', '获取QQ音乐歌词失败', QMessageBox.Cancel)
                pass

    # 尝试用不同编码打开文件，返回成功状态和文件内容
    def openFile(self):
        fname = QFileDialog.getOpenFileName(
            self, '打开文件', ".", "All Files (*);;Vrc Files (*.vrc);;Text Files (*.txt);;Lrc Files (*.lrc);;Srt Files (*.srt);;Ass Files (*.ass)")
        if fname[0]:
            decoded = False
            for enc in ['utf-8-sig', 'utf-8', 'utf-16-le', 'gbk']:
                try:
                    with open(fname[0], 'r', encoding=enc) as f:
                        data = f.read()
                    decoded = True
                    break
                except OSError:
                    QMessageBox.warning(
                        self, '提示', '导入失败, 发生错误', QMessageBox.Cancel)
                    return False, None
                except UnicodeDecodeError:
                    pass
            if not decoded:
                QMessageBox.warning(self, '提示', '编码格式不支持', QMessageBox.Cancel)
                return False, None
            else:
                return True, data
        else:
            return False, None

    # 打开LRC文件
    def impotLrc(self, num):
        success, data = self.openFile()
        if success:
            if(num != 2):
                self.textEdit.setText(data)
            else:
                self.textEdit_2.setText(data)

    # 打开VRC文件
    def impotVrc(self):
        try:
            success, data = self.openFile()
            if success:
                data = json.loads(data)
                self.textEdit.setText(data["origin"]["text"])
                if(data["translated"] == True):
                    self.textEdit_2.setText(data["translate"]["text"])
                else:
                    self.textEdit_2.setText("")
        except (json.decoder.JSONDecodeError):
            QMessageBox.information(
                self, '提示', '打开的不是标准的VRC格式文件', QMessageBox.Cancel)
            pass

    # 导入双语LRC文件
    def impotMixLrc(self):
        success, data = self.openFile()
        if success:
            data = mlrc2vrc(data)
            self.textEdit.setText(data["origin"]["text"])
            self.textEdit_2.setText(data["translate"]["text"])

    # 导出VRC
    def vrcSave(self):
        try:
            if(len(self.textEdit.toPlainText()) < 1):
                QMessageBox.information(
                    self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
            else:
                filename = QFileDialog.getSaveFileName(
                    self, '保存', '.', "Vrc Files (*.vrc);;All Files (*)")

                origin = self.textEdit.toPlainText()
                translate = self.textEdit_2.toPlainText()

                vrc_obj = {
                    'karaoke': False,
                    'scrollDisabled': False,
                }

                with open(filename[0], 'w', encoding='utf-8') as f:

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
                        QMessageBox.information(
                            self, '提示', '导出成功', QMessageBox.Cancel)
                    else:
                        QMessageBox.warning(
                            self, '提示', '导出失败', QMessageBox.Cancel)
        except FileNotFoundError:
            pass

    # 导出原文LRC
    def originLrcSave(self):
        try:
            origin = self.textEdit.toPlainText()

            if(len(origin) > 0):
                filename = QFileDialog.getSaveFileName(
                    self, '保存', '.', "Lrc Files (*.lrc);;Text Files (*.txt);;All Files (*)")
                with open(filename[0], 'w', encoding='utf-8') as f:
                    f.write(origin)
                    f.close()
            else:
                QMessageBox.information(
                    self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
        except FileNotFoundError:
            pass

    # 导出原文LRC
    def translateLrcSave(self):
        try:
            translate = self.textEdit_2.toPlainText()

            if(len(translate) > 0):
                filename = QFileDialog.getSaveFileName(
                    self, '保存', '.', "Lrc Files (*.lrc);;Text Files (*.txt);;All Files (*)")
                with open(filename[0], 'w', encoding='utf-8') as f:
                    f.write(translate)
                    f.close()
            else:
                QMessageBox.information(
                    self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
        except FileNotFoundError:
            pass

    # 导出双语LRC
    def output2mixlrc(self):
        try:
            origin = self.textEdit.toPlainText()
            translate = self.textEdit_2.toPlainText()
            if(len(origin) > 0 and len(translate) > 0):
                newdata = lrcs2mlrc(origin, translate)

                filename = QFileDialog.getSaveFileName(
                    self, '保存', '.', "Lrc Files (*.lrc);;Text Files (*.txt);;All Files (*)")
                with open(filename[0], 'w', encoding='utf-8') as f:
                    f.write(newdata)
                    f.close()
            else:
                QMessageBox.information(
                    self, '提示', '无法导出，内容为空', QMessageBox.Cancel)
        except FileNotFoundError:
            pass


if __name__ == "__main__":

    new = []
    new.append(sys.argv[0])

    app = QApplication(new)

    # 创建启动界面，支持png透明图片
    if len(sys.argv) > 1 and sys.argv[1] == '-t':
        splash = QtWidgets.QSplashScreen(
            QtGui.QPixmap('assets/images/splash.png'))

    else:
        splash = QtWidgets.QSplashScreen(
            QtGui.QPixmap(sys.path[1] + '/assets/images/splash.png'))
    splash.show()

    # 可以显示启动信息
    splash.showMessage("启动中...", QtCore.Qt.AlignRight |
                       QtCore.Qt.AlignBottom, QtCore.Qt.white)

    time.sleep(1)

    # 关闭启动画面
    splash.close()

    window = Window()
    window.show()

    sys.exit(app.exec_())
