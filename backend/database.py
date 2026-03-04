import mysql.connector
        

def get_connection():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0709",
            database="db_cenicosecinicos"
        )
        return conexao
    
    except Exception as e:
        print("Erro ao conectar:", e)
        return None

if __name__ == "__main__":
    conexao = get_connection()
    
    if conexao:
        print("Conexão OK!")
        conexao.close()
    else:
        print("Falha na conexão.")