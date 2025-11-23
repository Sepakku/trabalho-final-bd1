from flask import Blueprint, jsonify, request
from backend.servicos.comprador import CompradorService

comprador_blueprint = Blueprint("comprador", __name__)


@comprador_blueprint.route("/comprador/carrinho", methods=["POST"])
def adicionar_carrinho():
    """Adiciona produto ao carrinho/pedido"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    id_produto = json_data.get("id_produto")
    quantidade = json_data.get("quantidade", 1)
    
    if not cpf or not id_produto:
        return jsonify({"error": "cpf e id_produto são obrigatórios"}), 400
    
    result = CompradorService().adicionar_ao_carrinho(cpf, id_produto, quantidade)
    if result is None:
        return jsonify({"error": "comprador_nao_existe", "message": "Comprador não encontrado. Por favor, cadastre-se primeiro."}), 404
    if result:
        return jsonify({"message": "Produto adicionado ao carrinho"}), 200
    return jsonify({"error": "Erro ao adicionar produto"}), 400


@comprador_blueprint.route("/comprador/cadastrar", methods=["POST"])
def cadastrar_comprador():
    """Cadastra um novo comprador"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    pnome = json_data.get("pnome")
    sobrenome = json_data.get("sobrenome")
    cep = json_data.get("cep")
    email = json_data.get("email")
    senha = json_data.get("senha")
    
    if not cpf or not pnome or not sobrenome or not email or not senha:
        return jsonify({"error": "cpf, pnome, sobrenome, email e senha são obrigatórios"}), 400
    
    # Hash simples da senha (em produção, usar bcrypt ou similar)
    import hashlib
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    success, message = CompradorService().criar_comprador(cpf, pnome, sobrenome, cep, email, senha_hash)
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


@comprador_blueprint.route("/comprador/carrinho/<int:id_produto>", methods=["DELETE"])
def remover_carrinho(id_produto):
    """Remove produto do carrinho/pedido"""
    cpf = request.args.get("cpf")
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    result = CompradorService().remover_do_carrinho(cpf, id_produto)
    if result:
        return jsonify({"message": "Produto removido do carrinho"}), 200
    return jsonify({"error": "Erro ao remover produto do carrinho"}), 400


