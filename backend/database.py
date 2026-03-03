import mysql.connector
        

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
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


# # ------------------------------------------------ CRUD ---------------------------------------------------------
# # ----------------- CREAT
# comando = 'INSERT INTO cliente (nome, cpf, cnpj, tipo_pessoa) VALUES ("Matheus", "01567911293", "null", "F")'
# cursor.execute(comando)
# conexao.commit()

# # # ------------------READ
# comando = 'SELECT * FROM cliente'
# cursor.execute(comando)
# resultado = cursor.fetchall()
# print(resultado)

# # ---------------- UPDATE
# comando = 'UPDATE cliente SET cnpj = 1 WHERE ID_cliente = 1'
# cursor.execute(comando)
# conexao.commit()

# # -------------- DELETE
# comando = 'DELETE FROM cliente WHERE ID_cliente = 3'
# cursor.execute(comando)
# conexao.commit()


