from flask import Blueprint, jsonify, request
from backend.servicos.produto import ProdutoDatabase

produtos_blueprint = Blueprint("produto", __name__)


@produtos_blueprint.route("/produtos", methods=["GET"])
def getprodutos():
    nome = request.args.get("nome", "")
    origem = request.args.get("origem", "")
    loja = request.args.get("loja", "")
    categoria = request.args.get("categoria", "")
    preco_min = request.args.get("preco_min", "")
    preco_max = request.args.get("preco_max", "")
    bem_avaliado = request.args.get("bem_avaliado", "")
    return jsonify(ProdutoDatabase().get_produto(nome, origem, loja, categoria, preco_min, preco_max, bem_avaliado)), 200
