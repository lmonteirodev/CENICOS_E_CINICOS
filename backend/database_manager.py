from database import get_connection
import re

class ClienteDAO:
    @staticmethod
    def carregar_clientes():
        conexao = get_connection()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT c.nome, c.cpf_cnpj, t.telefone, e.email
            FROM cliente c
            LEFT JOIN telefone_cliente t ON t.ID_cliente = c.ID_cliente
            LEFT JOIN email_cliente e ON e.ID_cliente = c.ID_cliente
        """)
        dados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return dados
    
    @staticmethod
    def cadastrar_cliente (nome, cpf_cnpj, telefone, email):
        def definir_tipo_pessoa (cpf_cnpj: str):
            somente_numeros = re.sub(r'\D', '', cpf_cnpj)

            if len(somente_numeros) == 11:
                return 'F'
            elif len(somente_numeros) == 14:
                return 'J' 
            else:
                raise ValueError("CPF/CNPJ inválido")
                    
        tipo_pessoa = definir_tipo_pessoa(cpf_cnpj)

        conexao = get_connection()
        cursor = conexao.cursor()
        try:
            # 1. Inserir cliente
            cursor.execute("""INSERT INTO cliente (nome, cpf_cnpj, tipo_pessoa) VALUES (%s, %s, %s)""", (nome, cpf_cnpj, tipo_pessoa))

            # 2. Obter o ID do cliente inserido
            ID_cliente = cursor.lastrowid

            # 3. Inserir telefone vinculado ao cliente
            cursor.execute("""INSERT INTO telefone_cliente (telefone, iD_cliente) VALUES (%s, %s)""", (telefone, ID_cliente))

            # 4. Inserir email vinculado ao cliente
            cursor.execute("""INSERT INTO email_cliente (email, id_cliente) VALUES (%s, %s)""", (email, ID_cliente))
            

            # Finalizar
            conexao.commit()
        except Exception as e:
            conexao.rollback()
            raise e
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def buscar_ultimos_clientes(limite=3):
        conexao = get_connection()
        cursor = conexao.cursor()
        # Busca Nome e CPF/CNPJ dos últimos cadastrados
        cursor.execute("""
            SELECT nome, cpf_cnpj FROM cliente ORDER BY ID_cliente DESC LIMIT %s
        """, (limite,))
        dados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return dados
    
class FuncDAO:
    @staticmethod
    def carregar_func():
        conexao = get_connection()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT f.nome, f.cpf_cnpj, f.cargo, f.email, t.telefone
            FROM funcionario f
            LEFT JOIN telefone_funcionario t ON t.ID_funcionario = f.ID_funcionario
        """)
        funcionarios = cursor.fetchall()
        cursor.close()
        conexao.close()
        return funcionarios
    
    @staticmethod
    def cadastrar_func (nome, cpf_cnpj, telefone, cargo, email):
            def definir_tipo_pessoa (cpf_cnpj: str):
                somente_numeros = re.sub(r'\D', '', cpf_cnpj)
                if len(somente_numeros) == 11:
                    return 'F'
                elif len(somente_numeros) == 14:
                    return 'J' 
                else:
                    raise ValueError("CPF/CNPJ inválido")

            tipo_pessoa = definir_tipo_pessoa(cpf_cnpj)

            conexao = get_connection()        
            cursor = conexao.cursor()
            try:
                # Inserir funcionario
                cursor.execute("""INSERT INTO funcionario (nome, cpf_cnpj, tipo_pessoa, cargo, email) VALUES (%s, %s, %s, %s, %s)""", (nome, cpf_cnpj, tipo_pessoa, cargo, email))
                
                # Obter o ID do funcionario inserido
                ID_funcionario = cursor.lastrowid

                # Inserir telefone vinculado ao funcionario
                cursor.execute("""INSERT INTO telefone_funcionario (telefone, iD_funcionario) VALUES (%s, %s)""", (telefone, ID_funcionario))

                conexao.commit()
            except Exception as e:
                conexao.rollback()
                raise e
            finally:
                cursor.close()
                conexao.close()