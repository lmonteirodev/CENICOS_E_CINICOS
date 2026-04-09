# ============================== IMPORTS ===========================
from database_manager import ClienteDAO, FuncDAO, AgendamentoDAO
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QDate, QFileInfo, QDateTime
from PyQt5.QtWidgets import QButtonGroup, QFileIconProvider, QInputDialog, QFileDialog, QMessageBox
import sys
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import re
#================================= API =============================

# Escopo para leitura e escrita no Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def obter_credenciais():
    creds = None
    # O arquivo token.json armazena o acesso do usuário
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se não houver credenciais válidas, peça ao usuário para logar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Aqui ele lê o arquivo que você baixou do Google
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva as credenciais para a próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# ======================== FUNÇÃO MESTRA ============================


def _connect_menu_buttons(parent, controller):
    for btn in parent.findChildren(QtWidgets.QPushButton):
        tela = btn.property("tela")

        if not tela:
            nome = btn.objectName()
            if nome.startswith("btn_abrir_"):
                tela = nome.replace("btn_abrir_", "").replace("_menu", "")
                tela = re.sub(r'_\d+$', '', tela)  # remove _2, _3...

            if tela in ["cliente", "funcionario", "documento"]:
                    tela += "s"


        if tela:
            print(f"{btn.objectName()} -> {tela}")
            btn.clicked.connect(lambda _, t=tela: controller.show_screen(t))

