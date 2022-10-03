#campos
#id=autoIncrement, salt=bin, site=txt, nome=txt, senha=bin, descricao=txt
import sqlite3
import os


#cria ou abre o banco de dados, cria a tabela caso não exista
nome_db = f'{os.getcwd()}/sites.db'
def cria_tabela():
    """
    Cria o banco de dados [sites.db] e a tabela [dados] caso não existam\n
    <- bool return - Retorna True em caso de sucesso
    """
    retorno = False
    try:
        conexao = sqliteConnection = sqlite3.connect(nome_db)
        sql = 'create table if not exists dados (id INTEGER PRIMARY KEY AUTOINCREMENT, '
        sql+= 'site TEXT, descricao TXT, nome BLOB NOT NULL, senha BLOB NOT NULL)'
        
        ponteiro = conexao.cursor()
        ponteiro.execute(sql)
        ponteiro.close()
        retorno = True
        print("Banco de dados e tabela criados com sucesso")
    except sqlite3.Error as error:
        print(f'Erro criando a tabela, erro: {error}')
    finally:
        if conexao:
            conexao.close()
    
    return retorno

#adiciona um regostro na tabela
def adiciona_registro(site:str, descricao:str, nome:bytes, senha:bytes):
    """
    Adiciona um registro na tabela\n
    -> str site - Qualquer valor em formato de texto puro\n
    -> str descricao - Qualquer valor em formato de texto puro\n
    -> bin nome - Valor em binário criptografado\n
    -> bin senha -  Valor em binário criptografado\n
    <- bool return - Retorna True em caso de sucesso
    """
    retorno = False
    try:
        conexao = sqliteConnection = sqlite3.connect(nome_db)
        ponteiro = sqliteConnection.cursor()

        sqlite_insert_blob_query = """ INSERT INTO dados
                                (site, descricao, nome, senha) VALUES (?, ?, ?, ?)"""

        data_tuple = (site, descricao, nome, senha)
        ponteiro.execute(sqlite_insert_blob_query, data_tuple)
        conexao.commit()
        ponteiro.close()
        retorno = True
    except sqlite3.Error as error:
        print(f'Erro adicionando registro, erro: {error}')
    finally:
        if conexao:
            conexao.close()
    
    return retorno

#deleta o registro informado
def deleta_registro(id:int):
    """
    Deleta o registro informado\n
    -> int id - umero do registro a ser deletado\n
    <- bool return - Retorna True em caso de sucesso
    """
    retorno = False
    try:
        conexao = sqliteConnection = sqlite3.connect(nome_db)
        ponteiro = sqliteConnection.cursor()
        
        sql_delete_blob_query = """DELETE from dados where id = ?"""
        ponteiro.execute(sql_delete_blob_query, (id,))
        conexao.commit()
        ponteiro.close()
        retorno = True
    except sqlite3.Error as error:
        print(f"Ocorreu um erro ao deletar o registro. Erro:{error}")
    finally:
        if conexao:
            conexao.close()
    
    return retorno

#retorna os registros
def retorna_registro(id:int):
    """
    Retorna os registros que sejam >= ao id informado\n
    -> int id - Numero do id inicial\n
    <- list return - Retorna uma lista contendo uma tuplas de cada registro\n
    ordem: (id, site, descricao, nome, senha)
    """
    retorno = []
    try:
        conexao = sqliteConnection = sqlite3.connect(nome_db)
        ponteiro = sqliteConnection.cursor()
        
        sql_fetch_blob_query = """SELECT * from dados where id >= ? ORDER BY site"""
        ponteiro.execute(sql_fetch_blob_query, (id,))
        record = ponteiro.fetchall()
        for row in record:
            reg = (row[0],row[1],row[2],row[3],row[4])
            retorno.append(reg)

        ponteiro.close()
    except sqlite3.Error as error:
        print(f"Ocorreu um erro ao verificar o registro. Erro:{error}")
    finally:
        if conexao:
            conexao.close()
    
    return retorno        

#for i in range(1, 5):
#    adiciona_registro('youtube', 'teste', b'iuqyiyqi', b'iwyiwyi',b'vvmmjhkjhk')

#teste = retorna_registro(0)
#for i in teste:
#    print (teste)

#for i in range(1, 50):
#    deleta_registro(i)