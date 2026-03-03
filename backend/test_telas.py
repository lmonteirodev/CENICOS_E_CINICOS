from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication


def _connect_menu_buttons(ui, controller):
    """Connect menu buttons from a loaded UI to controller.show_screen.

    This tries several common object names found across the .ui files.
    Prints which connections were made to help debugging.
    """
    mapping = {
        "agenda": ["btn_abrir_agenda_menu", "btn_abrir_agenda", "btn_abrir_agenda_2", "btn_abrir_agenda_3"],
        "clientes": ["btn_abrir_cliente_menu", "btn_abrir_clientes", "btn_abrir_novo_cliente", "btn_abrir_novo_cliente_2"],
        "funcionarios": ["btn_abrir_funcionario_menu"],
        "documentos": ["btn_abrir_documento_menu", "btn_abrir_documentos"],
        "dashboard": ["btn_abrir_dashboard_menu"],
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
import sys

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

class dash_screen(QtWidgets.QWidget):
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
    
class clientes_screen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_clientes.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        # menu_lateral - conectar botões
        self._connect_buttons()
    
    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class func_screen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_funcionarios.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        # menu_lateral - conectar botões
        self._connect_buttons()
    
    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class doc_screen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_documentos.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        # menu_lateral - conectar botões
        self._connect_buttons()
    
    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class agenda_screen(QtWidgets.QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = uic.loadUi("telas/aba_agenda.ui")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        # menu_lateral - conectar botões
        self._connect_buttons()
    
    def _connect_buttons(self):
        _connect_menu_buttons(self.ui, self.controller)

class mainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.screens = {}
        self.screens["dashboard"] = dash_screen(self)
        self.screens["clientes"] = clientes_screen(self)
        self.screens["funcionarios"] = func_screen(self)
        self.screens["documentos"] = doc_screen(self)
        self.screens["agenda"] = agenda_screen(self)

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        self.show_screen("dashboard")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     controller = ScreenController()
#     controller.show_screen(mainwindow)

#     # ClientesCadScreen.pushButton_3.clicked.connect(ClientesCadScreen.cadastrar_cliente)
#     sys.exit(app.exec())
    
app = QtWidgets.QApplication(sys.argv)
window = mainwindow()
window.showFullScreen()   # ou showMaximized()
sys.exit(app.exec_())