from backend.servicos.database.conector import DatabaseManager


class ProdutoDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    # Função para consultar os produtos com filtros de nome, origem, loja, categoria, intervalos de preço, bem avaliado
    def get_produto(self, nome: str, origem: str, loja: str, categoria: str, min_p: str, max_p: str, bem_avaliado: str):
        query = """
                SELECT 
                    p.alerta_estoque, 
                    p.desc_produto, p.estoque_atual, 
                    p.id_produto, 
                    cat.nome_categoria, 
                    v.nome_loja, 
                    p.nome_produto, 
                    p.origem, 
                    p.preco,
                    ROUND(AVG(a.nota), 2) AS media_nota
                FROM produto p
                LEFT JOIN vendeprod vp ON vp.id_produto = p.id_produto
                LEFT JOIN pertencecat pc ON pc.id_produto = p.id_produto
                LEFT JOIN categoria cat ON cat.id_categoria = pc.id_categoria
                LEFT JOIN vendedor v ON v.cpf_vendedor = vp.cpf_vendedor
                LEFT JOIN avaliaprod a ON a.id_produto = p.id_produto
                """

        where_clauses = []

        if nome:
            where_clauses.append(f"p.nome_produto LIKE '%{nome}%'")

        if origem:
            where_clauses.append(f"p.origem = '{origem}'")

        if loja:
            where_clauses.append(f"v.nome_loja = '{loja}'")

        if categoria:
            where_clauses.append(f"cat.nome_categoria = '{categoria}'")

        if min_p:
            where_clauses.append(f"p.preco >= {min_p}")

        if max_p:
            where_clauses.append(f"p.preco <= {max_p}")

        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + "\n"

        query += """
                GROUP BY
                    p.alerta_estoque, 
                    p.desc_produto, p.estoque_atual, 
                    p.id_produto, 
                    cat.nome_categoria, 
                    v.nome_loja, 
                    p.nome_produto, 
                    p.origem, 
                    p.preco
                """

        if bem_avaliado:
            query += f"\nHAVING AVG(a.nota) >= {bem_avaliado}"

        return self.db.execute_select_all(query)
