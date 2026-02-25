# import random as rdm
# import mysql.connector

# class Database:
#     def __init__(self):
#         self.conn = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="1234",
#             database="db_cenicosecinicos"
#         )
#         self.cursor = self.conn.cursor(dictionary=True)

#     def executar(self, query, params=None):
#         self.cursor.execute(query, params or ())
#         self.conn.commit()

#     def buscar(self, query, params=None):
#         self.cursor.execute(query, params or ())
#         return self.cursor.fetchall()

#     def fechar(self):
#         self.cursor.close()
#         self.conn.close()

# class Cliente:
#     def __init__(self):
#         self.ID_cliente = rdm.randint(1, 999999999999)

#     def cadastrar_cliente(self):
#         self.nome = input("Digite o nome do cliente: ")
#         self.endereco = input("Digite o endereço do cliente: ")
#         self.telefone = input("Digite o telefone do cliente: ") 
#         self.email = input("Digite o email do cliente: ")
#         self.tipo_pessoa = input("Digite o tipo de pessoa (Física ou Jurídica): ")

#         self.cpf = None
#         self.cnpj = None

#         if self.tipo_pessoa.lower() == "física":
#             self.tipo_pessoa = "Física"
#             self.cpf = input("Digite o CPF do cliente: ")

#         elif self.tipo_pessoa.lower() == "jurídica":
#             self.tipo_pessoa = "Jurídica"
#             self.cnpj = input("Digite o CNPJ do cliente: ")

#         else:
#             print("Tipo inválido.")
#             return

# # INSERT NO BANCO
#         Database.executar(
#             """INSERT INTO clientes 
#                (ID_cliente, nome, endereco, telefone, email, tipo_pessoa, cpf, cnpj) 
#                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
#             (self.ID_cliente, self.nome, self.endereco, self.telefone,
#              self.email, self.tipo_pessoa, self.cpf, self.cnpj)
#         )

#         print("\n✓ Cliente cadastrado com sucesso!\n")

#         return self.ID_cliente
# #commit no banco de dados
#     def commit(self):
#         Database.conn.commit()

import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0709",
            database="db_cenicosecinicos"
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
        
