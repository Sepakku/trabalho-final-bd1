from flask import Blueprint, jsonify, request
from backend.servicos.produto_comprador import ProdutoCompradorDatabase

produtos_comprador_blueprint = Blueprint("produto_comprador", __name__)


@produtos_comprador_blueprint.route("/produtos_comprador", methods=["GET"])
def getprodutos_comprador():
    nome = request.args.get("nome", "")
    origem = request.args.get("origem", "")
    loja = request.args.get("loja", "")
    categoria = request.args.get("categoria", "")
    preco_min = request.args.get("preco_min", "")
    preco_max = request.args.get("preco_max", "")
    bem_avaliado = request.args.get("bem_avaliado", "")
    return jsonify(ProdutoCompradorDatabase().get_produto_comprador(nome, origem, loja, categoria, preco_min, preco_max, bem_avaliado)), 200


@produtos_comprador_blueprint.route("/categorias", methods=["GET"])
def get_categorias():
    """Retorna todas as categorias disponíveis"""
    categorias = ProdutoCompradorDatabase().get_categorias()
    return jsonify(categorias), 200
