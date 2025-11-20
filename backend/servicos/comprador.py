from backend.servicos.database.conector import DatabaseManager
from datetime import datetime
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
            indice = 0
            for item in carrinho:
                if "produto" in item:
                    if item["idade"] == id_produto:
                        indice = item
                        break
            
            if indice:
                carrinho(indice)['quantidade'] += quantidade

            carrinho.append({
                'produto' : id_produto,
                'quantidade' : quantidade
            })
            return True
        return False
    