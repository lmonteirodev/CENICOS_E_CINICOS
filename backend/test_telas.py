# ============================== IMPORTS ==========================
from database_manager import ClienteDAO, FuncDAO
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QDate
import sys

# ======================== FUNÇÃO MESTRA ==========================
def _connect_menu_buttons(ui, controller):
    """Connect menu buttons from a loaded UI to controller.show_screen.

    This tries several common object names found across the .ui files.
    Prints which connections were made to help debugging.
    """
    mapping = {
        "agenda": ["btn_abrir_agenda_menu", "btn_abrir_agenda", "btn_abrir_agenda_2", "btn_abrir_agenda_3"],
        "clientes": ["btn_abrir_cliente_menu", "btn_abrir_clientes"],
        "funcionarios": ["btn_abrir_funcionario_menu"],
        "documentos": ["btn_abrir_documento_menu", "btn_abrir_documentos"],
        "dashboard": ["btn_abrir_dashboard_menu"],
        "cadastro_cliente": ["btn_abrir_novo_cliente_2","btn_cadastrar_cliente"]
    }

    for screen, names in mapping.items():
        for name in names:
            btn = ui.findChild(QtWidgets.QPushButton, name)
            if btn:
                try:
                    def _on_click(_=None, s=screen, n=name):
                        print(f"UI button clicked: {n} -> requesting '{s}'")
                        controller.show_screen(s)

                    btn.clicked.connect(_on_click)
                    btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                except Exception:
                    # non-fatal; continue trying other buttons
                    pass
                print(f"connected UI button '{name}' -> '{screen}'")

# ======================== CLASSES DE TELAS =========================
class DashScreen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.screen_size = controller
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_dashboard.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        # menu_lateral - conectar botões
        self._connect_buttons()
    
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
        
        self.novo_cliente = self.ui.findChild(QtWidgets.QPushButton, "pushButton")
        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")
        
        self._connect_buttons()

        if self.novo_cliente:
            self.novo_cliente.clicked.connect(lambda: self.controller.show_screen("cadastro_cliente"))
            self.novo_cliente.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        if self.tableWidget:
            self.configurar_tabela()
            self.carregar_clientes()

    def configurar_tabela(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Cliente", "Documento", "Contato", "Status", "Serviços"]
        )

        header = self.tableWidget.horizontalHeader()

        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Fixed)

        self.tableWidget.setColumnWidth(0, 400) # Nome
        self.tableWidget.setColumnWidth(1, 200) # CPF/CNPJ
        self.tableWidget.setColumnWidth(2, 300) # Contato
        self.tableWidget.setColumnWidth(3, 100) # Status
        self.tableWidget.setColumnWidth(4, 100) # Qtd Serviços
        self.tableWidget.setShowGrid(False)

    def carregar_clientes(self):
        try:
            clientes = ClienteDAO.carregar_clientes()
            self.tableWidget.setRowCount(len(clientes))

            for i, (nome, documento, telefone, email) in enumerate(clientes):
                contato = f"{email}\n{telefone}" if email and telefone else (email or telefone or "N/A")

                item_nome = QtWidgets.QTableWidgetItem(str(nome))
                item_doc = QtWidgets.QTableWidgetItem(str(documento))
                item_contato = QtWidgets.QTableWidgetItem(str(contato))
                item_status = QtWidgets.QTableWidgetItem("ATIVO")
                item_servicos = QtWidgets.QTableWidgetItem("0")

                item_doc.setTextAlignment(Qt.AlignCenter)
                item_contato.setTextAlignment(Qt.AlignCenter)
                item_status.setTextAlignment(Qt.AlignCenter)
                item_servicos.setTextAlignment(Qt.AlignCenter)

                self.tableWidget.setItem(i, 0, item_nome)
                self.tableWidget.setItem(i, 1, item_doc)
                self.tableWidget.setItem(i, 2, item_contato)
                self.tableWidget.setItem(i, 3, item_status)
                self.tableWidget.setItem(i, 4, item_servicos)

                self.tableWidget.setRowHeight(i, 60)
                
        except Exception as e:
            print(f"Erro detalhado: {e}")
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes: {e}")

    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

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

        btn_voltar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_2")
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
        # menu_lateral - conectar botões
        self._connect_buttons()
    
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
        # menu_lateral - conectar botões
        self._connect_buttons()
    
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
        # menu_lateral - conectar botões
        self._connect_buttons()
    
    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

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

        self.show_screen("dashboard")

    def adicionar_tela(self, nome, widget):
        indice = self.stack.addWidget(widget)
        self.indices_telas[nome] = indice

    def show_screen(self, nome):
        """Método que os botões do menu chamam via controller"""
        if nome in self.indices_telas:
            indice = self.indices_telas[nome]
            self.stack.setCurrentIndex(indice)

            widget_atual = self.stack.currentWidget()
            if nome == "clientes" and hasattr(widget_atual, "carregar_clientes"):
                widget_atual.carregar_clientes()

            print(f"Mudando para a tela: {nome}")
        else:
            print(f"Erro: Tela '{nome}' não encontrada no mapeamento.")

# ======================== TESTE DE TELAS ========================= 
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
sys.exit(app.exec_())