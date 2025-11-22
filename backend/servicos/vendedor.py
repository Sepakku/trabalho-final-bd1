from backend.servicos.database.conector import DatabaseManager
from datetime import datetime, timedelta

class VendedorService:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    def get_vendedor(self, cpf: str):
        """Retorna informações do vendedor"""
        query = """
            SELECT u.cpf, u.pnome, u.sobrenome, u.email, u.cep,
                   v.nome_loja, v.desc_loja
            FROM usuario u
            JOIN vendedor v ON v.cpf_vendedor = u.cpf
            WHERE u.cpf = %s
        """
        return self.db.execute_select_one(query, (cpf,))

    def get_produtos_mais_vendidos(self, cpf_vendedor: str, meses: int = 1):
        """Retorna os 3 produtos mais vendidos no período"""
        data_inicio = datetime.now() - timedelta(days=meses * 30)
        
        query = """
            SELECT 
                p.id_produto,
                p.nome_produto,
                p.preco,
                SUM(cp.quantidade) as total_vendido
            FROM produto p
            JOIN vendeprod vp ON vp.id_produto = p.id_produto
            JOIN contemprod cp ON cp.id_produto = p.id_produto
            JOIN pedido ped ON ped.cpf_cliente = cp.cpf_cliente 
                AND ped.data_pedido = cp.data_pedido
            WHERE vp.cpf_vendedor = %s
                AND ped.data_pedido >= %s
                AND ped.status_pedido != 'cancelado'
            GROUP BY p.id_produto, p.nome_produto, p.preco
            ORDER BY total_vendido DESC
            LIMIT 3
        """
        return self.db.execute_select_all(query, (cpf_vendedor, data_inicio))

    def get_lucro_total(self, cpf_vendedor: str, meses: int = 1):
        """Retorna lucro total no período"""
        data_inicio = datetime.now() - timedelta(days=meses * 30)
        
        query = """
            SELECT 
                COUNT(DISTINCT ped.cpf_cliente || ped.data_pedido) as total_vendas,
                SUM(cp.quantidade * p.preco) as receita_total,
                SUM(cp.quantidade) as total_produtos_vendidos
            FROM produto p
            JOIN vendeprod vp ON vp.id_produto = p.id_produto
            JOIN contemprod cp ON cp.id_produto = p.id_produto
            JOIN pedido ped ON ped.cpf_cliente = cp.cpf_cliente 
                AND ped.data_pedido = cp.data_pedido
            WHERE vp.cpf_vendedor = %s
                AND ped.data_pedido >= %s
                AND ped.status_pedido != 'cancelado'
        """
        return self.db.execute_select_one(query, (cpf_vendedor, data_inicio))

    def get_produtos_estoque_baixo(self, cpf_vendedor: str):
        """Retorna produtos com estoque abaixo do alerta"""
        query = """
            SELECT 
                p.id_produto,
                p.nome_produto,
                p.estoque_atual,
                p.alerta_estoque,
                p.preco
            FROM produto p
            JOIN vendeprod vp ON vp.id_produto = p.id_produto
            WHERE vp.cpf_vendedor = %s
                AND p.estoque_atual <= p.alerta_estoque
            ORDER BY p.estoque_atual ASC
        """
        return self.db.execute_select_all(query, (cpf_vendedor,))

    def get_produtos_vendedor(self, cpf_vendedor: str):
        """Retorna todos os produtos do vendedor"""
        query = """
            SELECT 
                p.id_produto,
                p.nome_produto,
                p.desc_produto,
                p.preco,
                p.estoque_atual,
                p.alerta_estoque,
                p.origem,
                COALESCE(AVG(a.nota), 0) as media_avaliacao
            FROM produto p
            JOIN vendeprod vp ON vp.id_produto = p.id_produto
            LEFT JOIN avaliaprod a ON a.id_produto = p.id_produto
            WHERE vp.cpf_vendedor = %s
            GROUP BY p.id_produto, p.nome_produto, p.desc_produto, 
                     p.preco, p.estoque_atual, p.alerta_estoque, p.origem
            ORDER BY p.id_produto
        """
        return self.db.execute_select_all(query, (cpf_vendedor,))

    def adicionar_produto(self, cpf_vendedor: str, nome: str, descricao: str, 
                         preco: float, estoque: int, alerta_estoque: int, origem: str = ""):
        """Adiciona novo produto à loja"""
        # Insere produto
        insert_produto = """
            INSERT INTO produto (nome_produto, desc_produto, preco, estoque_atual, 
                               alerta_estoque, origem)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_produto
        """
        id_produto = self.db.execute_statement_returning(
            insert_produto, (nome, descricao, preco, estoque, alerta_estoque, origem)
        )
        
        if not id_produto:
            return False
        
        # Associa produto ao vendedor
        insert_vende = """
            INSERT INTO vendeprod (cpf_vendedor, id_produto)
            VALUES (%s, %s)
        """
        return self.db.execute_statement(insert_vende, (cpf_vendedor, id_produto))

    def atualizar_estoque(self, cpf_vendedor: str, id_produto: int, nova_quantidade: int):
        """Atualiza quantidade em estoque de um produto"""
        # Verifica se o produto pertence ao vendedor
        query_verifica = """
            SELECT 1 FROM vendeprod 
            WHERE cpf_vendedor = %s AND id_produto = %s
        """
        if not self.db.execute_select_one(query_verifica, (cpf_vendedor, id_produto)):
            return False
        
        update = """
            UPDATE produto 
            SET estoque_atual = %s
            WHERE id_produto = %s
        """
        return self.db.execute_statement(update, (nova_quantidade, id_produto))

    def remover_produto(self, cpf_vendedor: str, id_produto: int):
        """Remove produto da loja (remove associação)"""
        # Verifica se o produto pertence ao vendedor
        query_verifica = """
            SELECT 1 FROM vendeprod 
            WHERE cpf_vendedor = %s AND id_produto = %s
        """
        if not self.db.execute_select_one(query_verifica, (cpf_vendedor, id_produto)):
            return False
        
        delete = """
            DELETE FROM vendeprod 
            WHERE cpf_vendedor = %s AND id_produto = %s
        """
        return self.db.execute_statement(delete, (cpf_vendedor, id_produto))

    def get_produtos_mais_devolvidos(self, cpf_vendedor: str, meses: int = 1):
        """Retorna produtos com mais devoluções no período"""
        data_inicio = datetime.now() - timedelta(days=meses * 30)
        
        query = """
            SELECT 
                p.id_produto,
                p.nome_produto,
                COUNT(DISTINCT s.cpf_cliente || s.data_pedido || s.data_solicitacao) as total_devolucoes
            FROM produto p
            JOIN vendeprod vp ON vp.id_produto = p.id_produto
            JOIN associaprod ap ON ap.id_produto = p.id_produto
            JOIN solicitacao s ON s.cpf_cliente = ap.cpf_cliente 
                AND s.data_pedido = ap.data_pedido 
                AND s.data_solicitacao = ap.data_solicitacao
            WHERE vp.cpf_vendedor = %s
                AND s.tipo = 'devolucao'
                AND s.data_solicitacao >= %s
            GROUP BY p.id_produto, p.nome_produto
            ORDER BY total_devolucoes DESC
        """
        return self.db.execute_select_all(query, (cpf_vendedor, data_inicio))

    def get_produtos_melhor_avaliacao(self, cpf_vendedor: str):
        """Retorna produtos com melhor avaliação"""
        query = """
            SELECT 
                p.id_produto,
                p.nome_produto,
                p.preco,
                AVG(a.nota) as media_avaliacao,
                COUNT(a.nota) as total_avaliacoes
            FROM produto p
            JOIN vendeprod vp ON vp.id_produto = p.id_produto
            LEFT JOIN avaliaprod a ON a.id_produto = p.id_produto
            WHERE vp.cpf_vendedor = %s
            GROUP BY p.id_produto, p.nome_produto, p.preco
            HAVING COUNT(a.nota) > 0
            ORDER BY media_avaliacao DESC, total_avaliacoes DESC
        """
        return self.db.execute_select_all(query, (cpf_vendedor,))

    def atualizar_produto(self, cpf_vendedor: str, id_produto: int, nome: str = None,
                         descricao: str = None, preco: float = None, origem: str = None,
                         alerta_estoque: int = None):
        """Atualiza informações de um produto"""
        # Verifica se o produto pertence ao vendedor
        query_verifica = """
            SELECT 1 FROM vendeprod 
            WHERE cpf_vendedor = %s AND id_produto = %s
        """
        if not self.db.execute_select_one(query_verifica, (cpf_vendedor, id_produto)):
            return False
        
        campos = []
        valores = []
        
        if nome:
            campos.append("nome_produto = %s")
            valores.append(nome)
        if descricao:
            campos.append("desc_produto = %s")
            valores.append(descricao)
        if preco:
            campos.append("preco = %s")
            valores.append(preco)
        if origem:
            campos.append("origem = %s")
            valores.append(origem)
        if alerta_estoque is not None:
            campos.append("alerta_estoque = %s")
            valores.append(alerta_estoque)
        
        if not campos:
            return False
        
        valores.append(id_produto)
        update = f"""
            UPDATE produto 
            SET {', '.join(campos)}
            WHERE id_produto = %s
        """
        return self.db.execute_statement(update, tuple(valores))
