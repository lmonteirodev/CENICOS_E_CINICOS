import mysql.connector
from PyQt5 import uic, QtWidgets
from reportlab.pdfgen import canvas
import sys
import os

conexao = mysql.connector.connect(
    host='Localhost',
    user='root',
    password='0709',
    database='db_cenicosecinicos',
)
cursor = conexao.cursor()

def get_connection():
    """Abre uma conexão usando PyMySQL."""
    try:
        conn = mysql.connector.connect(**conexao)
        return conn
    except Exception as e:
        print(f"[ERRO CONEXÃO] {e}")
        return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Carrega UIs da pasta 'telas'
    clientes = uic.loadUi(os.path.join("abas", "aba_clientes.ui"))
    # telaListar = uic.loadUi(os.path.join("telas", "listar_dados.ui"))
    # tela_editar = uic.loadUi(os.path.join("telas", "menu_editar.ui"))

    # # Conexões de açoes dos botões
    # cadprod.pushButton.clicked.connect(funcao_cadastrar)        # Botão salvar/cadastrar
    # cadprod.pushButton_2.clicked.connect(abrir_tela_listar)     # Botão abrir/listar

    # #Botão gerar PDF na tela de listagem
    # telaListar.pushButton.clicked.connect(gerar_pdf) 
    
    # telaListar.botaoEditar.clicked.connect(editar_dados)        # Editar (abrir editor)
    # telaListar.botaoExcluir.clicked.connect(excluir_dados)      # Excluir
    # tela_editar.pushButton.clicked.connect(salvar_valor_editado)# Salvar alterações
        
    # mostra a janela principal
    clientes.show()
    # inicia o loop de eventos da aplicação
    sys.exit(app.exec())