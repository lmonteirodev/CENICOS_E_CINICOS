# Módulo de Database
# Responsável pela conexão e operações com banco de dados
import mysql.connector


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="Cenicos&CinicosDB"
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def executar(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def buscar(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def fechar(self):
        self.cursor.close()
        self.conn.close()