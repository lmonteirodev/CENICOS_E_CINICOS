# IMPORTS----------------------------------------------------------------------------------------------------------
from database import get_connection
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtWidgets
# from reportlab.pdfgen import canvas
import sys
# import os
import re


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
        self.btn_abrir_novo_cliente_2.clicked.connect(lambda: self.controller.show_screen(ClientesCadScreen))
        
        # frames menores
        self.btn_abrir_clientes.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_agenda.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_agenda_2.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_documentos.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class AgendaScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_agenda.ui")
        self.controller = controller

        # menu_lateral
        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.clientes_button.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.documentos_button.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class ClientesScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_clientes.ui")
        self.controller = controller
    
        # menu_lateral
        self.agenda_button.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.documentos_button.clicked.connect(lambda: self.controller.show_screen(DocScreen))

        # frame superior
        self.pushButton.clicked.connect(lambda: self.controller.show_screen(ClientesCadScreen))

class ClientesCadScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_clientes_cad.ui")
        self.controller = controller

        # menu_lateral
        self.clientes_button.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.agenda_button.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.documentos_button.clicked.connect(lambda: self.controller.show_screen(DocScreen))

        # frame superior
        self.pushButton_2.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))

    def cadastrar_cliente ():
        try:
            conexao = get_connection()
            if not conexao:
                QtWidgets.QMessageBox.critical(ClientesCadScreen, "Erro", "Sem conexão com banco de dados.")
                return
            
            def definir_tipo_pessoa (cpf_cnpj: str):
                somente_numeros = re.sub(r'\D', '', cpf_cnpj)
                if len(somente_numeros) == 11:
                    return 'F'
                elif len(somente_numeros) == 14:
                    return 'J' 
                else: raise ValueError("CPF/CNPJ inválido")

            nome = ClientesCadScreen.lineEdit_1.text().strip()
            cpf_cnpj = ClientesCadScreen.lineEdit_2.text().strip()
            telefone = ClientesCadScreen.lineEdit_3.text().strip()
            email = ClientesCadScreen.lineEdite_4.text().strip()

            if not (nome and cpf_cnpj and telefone and email):
                QtWidgets.QMessageBox.warning(ClientesCadScreen, "Aviso", "Preencha todos os campos.")
                conexao.close()
                return
            
            tipo_pessoa = definir_tipo_pessoa()
        
            cursor = conexao.cursor()
            sql = """INSERT INTO cliente (nome, cpf_cnpj, tipo_pessoa) VALUES (%s, %s, %s)"""
            sql2 = """INSERT INTO telefone_cliente (telefone) VALUES (%s)"""
            sql3 = """INSERT INTO email_cliente (email) VALUES (%s)"""
            valores = (nome, cpf_cnpj, telefone, email, tipo_pessoa)

            cursor.execute(sql, sql2, sql3, valores)
            conexao.commit()
            cursor.close()
            conexao.close()

            QtWidgets.QMessageBox.information(ClientesCadScreen, "Sucesso", "Cliente cadastrado com sucesso!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(ClientesCadScreen, "Erro", f"Ocorreu um erro: {str(e)}")


class FuncScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_funcionarios.ui")
        self.controller = controller
        
        # menu_lateral
        self.btn_abrir_dashboard_menu.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.btn_abrir_agenda_menu.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_cliente_menu.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_documento_menu.clicked.connect(lambda: self.controller.show_screen(DocScreen))

        # frame superior
        self.pushButton.clicked.connect(lambda: self.controller.show_screen(FuncCadScreen))

class FuncCadScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_funcionarios_cad.ui")
        self.controller = controller

        # menu_lateral
        self.btn_abrir_dashboard_menu.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.btn_abrir_agenda_menu.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_cliente_menu.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_funcionario_menu.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.btn_abrir_documento_menu.clicked.connect(lambda: self.controller.show_screen(DocScreen))

        # frame superior
        self.pushButton_2.clicked.connect(lambda: self.controller.show_screen(FuncScreen))

class DocScreen (BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_documentos.ui")
        self.controller = controller

        # menu_lateral
        self.dashboard_button.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.clientes_button.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.funcionarios_button.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.agenda_button.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = ScreenController()
    controller.show_screen(DashScreen)

    # ClientesCadScreen.pushButton_3.clicked.connect(ClientesCadScreen.cadastrar_cliente)
    sys.exit(app.exec())