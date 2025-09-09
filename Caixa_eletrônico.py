class Usuario:
    def __init__(self, nome: str, agencia: int, conta: int, senha: int):
        self.nome = nome
        self.agencia = agencia
        self.conta = conta
        self.senha = senha

    def login(self):
        login_senha = int(input('Digite a senha:'))
        login_agencia = int(input('Digite a agencia:'))
        login_conta = int(input('Digite a conta:'))
        if (self.senha == login_senha and
            self.conta == login_conta and
            self.agencia == login_agencia):
            print("Login realizado com sucesso!")
            return True
        else:
            print("Algum dado não está correto")
            return False

    def mudar_senha(self, nova_senha):
        self.senha = nova_senha


class ContaBanco:
    def __init__(self, usuario: Usuario, saldo: float = 0, limite: float = 0, chave_pix: str = ""):  #Passando a class Usuario como parametro eu posso acessar os atributos na minha classe ContaBanco
        self.usuario = usuario  # referência ao usuário
        self.saldo = saldo
        self.limite = limite
        self.chave_pix = chave_pix

    def Usuario_logado(self):
        if self.usuario.login():  # chama o login do usuário
            print(f"Agência: {self.usuario.agencia}")
            print(f"Conta: {self.usuario.conta}")
            print(f"Saldo: {self.saldo}")
        else:
            print("Não foi possível acessar as informações do usuário.")
    
    def Alterar_chave_pix(self):
        nova_chave = input('Insira uma chave pix: ')
        self.chave_pix = nova_chave

    def Consultar_chave_pix(self):
        self.Alterar_chave_pix()  # chama corretamente na instância
        print(f"Chave Pix cadastrada: {self.chave_pix}")
        

    def fazer_pix(self, conta: 'ContaBanco'):
        valor = float(input('Insira um valor de pix: '))
        if self.saldo >= valor:
            self.saldo -= valor
            conta.saldo += valor
            print(f"Pix de {valor} realizado de {self.usuario.nome} para {conta.usuario.nome}")
        else:
            print("Saldo insuficiente para realizar o Pix")

# Criação de usuários
usuario1 = Usuario('João',1111, 2222, 3333)
usuario2 = Usuario('Sergio', 4444, 5555, 6666)

# Criação de contas
conta1 = ContaBanco(usuario1, saldo=1000)
conta2 = ContaBanco(usuario2, saldo=500)

# Fazer login do usuário 1
conta1.Usuario_logado()

# Transferir Pix de conta1 para conta2
conta1.fazer_pix(conta2)

# Conferir saldos
print(f"Saldo conta1: {conta1.saldo}")
print(f"Saldo conta2: {conta2.saldo}")

        
        