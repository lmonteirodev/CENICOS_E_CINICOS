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

from database import get_connection

class AgendamentoDAO:
    @staticmethod
    def carregar_combos_interface():
        """Busca dados para os comboboxes sem expor a conexão à interface."""
        conexao = get_connection()
        cursor = conexao.cursor()
        try:
            # Busca Clientes
            cursor.execute("SELECT ID_cliente, nome FROM cliente ORDER BY nome")
            clientes = cursor.fetchall()
            
            # Busca Funcionários
            cursor.execute("SELECT ID_funcionario, nome FROM funcionario ORDER BY nome")
            funcs = cursor.fetchall()
            
            return clientes, funcs
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def salvar_evento_completo(data_formatada, id_cli, id_fun, id_tipo_servico):
        """
        Realiza a transação respeitando as chaves estrangeiras do diagrama técnico.
        """
        conexao = get_connection()
        cursor = conexao.cursor()
        try:
            # 1. Inserção na tabela 'servico' (Obrigatória antes da agenda)
            # Resolve o Erro 1452 garantindo que id_tipo_servico exista
            cursor.execute("""
                INSERT INTO servico (status_servico, data_servico, ID_funcionario, ID_tipo_servico) 
                VALUES (%s, %s, %s, %s)
            """, ("AGENDADO", data_formatada, id_fun, id_tipo_servico))
            
            id_servico_gerado = cursor.lastrowid

            # 2. Inserção na tabela 'agenda'
            # Correção Erro 1054: Removido ID_perfil (não existe nesta tabela no diagrama)
            sql_agenda = """
                INSERT INTO agenda (data_select, horario_inicio, horario_fim, 
                                   ID_servico, ID_funcionario, ID_cliente)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Horários padrão para evitar erro de campo vazio
            cursor.execute(sql_agenda, (data_formatada, "08:00:00", "18:00:00", 
                                        id_servico_gerado, id_fun, id_cli))
            
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            raise e
        finally:
            cursor.close()
            conexao.close()
    
    @staticmethod
    def listar_agendamentos_calendario():
        """Busca todos os eventos para exibir no calendário principal"""
        conexao = get_connection()
        cursor = conexao.cursor()
        try:
            # Seleciona a data e o tipo de serviço (para saber a cor)
            sql = """
                SELECT a.data_select, s.ID_tipo_servico 
                FROM agenda a
                JOIN servico s ON a.ID_servico = s.ID_servico
            """
            cursor.execute(sql)
            return cursor.fetchall() # Retorna algo como [(datetime, 1), (datetime, 2)]
        finally:
            cursor.close()
            conexao.close()