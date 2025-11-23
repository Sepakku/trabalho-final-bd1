from backend.servicos.database.conector import DatabaseManager


class ProdutoCompradorDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    # Função para consultar os produtos com filtros de nome, origem, loja, categoria, intervalos de preço, bem avaliado
    def get_produto_comprador(self, nome: str, origem: str, loja: str, categoria: str, min_p: str, max_p: str, bem_avaliado: str):
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
        params = []

        if nome:
            where_clauses.append("p.nome_produto ILIKE %s")
            params.append(f"%{nome}%")

        if origem:
            where_clauses.append("LOWER(p.origem) = LOWER(%s)")
            params.append(origem)

        if loja:
            where_clauses.append("LOWER(v.nome_loja) = LOWER(%s)")
            params.append(loja)

        if categoria:
            where_clauses.append("LOWER(cat.nome_categoria) = LOWER(%s)")
            params.append(categoria)

        if min_p:
            try:
                min_preco = float(min_p)
                where_clauses.append("p.preco >= %s")
                params.append(min_preco)
            except ValueError:
                pass

        if max_p:
            try:
                max_preco = float(max_p)
                where_clauses.append("p.preco <= %s")
                params.append(max_preco)
            except ValueError:
                pass

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
            try:
                nota_min = float(bem_avaliado)
                query += "\nHAVING AVG(a.nota) >= %s"
                params.append(nota_min)
            except ValueError:
                pass

        return self.db.execute_select_all(query, tuple(params) if params else None)

    def get_categorias(self):
        """Retorna todas as categorias disponíveis"""
        query = """
            SELECT DISTINCT id_categoria, nome_categoria
            FROM categoria
            ORDER BY nome_categoria
        """
        return self.db.execute_select_all(query)
