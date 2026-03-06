# ============================== IMPORTS ==========================
from database_manager import ClienteDAO, FuncDAO, AgendamentoDAO
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
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_dashboard.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # 1. Mapear a Tabela
        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")

        # 2. Conectar botões (Menu e Dashboard)
        self._connect_buttons()

        # 3. Configurar e Carregar
        if self.tableWidget:
            self.configurar_tabela_resumo()
            self.carregar_dados_recentes() # <-- ESSA FUNÇÃO BUSCA OS DADOS

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
            # Usando o DAO que você já tem para buscar os clientes
            clientes = ClienteDAO.carregar_clientes() 
            
            # Vamos exibir apenas os 5 últimos, por exemplo
            ultimos_clientes = clientes[-5:] 
            
            self.tableWidget.setRowCount(len(ultimos_clientes))

            for i, (nome, documento, telefone, email) in enumerate(ultimos_clientes):
                # Criar itens da tabela
                item_nome = QtWidgets.QTableWidgetItem(str(nome))
                item_tel = QtWidgets.QTableWidgetItem(str(telefone))

                # Alinhamento
                item_tel.setTextAlignment(QtCore.Qt.AlignCenter)

                # Inserir na tabela
                self.tableWidget.setItem(i, 0, item_nome)
                self.tableWidget.setItem(i, 1, item_tel)
                
                # Ajustar altura da linha para ficar elegante
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

        self.novo_func = self.ui.findChild(QtWidgets.QPushButton, "pushButton")
        self.tableWidget = self.ui.findChild(QtWidgets.QTableWidget, "tableWidget")
        
        self._connect_buttons()

        if self.novo_func:
            self.novo_func.clicked.connect(lambda: self.controller.show_screen("cadastro_funcionario"))
            self.novo_func.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        if self.tableWidget:
            self.configurar_tabela()
            self.carregar_func()

    def configurar_tabela(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Cliente", "Documento", "Contato", "Status", "Cargo"]
        )

        header = self.tableWidget.horizontalHeader()

        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Fixed)

        self.tableWidget.setColumnWidth(0, 400) # Nome
        self.tableWidget.setColumnWidth(1, 200) # CPF/CNPJ
        self.tableWidget.setColumnWidth(2, 300) # Contato
        self.tableWidget.setColumnWidth(3, 100) # Status
        self.tableWidget.setColumnWidth(4, 100) # Cargo
        self.tableWidget.setShowGrid(False)

    def carregar_func(self):
        try:
            func = FuncDAO.carregar_func()
            self.tableWidget.setRowCount(len(func))

            for i, (nome, documento, cargo, email, telefone) in enumerate(func):
                contato = f"{email}\n{telefone}" if email and telefone else (email or telefone or "N/A")

                item_nome = QtWidgets.QTableWidgetItem(str(nome))
                item_doc = QtWidgets.QTableWidgetItem(str(documento))
                item_contato = QtWidgets.QTableWidgetItem(str(contato))
                item_status = QtWidgets.QTableWidgetItem("ATIVO")
                item_cargo = QtWidgets.QTableWidgetItem(str(cargo))

                item_doc.setTextAlignment(Qt.AlignCenter)
                item_contato.setTextAlignment(Qt.AlignCenter)
                item_status.setTextAlignment(Qt.AlignCenter)
                item_cargo.setTextAlignment(Qt.AlignCenter)

                self.tableWidget.setItem(i, 0, item_nome)
                self.tableWidget.setItem(i, 1, item_doc)
                self.tableWidget.setItem(i, 2, item_contato)
                self.tableWidget.setItem(i, 3, item_status)
                self.tableWidget.setItem(i, 4, item_cargo)

                self.tableWidget.setRowHeight(i, 60)
                
        except Exception as e:
            print(f"Erro detalhado: {e}")
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar funcionários: {e}")

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

        # Mapeamento dos Widgets
        self.calendar_grande = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget_2")
        self.calendar_pequeno = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget")
        self.label_mes_ano = self.ui.findChild(QtWidgets.QLabel, "label_2")
        self.btn_hoje = self.ui.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.btn_agendar = self.ui.findChild(QtWidgets.QPushButton, "pushButton")

        self._connect_buttons()

        # Configurações de Botões
        if self.btn_agendar:
            self.btn_agendar.clicked.connect(lambda: self.controller.show_screen("agendamentos"))
            self.btn_agendar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        if self.btn_hoje:
            self.btn_hoje.clicked.connect(self.ir_para_hoje)

        # Sincronização e Sinais
        if self.calendar_grande and self.calendar_pequeno:
            self.calendar_grande.currentPageChanged.connect(self.atualizar_label_data)
            self.calendar_pequeno.selectionChanged.connect(self.sincronizar_para_grande)
            self.calendar_grande.selectionChanged.connect(self.sincronizar_para_pequeno)

            # Inicializa o label de data
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
            # Chama o DAO para listar datas e tipos (sem abrir banco na Screen)
            agendamentos = AgendamentoDAO.listar_agendamentos_calendario()
            
            # Limpa formatações anteriores para evitar "rastros" de cores
            self.calendar_grande.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

            for data_db, id_tipo in agendamentos:
                # Converte datetime do banco para QDate
                data_qdate = QtCore.QDate(data_db.year, data_db.month, data_db.day)
                
                # Define o estilo visual (Cores baseadas na sua legenda)
                fmt = QtGui.QTextCharFormat()
                fmt.setForeground(QtGui.QColor("white")) # Texto branco para melhor contraste
                
                if id_tipo == 1: fmt.setBackground(QtGui.QColor("#E57373"))   # Ensaios (Vermelho)
                elif id_tipo == 2: fmt.setBackground(QtGui.QColor("#64B5F6")) # Esquete (Azul)
                elif id_tipo == 3: fmt.setBackground(QtGui.QColor("#81C784")) # Talk-Show (Verde)
                elif id_tipo == 4: fmt.setBackground(QtGui.QColor("#FFB74D")) # Interação (Amarelo/Laranja)
                
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

        # Mapeamento de Widgets UI
        self.combo_cli = self.ui.findChild(QtWidgets.QComboBox, "comboBox_2")
        self.combo_fun = self.ui.findChild(QtWidgets.QComboBox, "comboBox")
        self.calendar = self.ui.findChild(QtWidgets.QCalendarWidget, "calendarWidget")
        
        # Mapeamento de Radios para capturar o ID_tipo_servico do diagrama
        self.mapa_tipos = {
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton"): 1,   # Ensaios
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton_2"): 2, # Esquete
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton_3"): 3, # Talk-Show
            self.ui.findChild(QtWidgets.QRadioButton, "radioButton_4"): 4  # Interação
        }

        self.btn_salvar = self.ui.findChild(QtWidgets.QPushButton, "pushButton_3")
        if self.btn_salvar:
            self.btn_salvar.clicked.connect(self.finalizar_agendamento)

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
        # 1. Captura o ID do serviço baseado no RadioButton
        id_servico = 1
        for radio, id_val in self.mapa_tipos.items():
            if radio and radio.isChecked():
                id_servico = id_val
                break

        # 2. Correção Erro 1292: Formatação correta da data para o MySQL
        # O banco espera 'YYYY-MM-DD HH:MM:SS'
        data_selecionada = self.calendar.selectedDate().toString("yyyy-MM-dd")
        data_formatada = f"{data_selecionada} 00:00:00"

        # 3. Captura IDs de chaves estrangeiras
        id_c = self.combo_cli.currentData()
        id_f = self.combo_fun.currentData()

        if not id_c or not id_f:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um Cliente e um Participante.")
            return

        try:
            # Chama o DAO para salvar
            AgendamentoDAO.salvar_evento_completo(data_formatada, id_c, id_f, id_servico)
            
            QtWidgets.QMessageBox.information(self, "Sucesso", "Agendamento realizado com sucesso!")
            self.controller.show_screen("agenda")
        except Exception as e:
            # Tratamento visual de erros técnicos para o usuário
            QtWidgets.QMessageBox.critical(self, "Erro de Banco", f"Falha ao salvar: {str(e)}")

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
        self.adicionar_tela("cadastro_funcionario", FuncCadScreen(self))

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

            if nome == "funcionarios" and hasattr(widget_atual, "carregar_func"):
                widget_atual.carregar_func()
            print(f"Mudando para a tela: {nome}")
        else:
            print(f"Erro: Tela '{nome}' não encontrada no mapeamento.")

# ======================== TESTE DE TELAS ========================= 
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
sys.exit(app.exec_())