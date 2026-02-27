# Módulo de Database
# Responsável pela conexão e operações com banco de dados
import mysql.connector
        
conexao = mysql.connector.connect(
    host='Localhost',
    user='root',
    password='0709',
    database='db_cenicosecinicos',
)
cursor = conexao.cursor()

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


# cursor.close()
# conexao.close()