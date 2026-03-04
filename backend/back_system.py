# IMPORTS----------------------------------------------------------------------------------------------------------
from database_manager import ClienteDAO, FuncDAO
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
 
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Nome", "Documento"])

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        v_header = self.tableWidget.verticalHeader()
        v_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.atualizar_tabela()

    def atualizar_tabela(self):
        try:
            clientes = ClienteDAO.buscar_ultimos_clientes(3)
            self.tableWidget.setRowCount(len(clientes))

            for i, (nome, documento) in enumerate(clientes):
                self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(nome))
                self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(documento))
                self.tableWidget.setRowHeight(i, 40)
        
        except Exception as e:
            print(f"Erro ao carregar mini-tabela: {e}")

class AgendaScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_agenda.ui")
        self.controller = controller

        # menu_lateral
        self.btn_abrir_dashboard_menu.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.btn_abrir_cliente_menu.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_funcionario_menu.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.btn_abrir_documento_menu.clicked.connect(lambda: self.controller.show_screen(DocScreen))

class ClientesScreen(BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_clientes.ui")
        self.controller = controller
    
        # menu_lateral
        self.btn_abrir_agenda_menu.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))
        self.btn_abrir_dashboard_menu.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.btn_abrir_funcionario_menu.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.btn_abrir_documento_menu.clicked.connect(lambda: self.controller.show_screen(DocScreen))

        # frame superior
        self.pushButton.clicked.connect(lambda: self.controller.show_screen(ClientesCadScreen))

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Cliente", "Documento", "Contato", "Status", "Serviços"]
        )

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)  # Cliente
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)  # Documento
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)  # Contato
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)  # Serviços

        self.tableWidget.setColumnWidth(0, 400) # Nome do Cliente
        self.tableWidget.setColumnWidth(1, 200) # CPF/CNPJ
        self.tableWidget.setColumnWidth(2, 300) # Contato
        self.tableWidget.setColumnWidth(3, 100) # Status
        self.tableWidget.setColumnWidth(4, 100) # Qtd Serviços

        self.carregar_clientes()

    def carregar_clientes(self):
        try:
            clientes = ClienteDAO.carregar_clientes()
            self.tableWidget.setRowCount(len(clientes))

            for i, (nome, documento, telefone, email) in enumerate(clientes):
                contato = f"{email}\n{telefone}" if email and telefone else (email or telefone or "N/A")

                self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(nome))
                self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(documento))
                self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(contato))
                self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem("ATIVO"))  # ou N/A se não tiver status
                self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem("0"))      # número de serviços
                self.tableWidget.setRowHeight(i, 60)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

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
        
        # Botão de cadastro
        self.pushButton_3.clicked.connect(self.cadastrar_cliente)
        self.pushButton_4.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))

    def cadastrar_cliente (self):
        nome = self.lineEdit_1.text().strip()
        cpf_cnpj = self.lineEdit_2.text().strip()
        telefone = self.lineEdit_3.text().strip()
        email = self.lineEdit_4.text().strip()

        if not (nome and cpf_cnpj and telefone and email):
            return QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
            
        try:
            ClienteDAO.cadastrar_cliente(nome, cpf_cnpj, telefone, email)

            QtWidgets.QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso!")

            self.lineEdit_1.clear()
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

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

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Nome", "Documento", "Contato", "Status", "Cargo"]
        )

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)  # Nome
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)  # Documento
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)  # Contato
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)  # Cargo

        self.tableWidget.setColumnWidth(0, 400) # Nome
        self.tableWidget.setColumnWidth(1, 200) # CPF/CNPJ
        self.tableWidget.setColumnWidth(2, 300) # Contato
        self.tableWidget.setColumnWidth(3, 100) # Status
        self.tableWidget.setColumnWidth(4, 100) # cargo

        self.carregar_funcionarios()

    def carregar_funcionarios(self):
        try:
            funcionarios = FuncDAO.carregar_func()
            self.tableWidget.setRowCount(len(funcionarios))

            for i, (nome, documento, cargo, telefone, email) in enumerate(funcionarios):
                contato = f"{email}\n{telefone}" if email and telefone else (email or telefone or "N/A")

                self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(nome))
                self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(documento))
                self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(contato))
                self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem("ATIVO"))
                self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(cargo))  # ou N/A se não tiver status
                self.tableWidget.setRowHeight(i, 60)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

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

        # Botão de cadastro
        self.pushButton_3.clicked.connect(self.cadastrar_func)
        self.pushButton_4.clicked.connect(lambda: self.controller.show_screen(FuncScreen))

    def cadastrar_func (self):
        nome = self.lineEdit_1.text().strip()
        cpf_cnpj = self.lineEdit_2.text().strip()
        cargo = self.lineEdit_3.text().strip()
        telefone = self.lineEdit_4.text().strip()
        email = self.lineEdit_5.text().strip()

        if not (nome and cpf_cnpj and telefone and email and cargo):
            return QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
                
        try:    
            FuncDAO.cadastrar_func(nome, cpf_cnpj, telefone, cargo, email)

            QtWidgets.QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso!")
            
            self.lineEdit_1.clear()
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.lineEdit_5.clear()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

class DocScreen (BaseScreen):
    def __init__(self, controller):
        super().__init__("telas/aba_documentos.ui")
        self.controller = controller

        # menu_lateral
        self.btn_abrir_dashboard_menu.clicked.connect(lambda: self.controller.show_screen(DashScreen))
        self.btn_abrir_cliente_menu.clicked.connect(lambda: self.controller.show_screen(ClientesScreen))
        self.btn_abrir_funcionario_menu.clicked.connect(lambda: self.controller.show_screen(FuncScreen))
        self.btn_abrir_agenda_menu.clicked.connect(lambda: self.controller.show_screen(AgendaScreen))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = ScreenController()
    controller.show_screen(DashScreen)

    sys.exit(app.exec())