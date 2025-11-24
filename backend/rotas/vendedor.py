from flask import Blueprint, jsonify, request
from backend.servicos.vendedor import VendedorService

vendedor_blueprint = Blueprint("vendedor", __name__)


@vendedor_blueprint.route("/vendedor", methods=["GET"])
def get_vendedor():
    """Retorna informações do vendedor"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    vendedor = VendedorService().get_vendedor(cpf)
    if vendedor:
        return jsonify(vendedor), 200
    return jsonify({"error": "Vendedor não encontrado"}), 404


@vendedor_blueprint.route("/vendedor/produtos/mais-vendidos", methods=["GET"])
def get_produtos_mais_vendidos():
    """Retorna os 3 produtos mais vendidos"""
    cpf = request.args.get("cpf")
    meses = int(request.args.get("meses", 1))
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    produtos = VendedorService().get_produtos_mais_vendidos(cpf, meses)
    return jsonify(produtos), 200


@vendedor_blueprint.route("/vendedor/lucro", methods=["GET"])
def get_lucro_total():
    """Retorna lucro total no período"""
    cpf = request.args.get("cpf")
    meses = int(request.args.get("meses", 1))
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    lucro = VendedorService().get_lucro_total(cpf, meses)
    return jsonify(lucro), 200


@vendedor_blueprint.route("/vendedor/produtos/estoque-baixo", methods=["GET"])
def get_produtos_estoque_baixo():
    """Retorna produtos com estoque baixo"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    produtos = VendedorService().get_produtos_estoque_baixo(cpf)
    return jsonify(produtos), 200


@vendedor_blueprint.route("/vendedor/produtos", methods=["GET"])
def get_produtos():
    """Retorna todos os produtos do vendedor"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    produtos = VendedorService().get_produtos_vendedor(cpf)
    return jsonify(produtos), 200


@vendedor_blueprint.route("/vendedor/produtos", methods=["POST"])
def adicionar_produto():
    """Adiciona novo produto à loja"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    nome = json_data.get("nome")
    descricao = json_data.get("descricao", "")
    preco = json_data.get("preco")
    estoque = json_data.get("estoque", 0)
    alerta_estoque = json_data.get("alerta_estoque", 0)
    origem = json_data.get("origem", "")
    
    if not all([cpf, nome, preco is not None]):
        return jsonify({"error": "cpf, nome e preco são obrigatórios"}), 400
    
    result = VendedorService().adicionar_produto(cpf, nome, descricao, preco, estoque, alerta_estoque, origem)
    if result:
        return jsonify({"message": "Produto adicionado com sucesso"}), 201
    return jsonify({"error": "Erro ao adicionar produto"}), 400


@vendedor_blueprint.route("/vendedor/produtos/<int:id_produto>/estoque", methods=["PATCH"])
def atualizar_estoque(id_produto):
    """Atualiza estoque de um produto"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    nova_quantidade = json_data.get("quantidade")
    
    if not cpf or nova_quantidade is None:
        return jsonify({"error": "cpf e quantidade são obrigatórios"}), 400
    
    result = VendedorService().atualizar_estoque(cpf, id_produto, nova_quantidade)
    if result:
        return jsonify({"message": "Estoque atualizado com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar estoque"}), 400


@vendedor_blueprint.route("/vendedor/produtos/<int:id_produto>", methods=["DELETE"])
def remover_produto(id_produto):
    """Remove produto da loja"""
    cpf = request.args.get("cpf")
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    result = VendedorService().remover_produto(cpf, id_produto)
    if result:
        return jsonify({"message": "Produto removido com sucesso"}), 200
    return jsonify({"error": "Erro ao remover produto"}), 400


@vendedor_blueprint.route("/vendedor/produtos/<int:id_produto>", methods=["PATCH"])
def atualizar_produto(id_produto):
    """Atualiza informações de um produto"""
    json_data = request.get_json()
    cpf = json_data.get("cpf")
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    result = VendedorService().atualizar_produto(
        cpf, id_produto,
        nome=json_data.get("nome"),
        descricao=json_data.get("descricao"),
        preco=json_data.get("preco"),
        origem=json_data.get("origem"),
        alerta_estoque=json_data.get("alerta_estoque")
    )
    if result:
        return jsonify({"message": "Produto atualizado com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar produto"}), 400


@vendedor_blueprint.route("/vendedor/produtos/mais-devolvidos", methods=["GET"])
def get_produtos_mais_devolvidos():
    """Retorna produtos com mais devoluções"""
    cpf = request.args.get("cpf")
    meses = int(request.args.get("meses", 1))
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    produtos = VendedorService().get_produtos_mais_devolvidos(cpf, meses)
    return jsonify(produtos), 200


@vendedor_blueprint.route("/vendedor/produtos/melhor-avaliacao", methods=["GET"])
def get_produtos_melhor_avaliacao():
    """Retorna produtos com melhor avaliação"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    produtos = VendedorService().get_produtos_melhor_avaliacao(cpf)
    return jsonify(produtos), 200


