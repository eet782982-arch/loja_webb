from flask import Flask, request, redirect, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

ARQUIVO = "dados.json"
RESET_SENHA = "1234"  # 🔐 ALTERA AQUI A SENHA

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

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Loja Web</title>
<style>
body{
font-family:Arial;
background:#f4f4f4;
margin:20px;
}
.card{
background:white;
padding:15px;
border-radius:10px;
margin-bottom:15px;
box-shadow:0 0 5px #ccc;
}
input{
padding:8px;
margin:5px;
}
button{
padding:10px;
background:#2196F3;
color:white;
border:none;
border-radius:5px;
cursor:pointer;
}
button.reset{
background:#e53935;
}
table{
width:100%;
border-collapse:collapse;
}
th,td{
border:1px solid #ddd;
padding:8px;
}
th{
background:#2196F3;
color:white;
}
</style>
</head>
<body>

<h1>Sistema de Gestão de Loja</h1>

<div class="card">
<h2>Adicionar Produto</h2>
<form method="post" action="/entrada">
<input name="nome" placeholder="Nome do Produto" required>
<input type="number" name="quantidade" placeholder="Quantidade" required>
<input type="number" step="0.01" name="custo" placeholder="Preço de Custo" required>
<input type="number" step="0.01" name="venda" placeholder="Preço de Venda" required>
<button>Adicionar</button>
</form>
</div>

<div class="card">
<h2>Registrar Venda</h2>
<form method="post" action="/venda">
<input name="nome" placeholder="Produto" required>
<input type="number" name="quantidade" placeholder="Quantidade" required>
<button>Vender</button>
</form>
</div>

<div class="card">
<h2>Estoque</h2>
<table>
<tr>
<th>Produto</th>
<th>Qtd</th>
<th>Custo</th>
<th>Venda</th>
</tr>
{% for nome,d in estoque.items() %}
<tr>
<td>{{nome}}</td>
<td>{{d.quantidade}}</td>
<td>{{d.preco_custo}}</td>
<td>{{d.preco_venda}}</td>
</tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>Relatório de Hoje</h2>

<p><b>Total Vendido:</b> {{total_vendas}} Kz</p>
<p><b>Lucro:</b> {{total_lucro}} Kz</p>

<table>
<tr>
<th>Produto</th>
<th>Qtd</th>
<th>Venda</th>
<th>Lucro</th>
</tr>

{% for v in vendas %}
<tr>
<td>{{v.produto}}</td>
<td>{{v.quantidade}}</td>
<td>{{v.valor_venda}}</td>
<td>{{v.lucro}}</td>
</tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>Controle do Sistema</h2>

<form method="post" action="/reset" onsubmit="return confirm('Tens certeza que queres apagar TUDO?');">
<input type="password" name="senha" placeholder="Senha de reset" required>
<button class="reset" type="submit">Reiniciar Tudo</button>
</form>

</div>

</body>
</html>
"""

@app.route("/")
def inicio():
    dados = carregar()

    hoje = datetime.now().date()

    vendas = []

    for v in dados["vendas"]:
        if datetime.fromisoformat(v["data"]).date() == hoje:
            vendas.append(v)

    total_vendas = sum(v["valor_venda"] for v in vendas)
    total_lucro = sum(v["lucro"] for v in vendas)

    return render_template_string(
        HTML,
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
        return "<h3>Senha incorreta! Acesso negado.</h3><a href='/'>Voltar</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
