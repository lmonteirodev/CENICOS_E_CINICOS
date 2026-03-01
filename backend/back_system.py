# IMPORTS----------------------------------------------------------------------------------------------------------
# from core.database import get_connection
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5 import uic
from reportlab.pdfgen import canvas
import sys
import os


# OBJETOS-------------------------------------------------------------------------------------------------------------
class BaseScreen(QMainWindow):
    def __init__(self, ui_file):
        super().__init__()
        uic.loadUi(ui_file, self)

class ScreenController:
    def __init__(self):
        self.current_screen = None

    def show_screen(self, screen_class):
        # Fecha a tela atual, se existir
        if self.current_screen is not None:
            self.current_screen.close()

        # Cria nova tela
        self.current_screen = screen_class(self)
        self.current_screen.showMaximized()


class DashScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_dashboard.ui")
        self.controller = controller
        
        # menu_lateral
        self.btn_abrir_agenda_menu.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_cliente_menu.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_funcionario_menu.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.btn_abrir_documento_menu.clicked.connect(lambda: self.controller.show_screen(DocScreen))

        # main_dashboard_frame
        self.btn_abrir_agenda_3.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        # frames menores
        self.btn_abrir_clientes.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_agenda.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_agenda_2.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_documentos.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class AgendaScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_agenda.ui")
        self.controller = controller

        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.clientes_button.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.documentos_button.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class ClientesScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_clientes.ui")
        self.controller = controller
    
        self.agenda_button.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.documentos_button.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class FuncScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_funcionarios.ui")
        self.controller = controller
        
        self.btn_abrir_dashboard_menu.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.btn_abrir_agenda_menu.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_cliente_menu.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_documento_menu.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class DocScreen (BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_documentos.ui")
        self.controller = controller

        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.clientes_button.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.agenda_button.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = ScreenController()
    controller.show_screen(DashScreen)

    sys.exit(app.exec())