@vendedor_blueprint.route("/vendedor/solicitacoes", methods=["GET"])
def get_solicitacoes():
    """Retorna todas as solicitações relacionadas ao vendedor"""
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    solicitacoes = VendedorService().get_solicitacoes(cpf)
    return jsonify(solicitacoes), 200


@vendedor_blueprint.route("/vendedor/solicitacoes", methods=["PATCH"])
def atualizar_status_solicitacao():
    """Atualiza o status de uma solicitação (aceitar/recusar)"""
    json_data = request.get_json()
    cpf_vendedor = json_data.get("cpf_vendedor")
    cpf_cliente = json_data.get("cpf_cliente")
    data_pedido = json_data.get("data_pedido")
    data_solicitacao = json_data.get("data_solicitacao")
    novo_status = json_data.get("status")  # 'em_analise' ou 'concluida'
    
    if not all([cpf_vendedor, cpf_cliente, data_pedido, data_solicitacao, novo_status]):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    
    if novo_status not in ['em_analise', 'concluida']:
        return jsonify({"error": "Status inválido. Use 'em_analise' ou 'concluida'"}), 400
    
    result = VendedorService().atualizar_status_solicitacao(
        cpf_vendedor, cpf_cliente, data_pedido, data_solicitacao, novo_status
    )
    
    if result:
        status_texto = "aceita" if novo_status == 'concluida' else "em análise"
        return jsonify({"message": f"Solicitação {status_texto} com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar solicitação. Verifique se a solicitação pertence a este vendedor."}), 400

@vendedor_blueprint.route("/vendedor/vendas", methods=["GET"])
def get_vendas_recentes():
    """Retorna lista de vendas recentes"""
    cpf = request.args.get("cpf")
    limite = request.args.get("limite", 5)
    status = request.args.get("status", "")
    
    if not cpf:
        return jsonify({"error": "cpf é obrigatório"}), 400
    
    try:
        limite = int(limite)
    except ValueError:
        limite = 5

    vendas = VendedorService().get_vendas_recentes(cpf, limite, status)
    return jsonify(vendas), 200

@vendedor_blueprint.route("/vendedor/vendas/status", methods=["PATCH"])
def atualizar_status_venda():
    """Atualiza o status de uma venda"""
    json_data = request.get_json()
    cpf_cliente = json_data.get("cpf_cliente")
    data_pedido = json_data.get("data_pedido")
    novo_status = json_data.get("status")
    
    if not all([cpf_cliente, data_pedido, novo_status]):
        return jsonify({"error": "Dados incompletos"}), 400
        
    if novo_status not in ['enviado', 'cancelado', 'entregue']:
        return jsonify({"error": "Status inválido"}), 400

    sucesso = VendedorService().atualizar_status_venda(cpf_cliente, data_pedido, novo_status)
    
    if sucesso:
        return jsonify({"message": "Status atualizado com sucesso"}), 200
    return jsonify({"error": "Erro ao atualizar status"}), 400

@vendedor_blueprint.route("/vendedor/pedidos/aguardando-envio", methods=["GET"])
def get_pedidos_aguardando_envio():
    """Retorna pedidos com status 'pagamento confirmado' aguardando envio"""
    cpf_vendedor = request.args.get("cpf_vendedor")
    if not cpf_vendedor:
        return jsonify({"error": "cpf_vendedor é obrigatório"}), 400
    
    pedidos = VendedorService().get_pedidos_aguardando_envio(cpf_vendedor)
    return jsonify(pedidos), 200

@vendedor_blueprint.route("/vendedor/pedido/enviar", methods=["POST"])
def enviar_pedido():
    """Marca um pedido como enviado (muda de 'pagamento confirmado' para 'enviado') e cria/atualiza entrega"""
    json_data = request.get_json()
    cpf_vendedor = json_data.get("cpf_vendedor")
    cpf_cliente = json_data.get("cpf_cliente")
    data_pedido = json_data.get("data_pedido")
    
    if not all([cpf_vendedor, cpf_cliente, data_pedido]):
        return jsonify({"error": "cpf_vendedor, cpf_cliente e data_pedido são obrigatórios"}), 400
    
    result = VendedorService().enviar_pedido(cpf_vendedor, cpf_cliente, data_pedido)
    if result:
        return jsonify({"message": "Pedido marcado como enviado com sucesso. Entrega criada/atualizada."}), 200
    return jsonify({"error": "Erro ao enviar pedido. Verifique se o pedido pertence a este vendedor e está com status 'pagamento confirmado'."}), 400