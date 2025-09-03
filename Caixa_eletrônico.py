class Usuario:
    def __init__(self, agencia:int, conta:int, senha:int):
        self.agencia = agencia
        self.conta = conta
        self.senha = senha

    def login(self):
        self.login_senha = int(input('Digite a senha: '))
        self.login_agencia = int(input('Digite a agencia: '))
        self.login_conta = int(input('Digite a conta: '))
        if (self.senha == self.login_senha and
            self.conta == self.login_conta and
            self.agencia == self.login_agencia):
            return True
        else:
            return False

    def mudar_senha(self, nova_senha):
        self.senha = nova_senha


usuario1 = Usuario(1111, 2222, 3333)

usuario1.login()

class conta_banco:
    def __init__(self, limite:int = 0, chave_pix:str = ""):
        self.limite = limite
        self.chave_pix = chave_pix

        
        