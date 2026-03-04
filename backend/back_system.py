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
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)           # Cliente
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # Documento
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)           # Contato
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)  # Serviços


        self.carregar_clientes()

    def carregar_clientes(self):
        conexao = get_connection()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT c.nome, c.cpf_cnpj, t.telefone, e.email
            FROM cliente c
            LEFT JOIN telefone_cliente t ON t.ID_cliente = c.ID_cliente
            LEFT JOIN email_cliente e ON e.ID_cliente = c.ID_cliente
        """)
        clientes = cursor.fetchall()

        self.tableWidget.setRowCount(len(clientes))

        for i, (nome, documento, telefone, email) in enumerate(clientes):
            contato = f"{email}, {telefone}" if email and telefone else (email or telefone or "N/A")

            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(nome))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(documento))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(contato))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem("ATIVO"))  # ou N/A se não tiver status
            self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem("0"))      # número de serviços

        cursor.close()
        conexao.close()


        

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
        try:
            conexao = get_connection()
            if not conexao:
                QtWidgets.QMessageBox.critical(self, "Erro", "Sem conexão com banco de dados.")
                return
            
            def definir_tipo_pessoa (cpf_cnpj: str):
                somente_numeros = re.sub(r'\D', '', cpf_cnpj)
                if len(somente_numeros) == 11:
                    return 'F'
                elif len(somente_numeros) == 14:
                    return 'J' 
                else: raise ValueError("CPF/CNPJ inválido")

            nome = self.lineEdit_1.text().strip()
            cpf_cnpj = self.lineEdit_2.text().strip()
            telefone = self.lineEdit_3.text().strip()
            email = self.lineEdit_4.text().strip()

            if not (nome and cpf_cnpj and telefone and email):
                QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
                conexao.close()
                return
            
            tipo_pessoa = definir_tipo_pessoa(cpf_cnpj)
        
            cursor = conexao.cursor()

            # 1. Inserir cliente
            sql_cliente = """INSERT INTO cliente (nome, cpf_cnpj, tipo_pessoa) VALUES (%s, %s, %s)"""
            valores_cliente = (nome, cpf_cnpj, tipo_pessoa)
            cursor.execute(sql_cliente, valores_cliente)

            # 2. Obter o ID do cliente inserido
            ID_cliente = cursor.lastrowid

            # 3. Inserir telefone vinculado ao cliente
            sql_telefone = """INSERT INTO telefone_cliente (telefone, iD_cliente) VALUES (%s, %s)"""
            valores_telefone = (telefone, ID_cliente)
            cursor.execute(sql_telefone, valores_telefone)

            # 4. Inserir email vinculado ao cliente
            sql_email = """INSERT INTO email_cliente (email, id_cliente) VALUES (%s, %s)"""
            valores_email = (email, ID_cliente)
            cursor.execute(sql_email, valores_email)

            # Finalizar
            conexao.commit()
            cursor.close()
            conexao.close()

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
        try:
            conexao = get_connection()
            if not conexao:
                QtWidgets.QMessageBox.critical(self, "Erro", "Sem conexão com banco de dados.")
                return
            
            def definir_tipo_pessoa (cpf_cnpj: str):
                somente_numeros = re.sub(r'\D', '', cpf_cnpj)
                if len(somente_numeros) == 11:
                    return 'F'
                elif len(somente_numeros) == 14:
                    return 'J' 
                else: raise ValueError("CPF/CNPJ inválido")

            nome = self.lineEdit_1.text().strip()
            cpf_cnpj = self.lineEdit_2.text().strip()
            cargo = self.lineEdit_3.text().strip()
            telefone = self.lineEdit_4.text().strip()
            email = self.lineEdit_5.text().strip()

            if not (nome and cpf_cnpj and telefone and email and cargo):
                QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
                conexao.close()
                return
            
            tipo_pessoa = definir_tipo_pessoa(cpf_cnpj)
        
            cursor = conexao.cursor()

            # Inserir funcuinario
            sql_funcionario = """INSERT INTO funcionario (nome, cpf_cnpj, tipo_pessoa, cargo, email) VALUES (%s, %s, %s, %s, %s)"""
            valores_funcionario = (nome, cpf_cnpj, tipo_pessoa, cargo, email)
            cursor.execute(sql_funcionario, valores_funcionario)

            # Obter o ID do funcionario inserido
            ID_funcionario = cursor.lastrowid

            # Inserir telefone vinculado ao funcionario
            sql_telefone = """INSERT INTO telefone_funcionario (telefone, iD_funcionario) VALUES (%s, %s)"""
            valores_telefone = (telefone, ID_funcionario)
            cursor.execute(sql_telefone, valores_telefone)

            # Finalizar
            conexao.commit()
            cursor.close()
            conexao.close()

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

    # ClientesCadScreen.pushButton_3.clicked.connect(ClientesCadScreen.cadastrar_cliente)
    sys.exit(app.exec())