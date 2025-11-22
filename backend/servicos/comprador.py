from backend.servicos.database.conector import DatabaseManager
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

class cliente:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    # armazena no DB uma nova avaliação de um produto ou a atualização de uma já existente
    def post_avaliacao(self, cpf: str, id_produto: int, nota: int):
        if cpf and id_produto and nota >= 0 and nota <= 5:
            query = """"
                select * 
                from avaliaprod
                where cpf_comprador = %(cpf)s and id_produto = %(id_produto)s
            """
            params = {
                "cpf": cpf,
                "id_produto": id_produto
            }
            avaliacao_anterior = self.db.execute_select_one(query,params)
            if avaliacao_anterior:
                query = """"
                    update avaliaprod
                    set nota = %(nota)s
                    where cpf_comprador = %(cpf)s and id_produto = %(id_produto)s
                """
                params = {
                    "cpf": cpf,
                    "id_produto": id_produto,
                    "nota": nota
                }
                self.db.execute_statement(query,params)
                return True
            query = """"
                insert into avaliaprod (cpf_comprador, id_produto, nota)
                values (%(cpf)s, %(id_produto)s, %(nota)s)
            """
            params = {
                    "cpf": cpf,
                    "id_produto": id_produto,
                    "nota": nota
                }
            # inserção sobre a premissa que o CPF e id_produto sempre existirão em suas respectivas tabelas
            self.db.execute_statement(query,params)
            return True
        return False
    
    #armazena no DB uma nova solicitação
    def post_solicitacao(self, cpf: str, data_pedido :datetime, tipo: str):
        if cpf and data_pedido and tipo:
            data_solicitacao = datetime.now(ZoneInfo("America/Sao_Paulo"))
            status_solicitacao = 'aberta'
            query = """"
                insert into solicitacao (cpf_cliente, data_pedido, data_solicitacao, tipo, status_solicitacao)
                values (%(cpf)s, %(data_pedido)s, %(data_solicitacao)s, %(tipo)s, %(status_solicitacao)s)
                """
            params = {
                    "cpf": cpf,
                    "data_pedido": data_pedido,
                    "data_solicitacao": data_solicitacao,
                    "tipo": tipo,
                    "status_solicitacao": status_solicitacao
                }
            self.db.execute_statement(query,params)
            return True
        return False
    
    #Adiciona um produto ao carrinho ou aumenta a quantidade quando produto já estiver presente
    def post_carrinho(self, id_produto: int, quantidade: int, carrinho: list):
        if id_produto and quantidade:
            indice = None
            for i, item in enumerate(carrinho):
                if item.get("produto") == id_produto:
                    indice = i
                    break
            
            if indice is not None:
                carrinho[indice]['quantidade'] += quantidade
            else:
                carrinho.append({
                'produto': id_produto,
                'quantidade': quantidade
            })
            return True
        return False
    
    #retorna uma query com as informações dos produtos que estão no carrinho
    def get_carrinho(self, carrinho: list):
        if not carrinho:
            return []

        id_produtos = [item["produto"] for item in carrinho]
        params = ", ".join(["%s"] * len(id_produtos))

        query = f"""
            SELECT nome_produto, preco
            FROM produto
            WHERE id IN ({params})
        """
        return self.db.execute_select_all(query)
    
    def valida_pag(self, valor_total):
        return True
    
    #Armazena no DB um novo pedido e atualiza todas as tabelas necessárias
    def post_pedido_individual(self, cpf_cliente: str, id_produto: int, quantidade: int, metodo_pagamento: str, num_parcelas: int, metodo_entrega: str, endereco_cliente: str):

        if cpf_cliente and id_produto and quantidade > 0:
            query = """
                SELECT estoque_atual, preco
                FROM produto
                WHERE id_produto = %(id_produto)s
            """
            params = {
                "id_produto": id_produto
            }
            Resultado = self.db.execute_select_one(query,params)
            if Resultado["estoque_atual"] < quantidade:
                return False
            data_pedido = datetime.now(ZoneInfo("America/Sao_Paulo"))
            total_pedido = quantidade * Resultado["preco"]
            status_pedido = "pendente"

            #inserindo registro na tabela pedido
            query = """"
                INSERT INTO pedido(cpf_cliente, data_pedido, status_pedido, total_produtos, total_pedido)
                VALUES (%(cpf_cliente)s, %(data_pedido)s, %(stats_pedido)s, %(quantidade)s, %(total_pedido)s)            
            """
            params = {
                "cpf_cliente": cpf_cliente,
                "data_pedido": data_pedido,
                "status_pedido": status_pedido,
                "quantidade": quantidade,
                "total_pedido": total_pedido
            }
            self.db.execute_statement(query,params)

            #inserindo registro na tabela contemprod
            query = """"
                INSERT INTO contemprod(cpf_cliente, data_pedido, id_produto, quantidade)
                VALUES (%(cpf_cliente)s, %(data_pedido)s, %(id_produto)s, %(quantidade)s)
            """
            params = {
                "cpf_cliente": cpf_cliente,
                "data_pedido": data_pedido,
                "id_produto": id_produto,
                "quantidade": quantidade
            }
            self.db.execute_statement(query,params)

            Novo_estoque = Resultado["estoque_atual"] - quantidade
            #atualizando o estoque atual do produto
            query = """"
                UPDATE produto
                SET estoque_atual = (%(Novo_estoque)s)
                WHERE id_produto = (%(id_produto)s)
            """
            params = {
                "Novo_estoque": Novo_estoque,
                "id_produto": id_produto
            }
            self.db.execute_statement(query,params)

            #busca pelo cpf do vendedor
            query = """"
                SELECT cpf_vendedor
                FROM vendeprod
                WHERE id_produto = (%(id_produto)s)            
            """

            params = {
                "id_produto": id_produto
            }
            cpf_vendedor = self.db.execute_select_one(query,params)
            cpf_vendedor = ["cpf_vendedor"]

            #inserindo registro na tabela pagamento
            if self.valida_pag(total_pedido):
                pagamento_valido = "aprovado"
            else:
                pagamento_valido = "pendente"
            query = """"
                INSERT INTO pagamento (status_pagamento, valor_pago, metodo_pagamento, num_parcelas, fk_cpf_vendedor, fk_cpf_cliente, fk_data_pedido)
                VALUES (%(pagamento_valido)s, %(total_pedido)s, %(metodo_pagamento)s, %(num_parcelas)s, %(cpf_vendedor)s, %(cpf_cliente)s, %(data_pedido)s)
            """
            params = {
                "pagamento_valido": pagamento_valido,
                "total_pedido": total_pedido,
                "metodo_pagamento": metodo_pagamento,
                "num_parcelas": num_parcelas,
                "cpf_vendedor": cpf_vendedor,
                "cpf_cliente": cpf_cliente,
                "data_pedido": data_pedido
            }
            self.db.execute_statement(query,params)

            #Atualizando numero de compras
            query = """
                UPDATE comprador
                SET num_compras = num_compras + 1
                WHERE cpf_comprador = (%(cpf_cliente)s)
            """
            params = {
                "cpf_cliente": cpf_cliente
            }
            self.db.execute_statement(query,params)

            #inserindo registro na tabela pagamento
            data_envio = data_pedido + timedelta(days=2)
            data_prevista = data_pedido + timedelta(days=7)
            frete = 20
            query = """"
                SELECT endereco
                FROM usuario
                WHERE cpf = (%(cpf_vendedor)s)    
            """
            params = {
                "cpf_vendedor": cpf_vendedor
            }
            endereco_vendedor = self.db.execute_select_one(query, params)
            endereco_vendedor = endereco_vendedor["endereco"]


            query = """"
                INSERT INTO entrega (status_entrega, metodo_entrega, endereco_entrega, data_envio, data_prevista, frete, endereco_vendedor, fk_cpf_cliente, fk_data_pedido, fk_cpf_vendedor)
                VALUES ("preparando", %(metodo_entrega)s, %(endereco_cliente)s, %(data_envio)s, %(data_prevista)s, %(frete)s, %(endereco_vendedor)s, %(cpf_cliente)s, %(data_pedido)s, %(cpf_vendedor)s)
            """
            params = {
                "metodo_entrega": metodo_entrega,
                "endereco_cliente": endereco_cliente,
                "data_envio": data_envio,
                "data_prevista": data_prevista,
                "frete": frete,
                "endereco_vendedor": endereco_vendedor,
                "cpf_cliente": cpf_cliente,
                "data_pedido": data_pedido,
                "cpf_vendedor": cpf_vendedor
            }
            return True
        return False