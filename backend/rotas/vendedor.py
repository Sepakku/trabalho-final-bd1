from flask import Blueprint, jsonify, request
from backend.servicos.vendedor import VendedorDatabase

vendedor_blueprint = Blueprint("vendedor", __name__)


@vendedor_blueprint.route("/vendedor", methods=["GET"])
def getvendedor():
    cpf = request.args.get("cpf", "")
    senha = request.args.get("senha", "")
    return jsonify(VendedorDatabase().get_vendedor(cpf, senha)), 200


@vendedor_blueprint.route("/vendedor", methods=["POST"])
def post_vendedor():
    json = request.get_json()
    cpf = json.get("cpf")
    senha = json.get("senha")
    loja = json.get("loja")
    descricao = json.get("descricao")
    if VendedorDatabase().post_vendedor(cpf, senha, loja, descricao):
        return jsonify("Vendedor registrado"), 200
    return jsonify("Erro ao registrar Vendedor"), 400


@vendedor_blueprint.route("/vendedor", methods=["DELETE"])
def delete_vendedor():
    json = request.get_json()
    cpf = json.get("cpf")
    senha = json.get("senha")

    if not cpf or not senha:
        return jsonify("CPF e senha são obrigatórios"), 400

    if VendedorDatabase().delete_vendedor(cpf, senha):
        return jsonify("Vendedor removido"), 200
    return jsonify("Erro ao remover Vendedor"), 400


@vendedor_blueprint.route("/vendedor", methods=["PATCH"])
def update_vendedor():
    json = request.get_json()
    cpf = json.get("cpf")
    senha = json.get("senha")
    loja = json.get("loja")
    descricao = json.get("descricao")

    if not cpf or not senha:
        return jsonify("CPF e senha são obrigatórios"), 400

    if VendedorDatabase().update_vendedor(cpf, senha, loja, descricao):
        return jsonify("Vendedor atualizado"), 200
    return jsonify("Erro ao atualizar Vendedor"), 400
