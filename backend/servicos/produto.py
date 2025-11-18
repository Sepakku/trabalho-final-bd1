from backend.serviços.database.conector import DatabaseManager


class ProdutoDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    def get_produto(self, origem: str, loja: str, categoria: str):
        query = """
                SELECT 
                    p.alerta_estoque, 
                    p.desc_produto, p.estoque_atual, 
                    p.id_produto, 
                    cat.nome_categoria, 
                    v.nome_loja, 
                    p.nome_produto, 
                    p.origem, 
                    p.preco 
                FROM produto p
                LEFT JOIN vendeprod vp ON vp.id_produto = p.id_produto
                LEFT JOIN pertencecat pc ON pc.id_produto = p.id_produto
                LEFT JOIN categoria cat ON cat.id_categoria = pc.id_categoria
                LEFT JOIN vendedor v ON v.cpf_vendedor = vp.cpf_vendedor
                """

        if origem:
            query += f"WHERE p.origem = '{origem}'\n"

        if loja:
            if "WHERE" in query:
                query += f"AND v.nome_loja = '{loja}'\n"
            else:
                query += f"WHERE v.nome_loja = '{loja}'\n"

        if categoria:
            if "WHERE" in query:
                query += f"AND cat.nome_categoria = '{categoria}'\n"
            else:
                query += f"WHERE cat.nome_categoria = '{categoria}'\n"

        return self.db.execute_select_all(query)