@comprador_blueprint.route("/comprador/pedidos", methods=["GET"])
def visualizar_pedidos():
    """Visualiza pedidos do comprador"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    pedidos = CompradorService().get_pedidos(cpf)
    return jsonify(pedidos), 200


@comprador_blueprint.route("/comprador/pedido", methods=["GET"])
def visualizar_pedido_detalhes():
    """Visualiza detalhes de um pedido específico"""
    cpf = request.args.get("cpf")
    data_pedido = request.args.get("data_pedido")
    
    if not cpf or not data_pedido:
        return jsonify({"error": "cpf e data_pedido são obrigatórios"}), 400
    
    pedido = CompradorService().get_pedido_detalhes(cpf, data_pedido)
    if pedido:
        return jsonify(pedido), 200
    return jsonify({"error": "Pedido não encontrado"}), 404


@comprador_blueprint.route("/comprador/pedido/finalizar", methods=["POST"])
def finalizar_pedido():
    """Finaliza pedido com método de pagamento, método de entrega e endereço"""
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({"error": "Dados JSON não fornecidos"}), 400
    
    cpf = json_data.get("cpf")
    metodo_pagamento = json_data.get("metodo_pagamento")  # credito, debito, pix
    metodo_entrega = json_data.get("metodo_entrega")  # Correios, PAC, Motoboy
    endereco_entrega = json_data.get("endereco_entrega")
    
    if not cpf:
        return jsonify({"error": "CPF é obrigatório"}), 400
    if not metodo_pagamento:
        return jsonify({"error": "Método de pagamento é obrigatório"}), 400
    if not metodo_entrega:
        return jsonify({"error": "Método de entrega é obrigatório"}), 400
    if not endereco_entrega:
        return jsonify({"error": "Endereço de entrega é obrigatório"}), 400
    
    try:
        result = CompradorService().finalizar_pedido(cpf, metodo_pagamento, endereco_entrega, metodo_entrega)
        if result:
            return jsonify({"message": "Pedido finalizado com sucesso"}), 200
        else:
            return jsonify({"error": "Não foi possível finalizar o pedido. Verifique se o carrinho tem produtos e se há um pedido pendente."}), 400
    except Exception as e:
        print(f"Erro ao finalizar pedido: {e}")
        return jsonify({"error": f"Erro interno ao finalizar pedido: {str(e)}"}), 500


@comprador_blueprint.route("/comprador/pedido/simular-pagamento", methods=["POST"])
def simular_pagamento():
    """Simula pagamento de um pedido, atualizando status de 'pendente' para 'aprovado'"""
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({"error": "Dados JSON não fornecidos"}), 400
    
    cpf = json_data.get("cpf")
    data_pedido = json_data.get("data_pedido")
    
    if not cpf:
        return jsonify({"error": "CPF é obrigatório"}), 400
    if not data_pedido:
        return jsonify({"error": "data_pedido é obrigatório"}), 400
    
    try:
        result = CompradorService().simular_pagamento(cpf, data_pedido)
        if result:
            return jsonify({"message": "Pagamento simulado com sucesso. Status atualizado para 'aprovado'."}), 200
        else:
            return jsonify({"error": "Não foi possível simular pagamento. Verifique se o pedido tem um pagamento pendente."}), 400
    except Exception as e:
        print(f"Erro ao simular pagamento: {e}")
        return jsonify({"error": f"Erro interno ao simular pagamento: {str(e)}"}), 500


@comprador_blueprint.route("/comprador/pedido/solicitacao", methods=["POST"])
def criar_solicitacao():
    """Cria solicitação sobre um pedido"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    data_pedido = json_data.get("data_pedido")
    tipo = json_data.get("tipo")  # devolucao, troca, suporte, cancelamento
    
    if not cpf or not data_pedido or not tipo:
        return jsonify({"error": "cpf, data_pedido e tipo são obrigatórios"}), 400
    
    result = CompradorService().criar_solicitacao(cpf, data_pedido, tipo)
    if result:
        return jsonify({"message": "Solicitação criada com sucesso"}), 201
    return jsonify({"error": "Erro ao criar solicitação"}), 400


@comprador_blueprint.route("/comprador/produtos-comprados", methods=["GET"])
def produtos_comprados():
    """Retorna lista de produtos que o comprador já comprou"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    produtos = CompradorService().get_produtos_comprados(cpf)
    return jsonify(produtos), 200


@comprador_blueprint.route("/comprador/avaliacao", methods=["POST"])
def avaliar_produto():
    """Avalia um produto"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    id_produto = json_data.get("id_produto")
    nota = json_data.get("nota")  # 1 a 5
    comentario = json_data.get("comentario", "")
    
    if not cpf or not id_produto or not nota:
        return jsonify({"error": "cpf, id_produto e nota são obrigatórios"}), 400
    
    if nota < 1 or nota > 5:
        return jsonify({"error": "Nota deve estar entre 1 e 5"}), 400
    
    result = CompradorService().avaliar_produto(cpf, id_produto, nota, comentario)
    if result:
        return jsonify({"message": "Produto avaliado com sucesso"}), 200
    return jsonify({"error": "Erro ao avaliar produto. Verifique se você comprou este produto."}), 400

@comprador_blueprint.route("/comprador/recomendacoes", methods=["GET"])
def get_recomendacoes():
    """Retorna recomendações baseadas na categoria preferida"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    recomendacoes = CompradorService().get_recomendacoes(cpf)
    
    # Se retornar lista vazia, o front tratará, mas retornamos 200 OK
    return jsonify(recomendacoes), 200