from flask import Flask, render_template, request, redirect, url_for, session, flash

# ------------------------------
# CLASSES (POO)
# ------------------------------
class Conta:
    contas = {}  # { (agencia, numero): Conta }

    def __init__(self, nome, agencia, numero, senha):
        self.nome = nome
        self.agencia = agencia
        self.numero = numero
        self.senha = senha
        self.saldo = 0.0
        self.limite = 0.0
        self.chave_pix = None
        self.extrato = []  # Lista de operações

    @classmethod
    def criar_conta(cls, nome, agencia, numero, senha):
        chave = (agencia, numero)
        if chave in cls.contas:
            return None
        conta = Conta(nome, agencia, numero, senha)
        cls.contas[chave] = conta
        return conta

    @classmethod
    def autenticar(cls, agencia, numero, senha):
        conta = cls.contas.get((agencia, numero))
        if conta and conta.senha == senha:
            return conta
        return None

    def registrar_operacao(self, descricao):
        self.extrato.append(descricao)

    def alterar_limite(self, novo_limite):
        self.limite = novo_limite
        self.registrar_operacao(f"Limite alterado para {novo_limite:.2f}")

    def alterar_senha(self, nova_senha):
        self.senha = nova_senha
        self.registrar_operacao("Senha alterada")

    def cadastrar_pix(self, chave):
        self.chave_pix = chave
        self.registrar_operacao(f"Chave Pix cadastrada: {chave}")

    def fazer_pix(self, chave_destino, valor):
        # Se for Pix para a própria conta, é crédito
        if self.chave_pix == chave_destino:
            self.saldo += valor
            self.registrar_operacao(f"Pix recebido (próprio): +{valor:.2f}")
            return True, "Pix creditado na própria conta."
        # Buscar conta destino
        destino = next((c for c in Conta.contas.values() if c.chave_pix == chave_destino), None)
        if destino:
            if self.saldo + self.limite >= valor:
                # Calcula quanto usar do saldo e quanto do limite
                if self.saldo >= valor:
                    self.saldo -= valor
                else:
                    restante = valor - self.saldo
                    self.saldo = 0
                    self.limite -= restante  # desconta do limite
                destino.saldo += valor
                self.registrar_operacao(f"Pix enviado: -{valor:.2f} para {chave_destino}")
                destino.registrar_operacao(f"Pix recebido: +{valor:.2f} de {self.nome}")
                return True, f"Pix de {valor:.2f} enviado para {chave_destino}."
            else:
                return False, "Saldo e limite insuficientes."



# ------------------------------
# APP FLASK
# ------------------------------
app = Flask(__name__)         #Criando o app com flask
app.secret_key = "chave_secreta"

# Criar conta de teste
Conta.criar_conta("João Silva", "001", "12345", "1234")
Conta.criar_conta("Jorge", "003", "123", "123")

def conta_logada():
    if "agencia" in session and "numero" in session:
        return Conta.contas.get((session["agencia"], session["numero"]))
    return None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        agencia = request.form["agencia"]
        numero = request.form["conta"]
        senha = request.form["senha"]
        conta = Conta.autenticar(agencia, numero, senha)
        if conta:
            session["agencia"] = agencia
            session["numero"] = numero
            return redirect(url_for("home"))
        flash("Dados inválidos.")
    return render_template("login.html")

@app.route("/home")
def home():
    conta = conta_logada()
    if not conta:
        return redirect(url_for("login"))
    return render_template("home.html", conta=conta)

@app.route("/pix", methods=["GET", "POST"])
def pix():
    conta = conta_logada()
    if not conta:
        return redirect(url_for("login"))

    if request.method == "POST":
        acao = request.form["acao"]
        if acao == "cadastrar":
            chave = request.form["chave"]
            conta.cadastrar_pix(chave)
            flash("Chave Pix cadastrada com sucesso.")
        elif acao == "fazer":
            chave_destino = request.form["chave_destino"]
            valor = float(request.form["valor"])
            ok, msg = conta.fazer_pix(chave_destino, valor)
            flash(msg)
    return render_template("pix.html", conta=conta)

@app.route("/alterar_limite", methods=["GET", "POST"])
def alterar_limite():
    conta = conta_logada()
    if not conta:
        return redirect(url_for("login"))
    if request.method == "POST":
        novo_limite = float(request.form["limite"])
        conta.alterar_limite(novo_limite)
        flash("Limite alterado com sucesso.")
        return redirect(url_for("home"))
    return render_template("alterar_limite.html", conta=conta)

@app.route("/alterar_senha", methods=["GET", "POST"])
def alterar_senha():
    conta = conta_logada()
    if not conta:
        return redirect(url_for("login"))
    if request.method == "POST":
        nova_senha = request.form["nova_senha"]
        conta.alterar_senha(nova_senha)
        flash("Senha alterada com sucesso.")
        return redirect(url_for("login"))
    return render_template("alterar_senha.html")

@app.route("/extrato")
def extrato():
    conta = conta_logada()
    if not conta:
        return redirect(url_for("login"))
    return render_template("extrato.html", conta=conta)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)