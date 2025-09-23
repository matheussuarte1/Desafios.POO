from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

# ------------------------------
# CLASSES (POO)
# ------------------------------
class Conta:
    contas = {}  # { (agencia, numero): Conta }

    def __init__(self, nome, agencia, numero, senha, saldo: float):
        self.nome = nome
        self.agencia = agencia
        self.numero = numero
        self.senha = senha
        self.saldo = float(saldo)  # garante que seja float
        self.limite = 0.0
        self.chave_pix = None
        self.extrato = []  # Lista de operações

    @classmethod
    def criar_conta(cls, nome, agencia, numero, senha, saldo: float):
        chave = (agencia, numero)
        if chave in cls.contas:
            return None
        conta = Conta(nome, agencia, numero, senha, saldo)
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
        self.registrar_operacao(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Limite alterado para {novo_limite:.2f}")

    def alterar_senha(self, nova_senha):
        self.senha = nova_senha

    def cadastrar_pix(self, chave):
        self.chave_pix = chave

    def fazer_pix(self, chave_destino, valor):
        if self.chave_pix == chave_destino:
            return False, "Não é permitido fazer Pix para a própria conta."

        destino = next((c for c in Conta.contas.values() if c.chave_pix == chave_destino), None)

        if not destino:
            return False, "Chave Pix de destino não encontrada."

        if valor <= 0:
            return False, "Valor inválido para Pix."

        if self.saldo + self.limite < valor:
            return False, "Saldo e limite insuficientes."

        # Débito do valor
        if self.saldo >= valor:
            self.saldo -= valor
        else:
            restante = valor - self.saldo
            self.saldo = 0
            self.limite -= restante

        destino.saldo += valor
        self.registrar_operacao(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Pix enviado: -{valor:.2f} para {chave_destino}")
        destino.registrar_operacao(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Pix recebido: +{valor:.2f} de {self.nome}")
        return True, f"Pix de {valor:.2f} enviado para {chave_destino}"

# ------------------------------
# APP FLASK
# ------------------------------
app = Flask(__name__)         #Criando o app com flask
app.secret_key = "chave_secreta"

# Criar conta de teste
Conta.criar_conta("João Silva", "001", "1234", "1234", 400)
Conta.criar_conta("Jorge", "003", "123", "123", 450)

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
        acao = request.form.get("acao")

        if acao == "cadastrar":
            chave = request.form.get("chave", "").strip()
            if not chave:
                flash("Informe uma chave PIX válida.")
            else:
                conta.cadastrar_pix(chave)
                flash(f"Chave Pix cadastrada: {chave}")

        elif acao == "fazer":
            chave_destino = request.form.get("chave_destino", "").strip()
            valor_str = request.form.get("valor", "").strip()

            # Validação de entradas
            if not chave_destino or not valor_str:
                flash("Preencha a chave e o valor.", "pix")
                return redirect(url_for("pix"))

            try:
                valor = float(valor_str)
                if valor <= 0:
                    flash("O valor do PIX deve ser maior que zero.", "pix")
                    return redirect(url_for("pix"))
            except ValueError:
                flash("Informe um valor numérico válido.", "pix")
                return redirect(url_for("pix"))

            # Realiza o PIX
            sucesso, msg = conta.fazer_pix(chave_destino, valor)
            flash(msg, "pix")

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

    erro = None  # Variável para mensagem de erro

    if request.method == "POST":
        senha_atual = request.form["senha_atual"]
        nova_senha = request.form["nova_senha"]

        if senha_atual != conta.senha:
            erro = "Senha atual incorreta."
        else:
            conta.alterar_senha(nova_senha)
            flash("Senha alterada com sucesso.", "senha")

    return render_template("alterar_senha.html", conta=conta, erro=erro)
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