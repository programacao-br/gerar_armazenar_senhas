Para esse segundo script de aprendizagem Python.
Foi criado um script para gerar e armazenar senha.
Aqui é utilizado a implementação de criptografia Fernet.

Funcionamento:
Ao iniciar o script é mostrado uma janela pedindo a senha master.

Se for a primeira vez que ele é executado, então será criado um
arquivo [salt.bin] com a chave gerada.

Essa "chave" em conjunto com a "senha master" é o que permite decriptografar
os campos "usuario" e "senha" que forem armazenados pelo script.

ATENÇÃO!!! se a "senha master" for esquecida, ou se o arquivo [salt.bin]
for perdido/deletado, não será possível decriptografar o que já foi salvo.

Objetivo de aprendizagem:
1- Conhecendo mais algum controles do pysimplegui.
2- Entendendo o funcionamento de strings em bytes, encode/decode
3- Usando criptografia com metodo Fernet em conjunto com senhas.
4- Entendendo a forma de copiar a [usuario] e [senha] para a area de transferencia.

![layout](https://user-images.githubusercontent.com/114777198/193620792-5157da06-50fd-49da-82ad-2ac2f88a2a66.png)