# ======================== CLASSES DE TELAS =========================
class DashScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_dashboard.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")

        self._connect_buttons()

        if self.tableWidget:
            self.configurar_tabela_resumo()
            self.carregar_dados_recentes()

    def configurar_tabela_resumo(self):
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Nome", "Documento"])
        
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setShowGrid(False)

    def carregar_dados_recentes(self):
        """Busca os últimos clientes cadastrados para exibir no resumo"""
        try:
            clientes = ClienteDAO.carregar_clientes() 
            ultimos_clientes = clientes[-5:] 
            
            self.tableWidget.setRowCount(len(ultimos_clientes))

            for i, (nome, documento, telefone, email) in enumerate(ultimos_clientes):
                item_nome = QtWidgets.QTableWidgetItem(str(nome))
                item_tel = QtWidgets.QTableWidgetItem(str(telefone))

                item_tel.setTextAlignment(QtCore.Qt.AlignCenter)

                self.tableWidget.setItem(i, 0, item_nome)
                self.tableWidget.setItem(i, 1, item_tel)
                
                self.tableWidget.setRowHeight(i, 45)

        except Exception as e:
            print(f"Erro ao carregar resumo do dashboard: {e}")

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class ClienteScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_cliente.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        
        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.txt_busca = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.btn_todos = self.ui.findChild(QtWidgets.QPushButton, "pushButton_7")
        self.btn_ativos = self.ui.findChild(QtWidgets.QPushButton, "pushButton_4")
        self.btn_inativos = self.ui.findChild(QtWidgets.QPushButton, "pushButton_8")
        self.btn_novo = self.ui.findChild(QtWidgets.QPushButton, "pushButton_6")

        if self.btn_novo:
            self.btn_novo.clicked.connect (lambda: self.controller.show_screen("cadastro_cliente"))
            self.btn_novo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))            

        if self.tableWidget:
            self.configurar_tabela()
            self.tableWidget.cellDoubleClicked.connect(self.alterar_status_interface)
            self.carregar_clientes()

        if self.txt_busca:
            self.txt_busca.textChanged.connect(self.filtrar_tabela)
        
        self._configurar_grupo_filtros()
        self._connect_buttons()

    def _configurar_grupo_filtros(self):
        self.grupo_filtro = QButtonGroup(self)
        for btn in [self.btn_todos, self.btn_ativos, self.btn_inativos]:
            if btn:
                btn.setCheckable(True)
                self.grupo_filtro.addButton(btn)
                btn.clicked.connect(self.filtrar_tabela)
        if self.btn_todos: self.btn_todos.setChecked(True)

    def carregar_clientes(self):       
        try:
            self.tableWidget.setRowCount(0)
            clientes = ClienteDAO.carregar_clientes()

            for i, dados in enumerate(clientes):
                self.tableWidget.insertRow(i)
                nome, documento, telefone, email = dados[:4]

                status_inicial = "ATIVO"

                item_nome = QtWidgets.QTableWidgetItem(str(nome))
                item_doc = QtWidgets.QTableWidgetItem(str(documento))
                item_contato = QtWidgets.QTableWidgetItem(f"{email}\n{telefone}")
                item_status = QtWidgets.QTableWidgetItem(status_inicial)
                item_servicos = QtWidgets.QTableWidgetItem("0")

                item_status.setForeground(QtGui.QColor("#28a745"))
                
                for item in [item_doc, item_contato, item_status, item_servicos]:
                    item.setTextAlignment(Qt.AlignCenter)

                self.tableWidget.setItem(i, 0, item_nome)
                self.tableWidget.setItem(i, 1, item_doc)
                self.tableWidget.setItem(i, 2, item_contato)
                self.tableWidget.setItem(i, 3, item_status)
                self.tableWidget.setItem(i, 4, item_servicos)
                self.tableWidget.setRowHeight(i, 60)

        except Exception as e:
            print(f"Erro ao carregar: {e}")

    def alterar_status_interface(self, row, column):
        """Altera o status apenas visualmente na tabela"""
        if column != 3: return

        item_status = self.tableWidget.item(row, 3)
        status_atual = item_status.text()
        novo_status = "INATIVO" if status_atual == "ATIVO" else "ATIVO"

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Alterar Status")
        msg.setText(f"Deseja marcar como {novo_status}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            item_status.setText(novo_status)

            cor = "#28a745" if novo_status == "ATIVO" else "#dc3545"
            item_status.setForeground(QtGui.QColor(cor))

            self.filtrar_tabela()

    def filtrar_tabela(self):
        """Lógica de filtro que lê o que está na tela agora"""
        texto = self.txt_busca.text().lower() if self.txt_busca else ""

        btn_selecionado = self.grupo_filtro.checkedButton()
        filtro_status = "TODOS"
        if btn_selecionado == self.btn_ativos: filtro_status = "ATIVO"
        elif btn_selecionado == self.btn_inativos: filtro_status = "INATIVO"

        for row in range(self.tableWidget.rowCount()):
            nome = self.tableWidget.item(row, 0).text().lower()
            doc = self.tableWidget.item(row, 1).text().lower()
            status_atual = self.tableWidget.item(row, 3).text()

            match_texto = texto in nome or texto in doc
            match_status = (filtro_status == "TODOS") or (status_atual == filtro_status)

            self.tableWidget.setRowHidden(row, not (match_texto and match_status))

    def configurar_tabela(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Cliente", "Documento", "Contato", "Status", "Serviços"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def _connect_buttons(self):
        _connect_menu_buttons(self, self.controller)

class ClientesCadScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.ui = uic.loadUi("telas/form_cliente_cad.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.txt_nome = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_1")
        self.txt_cpf = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_2")
        self.txt_tel = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_3")
        self.txt_email = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_4")
        
        self._connect_buttons()

        btn_voltar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_5")
        btn_cancelar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_4")
        
        btn_salvar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_3")

        if btn_voltar:
            btn_voltar.clicked.connect(lambda: self.controller.show_screen("clientes"))
        if btn_cancelar:
            btn_cancelar.clicked.connect(lambda: self.controller.show_screen("clientes"))
        if btn_salvar:
            btn_salvar.clicked.connect(self.cadastrar_cliente)
            btn_salvar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def cadastrar_cliente(self):
        nome = self.txt_nome.text().strip()
        cpf_cnpj = self.txt_cpf.text().strip()
        telefone = self.txt_tel.text().strip()
        email = self.txt_email.text().strip()

        if not (nome and cpf_cnpj and telefone and email):
            QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos obrigatórios.")
            return
            
        try:
            ClienteDAO.cadastrar_cliente(nome, cpf_cnpj, telefone, email)

            QtWidgets.QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso!")

            self.txt_nome.clear()
            self.txt_cpf.clear()
            self.txt_tel.clear()
            self.txt_email.clear()

            self.controller.show_screen("clientes")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar no banco: {str(e)}")

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class FuncScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_funcionarios.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.novo_func = self.ui.findChild(QtWidgets.QPushButton, "pushButton")
        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.txt_busca = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit")

        self.btn_todos = self.ui.findChild(QtWidgets.QPushButton, "pushButton_5")
        self.btn_ativos = self.ui.findChild(QtWidgets.QPushButton, "pushButton_4")
        self.btn_inativos = self.ui.findChild(QtWidgets.QPushButton, "pushButton_6")

        if self.tableWidget:
            self.configurar_tabela()
            self.tableWidget.cellDoubleClicked.connect(self.alterar_status_interface)
            self.carregar_func()

        if self.txt_busca:
            self.txt_busca.textChanged.connect(self.filtrar_tabela)

        self._configurar_grupo_filtros()
        self._connect_buttons()

        if self.novo_func:
            self.novo_func.clicked.connect(lambda: self.controller.show_screen("cadastro_funcionario"))
            self.novo_func.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def _configurar_grupo_filtros(self):
        """Configura os botões de filtro para funcionarem em grupo"""
        self.grupo_filtro = QButtonGroup(self)
        filtros = [self.btn_todos, self.btn_ativos, self.btn_inativos]
        
        for btn in filtros:
            if btn:
                btn.setCheckable(True)
                self.grupo_filtro.addButton(btn)
                btn.clicked.connect(self.filtrar_tabela)
        
        if self.btn_todos:
            self.btn_todos.setChecked(True)

    def configurar_tabela(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Funcionário", "Documento", "Contato", "Status", "Cargo"]
        )
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setShowGrid(False)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # Impede edição 

    def carregar_func(self):
        try:
            func = FuncDAO.carregar_func()
            self.tableWidget.setRowCount(0)

            for i, (nome, documento, cargo, email, telefone) in enumerate(func):
                self.tableWidget.insertRow(i)
                contato = f"{email}\n{telefone}" if email and telefone else (email or telefone or "N/A")

                item_nome = QtWidgets.QTableWidgetItem(str(nome))
                item_doc = QtWidgets.QTableWidgetItem(str(documento))
                item_contato = QtWidgets.QTableWidgetItem(str(contato))
                item_status = QtWidgets.QTableWidgetItem("ATIVO")
                item_cargo = QtWidgets.QTableWidgetItem(str(cargo))

                item_status.setForeground(QtGui.QColor("#28a745"))

                # Alinhamento
                for item in [item_doc, item_contato, item_status, item_cargo]:
                    item.setTextAlignment(Qt.AlignCenter)

                self.tableWidget.setItem(i, 0, item_nome)
                self.tableWidget.setItem(i, 1, item_doc)
                self.tableWidget.setItem(i, 2, item_contato)
                self.tableWidget.setItem(i, 3, item_status)
                self.tableWidget.setItem(i, 4, item_cargo)
                self.tableWidget.setRowHeight(i, 60)
                
        except Exception as e:
            print(f"Erro ao carregar funcionários: {e}")
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar funcionários: {e}")

    def filtrar_tabela(self):
        """Filtra por nome/doc e pelos botões de status"""
        texto = self.txt_busca.text().lower() if self.txt_busca else ""
        
        btn_check = self.grupo_filtro.checkedButton()
        filtro_status = "TODOS"
        if btn_check == self.btn_ativos: filtro_status = "ATIVO"
        elif btn_check == self.btn_inativos: filtro_status = "INATIVO"

        for row in range(self.tableWidget.rowCount()):
            nome = self.tableWidget.item(row, 0).text().lower()
            doc = self.tableWidget.item(row, 1).text().lower()
            status_celula = self.tableWidget.item(row, 3).text().upper()

            match_busca = texto in nome or texto in doc
            match_status = (filtro_status == "TODOS") or (status_celula == filtro_status)

            self.tableWidget.setRowHidden(row, not (match_busca and match_status))

    def alterar_status_interface(self, row, column):
        """Muda o status entre Ativo/Inativo ao clicar duas vezes na coluna 3"""
        if column != 3: return

        item_status = self.tableWidget.item(row, 3)
        status_atual = item_status.text()
        novo_status = "INATIVO" if status_atual == "ATIVO" else "ATIVO"

        confirmar = QMessageBox.question(
            self, "Alterar Status", 
            f"Deseja alterar o status para {novo_status}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            item_status.setText(novo_status)
            cor = "#28a745" if novo_status == "ATIVO" else "#dc3545"
            item_status.setForeground(QtGui.QColor(cor))
            self.filtrar_tabela()

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class FuncCadScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.ui = uic.loadUi("telas/form_funcionarios_cad.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.txt_nome = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_1")
        self.txt_cpf = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_2")
        self.txt_cargo = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_3")
        self.txt_telefone = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_4")
        self.txt_email = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_5")
        
        self._connect_buttons()

        btn_voltar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_2")
        btn_cancelar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_4")
        
        btn_salvar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_3")

        if btn_voltar:
            btn_voltar.clicked.connect(lambda: self.controller.show_screen("funcionarios"))
        if btn_cancelar:
            btn_cancelar.clicked.connect(lambda: self.controller.show_screen("funcionarios"))
        if btn_salvar:
            btn_salvar.clicked.connect(self.cadastrar_func)
            btn_salvar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def cadastrar_func(self):
        nome = self.txt_nome.text().strip()
        cpf_cnpj = self.txt_cpf.text().strip()
        cargo = self.txt_cargo.text().strip()
        telefone = self.txt_telefone.text().strip()
        email = self.txt_email.text().strip()

        if not (nome and cpf_cnpj and cargo and telefone and email):
            QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos obrigatórios.")
            return
            
        try:
            FuncDAO.cadastrar_func(nome, cpf_cnpj, telefone, cargo, email)

            QtWidgets.QMessageBox.information(self, "Sucesso", "Funcionário cadastrado com sucesso!")

            self.txt_nome.clear()
            self.txt_cpf.clear()
            self.txt_telefone.clear()
            self.txt_cargo.clear()
            self.txt_email.clear()

            self.controller.show_screen("funcionarios")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar no banco: {str(e)}")

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class DocScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_documentos.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.base_path = r"G:\Meu Drive\Sistema_Arquivos"
        self.pastas = {
            "Clientes": os.path.join(self.base_path, "Clientes"),
            "Funcionários": os.path.join(self.base_path, "Funcionários"),
            "Fiscais": os.path.join(self.base_path, "Fiscais")
        }
        
        for p in self.pastas.values():
            os.makedirs(p, exist_ok=True)

        self.filtro_atual = "Clientes"

        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.btn_anexar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_7")

        self.txt_busca = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit")

        self.btn_filtro_cli = self.ui.findChild(QtWidgets.QPushButton, "pushButton")
        self.btn_filtro_fun = self.ui.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.btn_filtro_fis = self.ui.findChild(QtWidgets.QPushButton, "pushButton_8")

        self.icon_provider = QFileIconProvider()

        self._configurar_filtros_interface()
        self._connect_buttons()

        if self.txt_busca:
            self.txt_busca.textChanged.connect(self.filtrar_tabela)

        if self.btn_anexar:
            self.btn_anexar.clicked.connect(self.escolher_origem_e_anexar)

        if self.tableWidget:
            self.configurar_tabela()
            self.listar_arquivos()

    def _configurar_filtros_interface(self):
        """Transforma os botões superiores em abas selecionáveis"""
        self.grupo_filtros = QButtonGroup(self)
        filtros = [
            (self.btn_filtro_cli, "Clientes"),
            (self.btn_filtro_fun, "Funcionários"),
            (self.btn_filtro_fis, "Fiscais")
        ]
        
        for btn, tipo in filtros:
            if btn:
                btn.setCheckable(True)
                self.grupo_filtros.addButton(btn)
                btn.clicked.connect(lambda ch, t=tipo: self.mudar_aba_filtro(t))
        
        if self.btn_filtro_cli:
            self.btn_filtro_cli.setChecked(True)

    def mudar_aba_filtro(self, tipo):
        self.filtro_atual = tipo
        if self.txt_busca:
            self.txt_busca.clear()
        self.listar_arquivos()

    def filtrar_tabela(self):
        """Filtra as linhas da tabela em tempo real"""
        texto = self.txt_busca.text().lower()
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 0)
            if item:
                self.tableWidget.setRowHidden(row, texto not in item.text().lower())

    def configurar_tabela(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Arquivo", "Modificado em", "Origem", "", ""])
        
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        
        self.tableWidget.setColumnWidth(3, 70)
        self.tableWidget.setColumnWidth(4, 70)
        
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.verticalHeader().setVisible(False)

    def listar_arquivos(self):
        self.tableWidget.setRowCount(0)
        caminho_pasta = self.pastas[self.filtro_atual]
        
        if not os.path.exists(caminho_pasta): return

        try:
            arquivos = os.listdir(caminho_pasta)
            for nome in arquivos:
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                
                caminho_full = os.path.join(caminho_pasta, nome)
                info = QFileInfo(caminho_full)

                item_nome = QtWidgets.QTableWidgetItem(nome)
                item_nome.setIcon(self.icon_provider.icon(info))
                self.tableWidget.setItem(row, 0, item_nome)
                
                stats = os.stat(caminho_full)
                data_str = QDateTime.fromSecsSinceEpoch(int(stats.st_mtime)).toString("dd/MM/yyyy")
                item_data = QtWidgets.QTableWidgetItem(data_str)
                item_data.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 1, item_data)
                
                item_origem = QtWidgets.QTableWidgetItem(self.filtro_atual)
                item_origem.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, 2, item_origem)

                btn_abrir = QtWidgets.QPushButton("Abrir")
                btn_abrir.setFixedSize(55, 24)
                btn_abrir.setStyleSheet("font-size: 12px; background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 3px;")
                btn_abrir.clicked.connect(lambda ch, p=caminho_full: os.startfile(p))
                
                btn_excluir = QtWidgets.QPushButton("Excluir")
                btn_excluir.setFixedSize(55, 24)
                btn_excluir.setStyleSheet("font-size: 12px; color: #d9534f; background-color: transparent;")
                btn_excluir.clicked.connect(lambda ch, p=caminho_full: self.deletar_arquivo(p))

                self.tableWidget.setCellWidget(row, 3, self._criar_container_centralizado(btn_abrir))
                self.tableWidget.setCellWidget(row, 4, self._criar_container_centralizado(btn_excluir))
                self.tableWidget.setRowHeight(row, 38)

        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")

    def _criar_container_centralizado(self, widget):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        return container

    def escolher_origem_e_anexar(self):
        opcoes = ["Clientes", "Funcionários", "Fiscais"]
        origem, ok = QInputDialog.getItem(self, "Nova Anexação", "Escolha o destino do documento:", opcoes, 0, False)

        if ok and origem:
            files, _ = QFileDialog.getOpenFileNames(self, f"Selecionar Arquivos para {origem}")
            if files:
                try:
                    for f in files:
                        nome = os.path.basename(f)
                        destino = os.path.join(self.pastas[origem], nome)
                        shutil.copy2(f, destino)
                    
                    self.sincronizar_aba_e_listar(origem)
                    QMessageBox.information(self, "Sucesso", f"Arquivos salvos em {origem}!")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Falha no upload: {e}")

    def sincronizar_aba_e_listar(self, origem):
        mapeamento = {
            "Clientes": self.btn_filtro_cli,
            "Funcionários": self.btn_filtro_fun,
            "Fiscais": self.btn_filtro_fis
        }
        btn = mapeamento.get(origem)
        if btn:
            btn.setChecked(True)
            self.mudar_aba_filtro(origem)

    def deletar_arquivo(self, caminho):
        confirmar = QMessageBox.question(self, "Confirmar", f"Excluir definitivamente?\n{os.path.basename(caminho)}", QMessageBox.Yes | QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            os.remove(caminho)
            self.listar_arquivos()

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class AgendaScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_agenda.ui")
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.calendar_grande = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget_2")
        self.calendar_pequeno = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget")
        self.label_mes_ano = self.ui.findChild(QtWidgets.QLabel, "label_2")
        self.btn_hoje = self.ui.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.btn_agendar = self.ui.findChild(QtWidgets.QPushButton, "pushButton")

        self._connect_buttons()

        if self.btn_agendar:
            self.btn_agendar.clicked.connect(lambda: self.controller.show_screen("agendamentos"))
            self.btn_agendar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        if self.btn_hoje:
            self.btn_hoje.clicked.connect(self.ir_para_hoje)

        if self.calendar_grande and self.calendar_pequeno:
            self.calendar_grande.currentPageChanged.connect(self.atualizar_label_data)
            self.calendar_pequeno.selectionChanged.connect(self.sincronizar_para_grande)
            self.calendar_grande.selectionChanged.connect(self.sincronizar_para_pequeno)

            self.atualizar_label_data(self.calendar_grande.yearShown(), self.calendar_grande.monthShown())

    def showEvent(self, event):
        """Disparado sempre que a tela fica visível. Atualiza as cores do calendário."""
        self.atualizar_marcacoes_calendario()
        super().showEvent(event)

    def atualizar_marcacoes_calendario(self):
        """Busca agendamentos no banco e pinta o calendário conforme o tipo de serviço."""
        if not self.calendar_grande:
            return

        try:
            agendamentos = AgendamentoDAO.listar_agendamentos_calendario()
            
            self.calendar_grande.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

            for data_db, id_tipo in agendamentos:
                data_qdate = QtCore.QDate(data_db.year, data_db.month, data_db.day)
                
                fmt = QtGui.QTextCharFormat()
                fmt.setForeground(QtGui.QColor("white"))
                
                if id_tipo == 1: fmt.setBackground(QtGui.QColor("#E57373"))
                elif id_tipo == 2: fmt.setBackground(QtGui.QColor("#64B5F6"))
                elif id_tipo == 3: fmt.setBackground(QtGui.QColor("#81C784"))
                elif id_tipo == 4: fmt.setBackground(QtGui.QColor("#FFB74D"))
                
                self.calendar_grande.setDateTextFormat(data_qdate, fmt)
                
        except Exception as e:
            print(f"Erro ao atualizar visual do calendário: {e}")

    def ir_para_hoje(self):
        hoje = QDate.currentDate()
        self.calendar_grande.setSelectedDate(hoje)
        self.calendar_grande.setCurrentPage(hoje.year(), hoje.month())

    def atualizar_label_data(self, ano, mes):
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        texto = f"{meses[mes]} {ano}"
        if self.label_mes_ano:
            self.label_mes_ano.setText(texto)

    def sincronizar_para_grande(self):
        self.calendar_grande.blockSignals(True)
        data = self.calendar_pequeno.selectedDate()
        self.calendar_grande.setSelectedDate(data)
        self.calendar_grande.blockSignals(False)

    def sincronizar_para_pequeno(self):
        self.calendar_pequeno.blockSignals(True)
        data = self.calendar_grande.selectedDate()
        self.calendar_pequeno.setSelectedDate(data)
        self.calendar_pequeno.blockSignals(False)

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class AgendamentosScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_agenda_ev.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.calendar_grande = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget_2")
        self.calendar_pequeno = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget")
        self.label_mes_ano = self.ui.findChild(QtWidgets.QLabel, "label_2")
        self.btn_hoje = self.ui.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.btn_agendar = self.ui.findChild(QtWidgets.QPushButton, "pushButton")

        self.combo_cli = self.ui.findChild(QtWidgets.QComboBox, "comboBox_2")
        self.combo_fun = self.ui.findChild(QtWidgets.QComboBox, "comboBox")
        self.calendar = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget")
        self.cancelar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_4")
        
        self.mapa_tipos = {
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton"): 1,   # Ensaios
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton_2"): 2, # Esquete
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton_3"): 3, # Talk-Show
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton_4"): 4  # Interação
        }

        if self.cancelar:
            self.cancelar.clicked.connect(lambda: self.controller.show_screen("agenda"))
            self.cancelar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            
        self.btn_salvar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_3")
        if self.btn_salvar:
            self.btn_salvar.clicked.connect(self.finalizar_agendamento)

        self._connect_buttons()
        
    def showEvent(self, event):
        """Atualização Automática: Recarrega combos sempre que a aba é aberta."""
        try:
            clientes, funcs = AgendamentoDAO.carregar_combos_interface()
            
            self.combo_cli.clear()
            for id_c, nome in clientes:
                self.combo_cli.addItem(nome, id_c)

            self.combo_fun.clear()
            for id_f, nome in funcs:
                self.combo_fun.addItem(nome, id_f)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
        super().showEvent(event)

    def finalizar_agendamento(self):
        id_servico = 1
        for radio, id_val in self.mapa_tipos.items():
            if radio and radio.isChecked():
                id_servico = id_val
                break

        data_selecionada = self.calendar.selectedDate().toString("yyyy-MM-dd")
        data_formatada = f"{data_selecionada} 00:00:00"

        id_c = self.combo_cli.currentData()
        id_f = self.combo_fun.currentData()

        if not id_c or not id_f:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um Cliente e um Participante.")
            return

        try:
            AgendamentoDAO.salvar_evento_completo(data_formatada, id_c, id_f, id_servico)
            
            QtWidgets.QMessageBox.information(self, "Sucesso", "Agendamento realizado com sucesso!")
            self.controller.show_screen("agenda")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro de Banco", f"Falha ao salvar: {str(e)}")

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class OrcamentoScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_financeiro_cad.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        

        # Mapeamento de Widgets
        self.btn_ir_financeiro = self.ui.findChild(QtWidgets.QPushButton, "btn_financeiro_bk")

        if self.btn_ir_financeiro:
            self.btn_ir_financeiro.clicked.connect(
        lambda: self.controller.show_screen("financeiro")
    )
        self.input_item = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_1")
        self.input_valor = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_3")
        self.input_cliente = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_cliente")
        self.btn_adicionar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_7")
        self.btn_salvar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_3")
        self.list_resumo = self.ui.findChild(QtWidgets.QListWidget, "listWidget")
        self.lbl_total = self.ui.findChild(QtWidgets.QLabel, "label_6")

        self.itens_temporarios = []
        self.total_acumulado = 0.0

        # Conexões
        if self.btn_adicionar:
            self.btn_adicionar.clicked.connect(self.adicionar_item_lista)
        if self.btn_salvar:
            self.btn_salvar.clicked.connect(self.salvar_e_enviar_financeiro)

        self._connect_buttons()

    def adicionar_item_lista(self):
        desc = self.input_item.text().strip()
        valor_str = self.input_valor.text().replace(',', '.')

        try:
            valor = float(valor_str)
            self.itens_temporarios.append((desc, valor))
            
            # Adiciona ao QListWidget
            item_texto = f"{desc} - R$ {valor:.2f}"
            self.list_resumo.addItem(item_texto)

            # Atualiza Total
            self.total_acumulado += valor
            self.lbl_total.setText(f"R$ {self.total_acumulado:.2f}")

            # Limpa campos
            self.input_item.clear()
            self.input_valor.clear()
            self.input_item.setFocus()
        except ValueError:
            QMessageBox.warning(self, "Erro", "Insira um valor numérico válido.")

    def salvar_e_enviar_financeiro(self):
        cliente = self.input_cliente.text().strip()
        if not cliente or not self.itens_temporarios:
            QMessageBox.warning(self, "Erro", "Preencha o cliente e adicione itens.")
            return

        # 1. Aqui você chamaria o seu DAO para salvar no banco
        # Ex: OrcamentoDAO.salvar(cliente, self.total_acumulado, self.itens_temporarios)
        
        # 2. Notifica a tela de financeiro para atualizar
        financeiro = self.controller.get_screen("financeiro")
        if financeiro:
            financeiro.adicionar_linha_manual(cliente, self.total_acumulado, self.itens_temporarios.copy())

        QMessageBox.information(self, "Sucesso", "Orçamento salvo e enviado ao financeiro!")
        self.limpar_tela()

    def limpar_tela(self):
        self.list_resumo.clear()
        self.itens_temporarios = []
        self.total_acumulado = 0.0
        self.lbl_total.setText("R$ 0.00")
        self.input_cliente.clear()
    
    def _connect_buttons(self):
        _connect_menu_buttons(self, self.controller)


class FinanceiroScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/form_financeiro.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        
        self.btn_abrir_orcamento = self.ui.findChild(QtWidgets.QPushButton, "btn_abrir_orcamento")

        if self.btn_abrir_orcamento:
            self.btn_abrir_orcamento.clicked.connect(
        lambda: self.controller.show_screen("orcamento")
        )

        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.configurar_tabela()
        self._connect_buttons()

    def configurar_tabela(self):
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Data", "Cliente", "Total", "Ações"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def adicionar_linha_manual(self, cliente, total, itens):
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)
        
        data_atual = datetime.date.today().strftime("%d/%m/%Y")
        
        self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(data_atual))
        self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(cliente))
        self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R$ {total:.2f}"))

        btn_pdf = QtWidgets.QPushButton("Gerar PDF")
        btn_pdf.setStyleSheet("background-color: #28a745; color: white; border-radius: 5px;")
        btn_pdf.clicked.connect(lambda: self.gerar_pdf_orcamento(cliente, total, itens))
        
        self.tableWidget.setCellWidget(row, 3, btn_pdf)

    def gerar_pdf_orcamento(self, cliente, total, itens):
        nome_arquivo = f"Orcamento_{cliente}_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        doc = SimpleDocTemplate(nome_arquivo, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título e Cabeçalho
        elements.append(Paragraph(f"<b>ORÇAMENTO - {cliente}</b>", styles['Title']))
        elements.append(Paragraph(f"Data: {datetime.date.today().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        # Tabela de Itens
        dados_tabela = [["Descrição", "Valor (R$)"]]
        for desc, valor in itens:
            dados_tabela.append([desc, f"{valor:.2f}"])
        dados_tabela.append(["TOTAL", f"{total:.2f}"])

        t = Table(dados_tabela, colWidths=[300, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
        ]))
        
        elements.append(t)
        
        try:
            doc.build(elements)
            QMessageBox.information(self, "PDF", f"PDF gerado com sucesso: {nome_arquivo}")
            os.startfile(nome_arquivo)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {e}")

    def _connect_buttons(self):
        _connect_menu_buttons(self, self.controller)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.indices_telas = {}

        self.adicionar_tela("dashboard", DashScreen(self))
        self.adicionar_tela("clientes", ClienteScreen(self))
        self.adicionar_tela("funcionarios", FuncScreen(self))
        self.adicionar_tela("documentos", DocScreen(self))
        self.adicionar_tela("agenda", AgendaScreen(self))
        self.adicionar_tela("agendamentos", AgendamentosScreen(self))
        self.adicionar_tela("cadastro_cliente", ClientesCadScreen(self))
        self.adicionar_tela("cadastro_funcionario", FuncCadScreen(self))
        self.adicionar_tela("orcamento", OrcamentoScreen(self))
        self.adicionar_tela("financeiro", FinanceiroScreen(self))

        self.show_screen("dashboard")

    def adicionar_tela(self, nome, widget):
        indice = self.stack.addWidget(widget)
        self.indices_telas[nome] = indice

    def show_screen(self, nome):
        nome = nome.strip().lower()  # 👈 resolve 90% dos bugs
        if nome in self.indices_telas:
            indice = self.indices_telas[nome]
            self.stack.setCurrentIndex(indice)
            print(f"Mudando para a tela: {nome}")
        else:
            print(f"❌ Tela '{nome}' não encontrada.")

# ======================== TESTE DE TELAS ========================= 
try:    
    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())
except Exception as e:
    print(f"Erro detalhado: {e}")