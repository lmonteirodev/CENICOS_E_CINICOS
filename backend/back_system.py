# IMPORTS----------------------------------------------------------------------------------------------------------
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5 import uic
from reportlab.pdfgen import canvas
import sys
import os

# DATABASE---------------------------------------------------------------------------------------------------------
conexao = mysql.connector.connect(
    host='Localhost',
    user='root',
    password='0709',
    database='db_cenicosecinicos',
)
cursor = conexao.cursor()

def get_connection():
    """Abre uma conexão usando MySQL."""
    try:
        conn = mysql.connector.connect(**conexao)
        return conn
    except Exception as e:
        print(f"[ERRO CONEXÃO] {e}")
        return None

# OBJETOS-------------------------------------------------------------------------------------------------------------
class DashScreen(QMainWindow):
    '''Abre a tela Dashboard do programa'''
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join("telas", "aba_dashboard.ui"), self)

        self.btn_abrir_agenda_3.clicked.connect(self.abrir_agenda)
        self.btn_abrir_agenda_menu.clicked.connect(self.abrir_agenda)
        self.btn_abrir_cliente_menu.clicked.connect(self.abrir_cliente)
        self.btn_abrir_funcionario_menu.clicked.connect(self.abrir_funcionarios)
        self.btn_abrir_documento_menu.clicked.connect(self.abrir_doc)

    def abrir_cliente (self):
        self.clientes = ClientesScreen()
        self.clientes.show()

    def abrir_agenda (self):
        self.agenda = AgendaScreen()
        self.agenda.show()

    def abrir_funcionarios (self):
        self.funcionarios = FruncScreen()
        self.funcionarios.show()

    def abrir_doc (self):
        self.doc = DocScreen()
        self.doc.show()


class AgendaScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join("telas", "aba_agenda.ui"), self)

class ClientesScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join("telas", "aba_clientes.ui"), self)

class FruncScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join("telas", "aba_funcionarios.ui"), self)

class DocScreen (QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join("telas", "aba_documentos.ui"), self)




if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Carrega UIs da pasta 'telas'
    dash = DashScreen()

    dash.show()
    # inicia o loop de eventos da aplicação
    sys.exit(app.exec())