import random
import PySimpleGUI as sg
import dados_db
import base64
import os
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import subprocess

arquivo_salt = f'{os.getcwd()}/salt.bin'
arquivo_token = f'{os.getcwd()}/token.bin'

#gera a key de criptografia
def gerar_chave(senha:str) ->bytes:
    """
    Gera uma chave para encriptar os dados\n
    A chave gerada é completamente dependente da senha master\n
    Se a senha master for perdida, não será possivel decriptar os dados\n
    -> str senha - A senha master\n
    <- bytes return - Retorna a chave de criptografia
    """
    password = senha.encode('utf-8') #converte em binario
    
    #o salt devera ser armazenado caso não exista, somente
    #o mesmo salt com a senha correta é capaz de decriptar os dados
    if os.path.exists(arquivo_salt):
        arq = open(arquivo_salt,'rb')
        salt = arq.read()
        arq.close()
    else:    
        salt = os.urandom(16)
        arq = open(arquivo_salt,'wb')
        arq.write(salt)
        arq.close()

    #gera a key para encriptar/decriptar os dados
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000,)
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)

    #cria um token que será usado para verificar a senha master
    #ao iniciar, isso não é importante, só serve para confirmar a senha
    token = f.encrypt(b"dado que sera encryptado")
    if not os.path.exists(arquivo_token):
        arq=open(arquivo_token,'wb')
        arq.write(token)
        arq.close()
    else:
        arq=open(arquivo_token,'rb')
        token = arq.read()
        arq.close()
    
    return f

#criptografa o texto informado
def criptografa(f:bytes, texto:str) ->bytes:
    """
    Criptografa o texto informado\n
    -> bytes f - Uma referencia a class Fernet\n
    -> str texto - O texto a ser criptografado\n
    <- bytes return - Retorna uma 
    """
    cr = texto.encode('utf-8')
    return f.encrypt(cr)

#decriptografa a lista de bytes informado
def decriptografa(f:bytes, texto:bytes) ->str:
    """
    Decriptografa a lista de bytes informado\n
    -> bytes f - Uma referencia a class Fernet\n
    -> bytes texto - Uma lista de bytes\n
    <- str return - Em caso de sucesso, retorna a string decriptografada
    """
    retorno = ''
    try:
        dc = f.decrypt(texto)
        retorno = dc.decode()
    except:
        retorno = ''

    return retorno

#verifica se a senha master é válida
# tentando decriptar o token
def verifica_senha(f:bin) ->bool:
    """
    Verifica se a senha master é capas de decriptar o token\n
    -> bytes f - Uma referencia a class Fernet\n
    <- bool return - Retorna True em caso de sucesso
    """
    if not os.path.exists(arquivo_token):
        return False

    arq=open(arquivo_token,'rb')
    token = arq.read()
    arq.close()
    
    try:
        f.decrypt(token)
        return True
    except:
        return False

#copia o texto informado para o clipboard
#echo|set /p= Configura o comando [echo] para não adicionar nova linha
def copy2clip(txt:str) ->bool:
    """
    Copia o texto informado para o clipboard\n
    -> str txt - Texto a ser copiado\n
    <- bool return - Retorna True em caso de sucesso
    """
    retorno = False
    cmd='echo|set /p='+txt.strip()+'|clip'
    try:
        subprocess.check_output(cmd, text=True, shell=True)
        retorno = True
    except subprocess.CalledProcessError:
        retorno = False

    return retorno

#gera uma nova senha
def gera_senha() ->str:
    """
    Gera uma string com 15 caracteres aleatorios\n
    -> None - Essa função não recebe parametros\n
    <- str return - Retorna uma string com 15 caracteres
    """
    caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXZabcdefghijklmnopqrstuvwxz0123456789@#$&'
    ps = random.choices(caracteres, k=15)
    senha_gerada = ''.join(ps)
    return senha_gerada


#-----------------------entrada do script-----------------------------------
txtsenha = sg.popup_get_text('Enter password', password_char='*')
if None == txtsenha or len(txtsenha) == 0:
    exit()

if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=*_\-\.]{8,}', txtsenha):
    msg = """A senha informada não atende os requisitos\n
    A senha deve conter pelo menos 8 caracteres.\n
    Os caracteres podem ser letras, numeros e simbolos @#$%^&+=*_-.
    """
    sg.popup(msg)
    exit()

#gera a chave e testa a senha
key_gerada = gerar_chave(txtsenha)
if not verifica_senha(key_gerada):
    sg.popup('A senha informada não é válida')
    exit()

#cria o banco de dados e tabela caso nao exista
if not dados_db.cria_tabela():
    sg.popup(f'Ocorreu um erro ao tentar criar o banco de dados e a tabela.')
    exit()

#coleta os dados do banco de dados para montar a tabela
dados = dados_db.retorna_registro(0)

