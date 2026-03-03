import mysql.connector
        

def get_connection():
    try:
        conexao = mysql.connector.connect(
            host="localhost",       # ou IP do servidor
            user="root",
            password="0709",
            database="db_cenicosecinicos"
        )
        return conexao
    except Exception as e:
        print("Erro ao conectar:", e)
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


