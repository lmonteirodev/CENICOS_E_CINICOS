from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
w = QtWidgets.QMainWindow()
w.showFullScreen()
sys.exit(app.exec_())