#importante!!!, com essa opção a tabela retorna a informação
#somente da linha que foi selecionada
#select_mode=sg.TABLE_SELECT_MODE_BROWSE
cabecalho = ['Id','Site','Descrição']  #,'Nome','Senha']
sg.set_options(element_padding=(2, 2))

l_col = [[sg.Text('Usuario:')],[sg.Input(size=(25, 1),key='-USUARIO-'), sg.Button('Copiar', key='-CPUSUARIO-')],]
r_col = [[sg.Text('Senha:')],[sg.Input(size=(25, 1),key='-SENHA-'), sg.Button('Copiar', key='-CPSENHA-')],]

layout = [
            [sg.Text('ID: '),sg.Input(size=(10, 1),default_text='0',disabled=True,key='-ID-')],
            [sg.Text('Site:')],[sg.Input(size=(100, 1),key='-SITE-')],
            [sg.Text('Descrição:')],[sg.Input(size=(100, 1),key='-DESCRICAO-')],
            [sg.Column(l_col, element_justification='left', pad=(0, 10), key='LCOL'), sg.Column(r_col, element_justification='left', pad=(20, 10),key='RCOL')],
            [sg.Text('Lista das contas salvas')],
            [sg.Table(values=dados,
                        headings=cabecalho,
                        max_col_width=25,
                        auto_size_columns=True,
                        expand_x=True,
                        justification='left',
                        row_height=20,
                        enable_events = True,
                        key='-TABELA-',
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                        alternating_row_color='blue',
                        num_rows=min(len(dados), 20))],
            [sg.VSeparator()],
            [sg.Button('Salvar', key='-ADICIONAR-'),sg.Button('Deletar',key='-DELETAR-'),sg.Button('Gerar Senha', key='-GRSENHA-'), sg.Button('Fechar', key='-SAIR-')]
        ]        

window = sg.Window('Gerador e Armazenador de senha', layout, size=(680, 800) , resizable=True, font='Arial 12',finalize=True)


selecionada = None
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == '-SAIR-':
        break
    
    elif event == "-TABELA-":
        selecionada = values['-TABELA-'][0]
        linha = dados[selecionada]
        window['-ID-'](linha[0])
        window['-SITE-'](linha[1])
        window['-DESCRICAO-'](linha[2])
        window['-USUARIO-'](decriptografa(key_gerada, linha[3]))
        window['-SENHA-'](decriptografa(key_gerada, linha[4]))
    
    elif event == '-DELETAR-':
        id_str = values['-ID-']
        try:
            id_num = int(id_str)
        except:
            sg.popup('O campo [ID], não contém um valor válido.')
            continue
        
        questao = sg.popup_yes_no('Essa ação não tem retorno.\nDeseja deletar esse registro ?')
        if questao == 'No':
            continue

        resultado=dados_db.deleta_registro(id_num)
        if resultado:
            dados.pop(selecionada)
            window['-TABELA-'].update(values=dados)
            window['-ID-']('0')
            window['-SITE-']('')
            window['-USUARIO-']('')
            window['-SENHA-']('')
            window['-DESCRICAO-']('')
            window.refresh()
            sg.popup(f'Registro: [{id_num}], deletado com sucesso.')
        else:
            sg.popup(f'Não foi possivel deletar o Registro: [{id_num}]')

    elif event == '-ADICIONAR-':
        site = window['-SITE-'].get()
        if len(site.strip()) < 1:
            sg.popup('O campo site não pode estar vazio')
            continue

        usuario = window['-USUARIO-'].get()
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=*_\-\.]{6,}', usuario):
            sg.popup('O campo usuario contém caracteres inválidos')
            continue

        senha = window['-SENHA-'].get()
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=*_\-\.]{8,}', senha):
            sg.popup('A senha informada não é válida para o cadastro')
            continue

        descricao = window['-DESCRICAO-'].get()
        
        user = criptografa(key_gerada, usuario)
        passw = criptografa(key_gerada, senha)
        if dados_db.adiciona_registro(site, descricao,user, passw):
            dados = dados_db.retorna_registro(0)
            window['-TABELA-'].update(values=dados)
            window['-ID-']('0')
            window['-SITE-']('')
            window['-USUARIO-']('')
            window['-SENHA-']('')
            window['-DESCRICAO-']('')
            window.refresh()
            sg.popup(f'Registro adicionado com sucesso.')
        else:
            sg.popup(f'Ocorreu um erro ao tentar adicionar esse registro.')
    
    elif event == '-CPUSUARIO-':
        us = window['-USUARIO-'].get()
        if len(us) > 0:
            rs = copy2clip(us)
            if rs:
                sg.popup('Usuario copiado para a area de transferencia, com sucesso')
    
    elif event == '-CPSENHA-':
        us = window['-SENHA-'].get()
        if len(us) > 0:
            rs = copy2clip(us)
            if rs:
                sg.popup('Senha copiado para a area de transferencia, com sucesso')
    
    elif event == '-GRSENHA-':
        window['-SENHA-'](gera_senha())

window.close()
