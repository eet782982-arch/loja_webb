from flask import Flask, request, redirect, render_template
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas

app = Flask(__name__)

ARQUIVO = "dados.json"
RESET_SENHA = "1234"

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump({"estoque": {}, "vendas": []}, f)

def carregar():
    with open(ARQUIVO, "r") as f:
        return json.load(f)

def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

def resetar_dados():
    with open(ARQUIVO, "w") as f:
        json.dump({"estoque": {}, "vendas": []}, f, indent=4)


@app.route("/")
def inicio():
    dados = carregar()
    hoje = datetime.now().date()

    vendas = [
        v for v in dados["vendas"]
        if datetime.fromisoformat(v["data"]).date() == hoje
    ]

    total_vendas = sum(v["valor_venda"] for v in vendas)
    total_lucro = sum(v["lucro"] for v in vendas)

    return render_template(
        "index.html",
        estoque=dados["estoque"],
        vendas=vendas,
        total_vendas=total_vendas,
        total_lucro=total_lucro
    )


@app.route("/entrada", methods=["POST"])
def entrada():
    dados = carregar()

    nome = request.form["nome"]
    quantidade = int(request.form["quantidade"])
    custo = float(request.form["custo"])
    venda = float(request.form["venda"])

    if nome in dados["estoque"]:
        dados["estoque"][nome]["quantidade"] += quantidade
    else:
        dados["estoque"][nome] = {
            "quantidade": quantidade,
            "preco_custo": custo,
            "preco_venda": venda
        }

    salvar(dados)
    return redirect("/")


@app.route("/venda", methods=["POST"])
def venda():
    dados = carregar()

    nome = request.form["nome"]
    quantidade = int(request.form["quantidade"])

    if nome in dados["estoque"]:
        if dados["estoque"][nome]["quantidade"] >= quantidade:

            custo = dados["estoque"][nome]["preco_custo"]
            preco = dados["estoque"][nome]["preco_venda"]

            lucro = (preco - custo) * quantidade

            dados["estoque"][nome]["quantidade"] -= quantidade

            dados["vendas"].append({
                "produto": nome,
                "quantidade": quantidade,
                "valor_venda": preco * quantidade,
                "lucro": lucro,
                "data": datetime.now().isoformat()
            })

            salvar(dados)

    return redirect("/")


@app.route("/reset", methods=["POST"])
def reset():
    senha = request.form.get("senha")

    if senha == RESET_SENHA:
        resetar_dados()
        return redirect("/")
    else:
        return "<h3>Senha incorreta!</h3><a href='/'>Voltar</a>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
