from flask import Blueprint, jsonify, request
from backend.serviços.produto import ProdutoDatabase

produtos_blueprint = Blueprint("produto", __name__)


@produtos_blueprint.route("/produtos", methods=["GET"])
def getprodutos():
    origem = request.args.get("origem", "")
    loja = request.args.get("loja", "")
    categoria = request.args.get("categoria", "")
    return jsonify(ProdutoDatabase().get_produto(origem, loja, categoria)), 200
