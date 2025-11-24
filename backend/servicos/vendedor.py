from backend.servicos.database.conector import DatabaseManager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pytz import timezone

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
        meses = int(meses)
        data_inicio = (datetime.now() - timedelta(days=meses * 30)).strftime("%Y-%m-%d")

        query = """
            SELECT 
                COUNT(DISTINCT T1.cpf_cliente || '|' || T1.data_pedido) as total_vendas,
                COALESCE(SUM(T2.quantidade * T3.preco), 0) as receita_total,
                COALESCE(SUM(T2.quantidade), 0) as total_produtos_vendidos
            FROM pedido T1
            JOIN contemprod T2 ON T2.cpf_cliente = T1.cpf_cliente 
                AND T2.data_pedido = T1.data_pedido
            JOIN produto T3 ON T3.id_produto = T2.id_produto
            JOIN vendeprod T4 ON T4.id_produto = T3.id_produto
            WHERE T4.cpf_vendedor = %s
                AND T1.data_pedido >= %s
                AND T1.status_pedido != 'cancelado'
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

    def verificar_vendedor_existe(self, cpf: str):
        """Verifica se o vendedor existe na tabela"""
        query_vendedor = "SELECT cpf_vendedor FROM vendedor WHERE cpf_vendedor = %s"
        vendedor = self.db.execute_select_one(query_vendedor, (cpf,))
        return vendedor is not None

    def criar_vendedor(self, cpf: str, nome_loja: str, desc_loja: str = ""):
        """Cria um novo usuário e vendedor"""
        # Verifica se já existe usuário
        query_usuario = "SELECT cpf FROM usuario WHERE cpf = %s"
        usuario = self.db.execute_select_one(query_usuario, (cpf,))
        
        if not usuario:
            # Cria usuário com dados mínimos
            email = f"vendedor_{cpf}@ecommerce.local"
            senha_hash = "hash_padrao"  # Senha padrão para vendedores criados automaticamente
            pnome = "Vendedor"
            sobrenome = cpf[:4]  # Usa primeiros 4 dígitos do CPF como sobrenome
            
            insert_usuario = """
                INSERT INTO usuario (cpf, pnome, sobrenome, cep, email, senha_hash)
                VALUES (%s, %s, %s, NULL, %s, %s)
            """
            if not self.db.execute_statement(insert_usuario, (cpf, pnome, sobrenome, email, senha_hash)):
                print(f"Erro ao criar usuário para CPF: {cpf}")
                return False, "Erro ao criar usuário"
        
        # Verifica se já existe vendedor
        if self.verificar_vendedor_existe(cpf):
            return False, "Vendedor já existe com este CPF"
        
        # Cria vendedor
        insert_vendedor = """
            INSERT INTO vendedor (cpf_vendedor, nome_loja, desc_loja)
            VALUES (%s, %s, %s)
        """
        if not self.db.execute_statement(insert_vendedor, (cpf, nome_loja, desc_loja or "")):
            print(f"Erro ao criar vendedor para CPF: {cpf}")
            return False, "Erro ao criar vendedor"
        
        return True, "Vendedor criado com sucesso"

    def adicionar_produto(self, cpf_vendedor: str, nome: str, descricao: str, 
                         preco: float, estoque: int, alerta_estoque: int, origem: str = ""):
        """Adiciona novo produto à loja"""
        # Verifica se o vendedor existe, se não existir, cria automaticamente
        if not self.verificar_vendedor_existe(cpf_vendedor):
            # Cria vendedor com nome de loja padrão
            nome_loja = f"Loja {cpf_vendedor[:4]}"
            success, message = self.criar_vendedor(cpf_vendedor, nome_loja, f"Loja criada automaticamente para CPF {cpf_vendedor}")
            if not success:
                print(f"Erro ao criar vendedor automaticamente: {message}")
                return False
        
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

    def get_solicitacoes(self, cpf_vendedor: str):
        """Retorna todas as solicitações relacionadas aos produtos do vendedor"""
        query = """
            SELECT DISTINCT
                s.cpf_cliente,
                s.data_pedido,
                s.data_solicitacao,
                s.tipo,
                s.status_solicitacao,
                p.total_pedido,
                p.status_pedido,
                u.pnome || ' ' || u.sobrenome as nome_cliente
            FROM solicitacao s
            JOIN pedido p ON p.cpf_cliente = s.cpf_cliente 
                AND p.data_pedido = s.data_pedido
            JOIN contemprod cp ON cp.cpf_cliente = s.cpf_cliente 
                AND cp.data_pedido = s.data_pedido
            JOIN vendeprod vp ON vp.id_produto = cp.id_produto
            JOIN usuario u ON u.cpf = s.cpf_cliente
            WHERE vp.cpf_vendedor = %s
            ORDER BY s.data_solicitacao DESC
        """
        return self.db.execute_select_all(query, (cpf_vendedor,))

    def atualizar_status_solicitacao(self, cpf_vendedor: str, cpf_cliente: str, 
                                     data_pedido: str, data_solicitacao: str, 
                                     novo_status: str):
        """Atualiza o status de uma solicitação (aceitar/recusar)"""
        # Converte datas primeiro para usar na verificação
        # Converte data_solicitacao para datetime
        data_solicitacao_dt = None
        data_solicitacao_clean = data_solicitacao.strip()
        
        formatos = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%d %H:%M:%S.%f',
        ]
        
        for formato in formatos:
            try:
                data_solicitacao_dt = datetime.strptime(data_solicitacao_clean, formato)
                break
            except ValueError:
                continue
        
        if data_solicitacao_dt is None:
            try:
                data_solicitacao_clean = data_solicitacao_clean.replace('Z', '+00:00')
                data_solicitacao_dt = datetime.fromisoformat(data_solicitacao_clean)
            except:
                print(f"Erro ao converter data_solicitacao: {data_solicitacao}")
                return False
        
        # Converte data_pedido para datetime
        data_pedido_dt = None
        data_pedido_clean = data_pedido.strip()
        
        for formato in formatos:
            try:
                data_pedido_dt = datetime.strptime(data_pedido_clean, formato)
                break
            except ValueError:
                continue
        
        if data_pedido_dt is None:
            try:
                data_pedido_clean = data_pedido_clean.replace('Z', '+00:00')
                data_pedido_dt = datetime.fromisoformat(data_pedido_clean)
            except:
                print(f"Erro ao converter data_pedido: {data_pedido}")
                return False
        
        # Verifica se a solicitação está relacionada ao vendedor usando intervalo
        query_verifica = """
            SELECT 1
            FROM solicitacao s
            JOIN pedido p ON p.cpf_cliente = s.cpf_cliente 
                AND p.data_pedido >= %s - INTERVAL '1 second'
                AND p.data_pedido <= %s + INTERVAL '1 second'
            JOIN contemprod cp ON cp.cpf_cliente = s.cpf_cliente 
                AND cp.data_pedido >= %s - INTERVAL '1 second'
                AND cp.data_pedido <= %s + INTERVAL '1 second'
            JOIN vendeprod vp ON vp.id_produto = cp.id_produto
            WHERE vp.cpf_vendedor = %s
                AND s.cpf_cliente = %s
                AND s.data_solicitacao >= %s - INTERVAL '1 second'
                AND s.data_solicitacao <= %s + INTERVAL '1 second'
            LIMIT 1
        """
        
        if not self.db.execute_select_one(query_verifica, (data_pedido_dt, data_pedido_dt, data_pedido_dt, data_pedido_dt, cpf_vendedor, cpf_cliente, data_solicitacao_dt, data_solicitacao_dt)):
            return False
        
        # Valida o novo status
        if novo_status not in ['em_analise', 'concluida']:
            return False
        
        # Atualiza o status usando intervalo
        update = """
            UPDATE solicitacao
            SET status_solicitacao = %s
            WHERE cpf_cliente = %s
                AND data_pedido >= %s - INTERVAL '1 second'
                AND data_pedido <= %s + INTERVAL '1 second'
                AND data_solicitacao >= %s - INTERVAL '1 second'
                AND data_solicitacao <= %s + INTERVAL '1 second'
        """
        return self.db.execute_statement(update, (novo_status, cpf_cliente, data_pedido_dt, data_pedido_dt, data_solicitacao_dt, data_solicitacao_dt))

    def get_pedidos_aguardando_envio(self, cpf_vendedor: str):
        """Retorna todos os pedidos com status 'pagamento confirmado' aguardando envio"""
        query = """
            SELECT DISTINCT
                p.cpf_cliente,
                p.data_pedido,
                p.status_pedido,
                p.total_pedido,
                p.total_produtos,
                pg.metodo_pagamento,
                e.metodo_entrega,
                e.endereco_entrega,
                u.pnome || ' ' || u.sobrenome as nome_cliente
            FROM pedido p
            JOIN contemprod cp ON p.cpf_cliente = cp.cpf_cliente 
                AND cp.data_pedido >= p.data_pedido - INTERVAL '1 second'
                AND cp.data_pedido <= p.data_pedido + INTERVAL '1 second'
            JOIN vendeprod vp ON vp.id_produto = cp.id_produto
            LEFT JOIN pagamento pg ON pg.fk_cpf_cliente = p.cpf_cliente 
                AND pg.fk_data_pedido >= p.data_pedido - INTERVAL '1 second'
                AND pg.fk_data_pedido <= p.data_pedido + INTERVAL '1 second'
            LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente 
                AND e.fk_data_pedido >= p.data_pedido - INTERVAL '1 second'
                AND e.fk_data_pedido <= p.data_pedido + INTERVAL '1 second'
            JOIN usuario u ON u.cpf = p.cpf_cliente
            WHERE vp.cpf_vendedor = %s
                AND p.status_pedido = 'pagamento confirmado'
            ORDER BY p.data_pedido DESC
        """
        return self.db.execute_select_all(query, (cpf_vendedor,))

    def get_vendas_recentes(self, cpf_vendedor: str, limite: int = 5, status_filtro: str = ""):
        """Retorna as vendas mais recentes do vendedor (Atualizado com status_entrega)"""
        query = """
            SELECT DISTINCT
                p.data_pedido, 
                p.status_pedido, 
                p.cpf_cliente,
                p.total_pedido,
                prod.nome_produto,
                e.status_entrega
            FROM pedido p
            JOIN contemprod cp ON p.cpf_cliente = cp.cpf_cliente AND p.data_pedido = cp.data_pedido
            JOIN produto prod ON cp.id_produto = prod.id_produto
            JOIN vendeprod vp ON prod.id_produto = vp.id_produto
            LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente AND e.fk_data_pedido = p.data_pedido
            WHERE vp.cpf_vendedor = %s
        """
        
        params = [cpf_vendedor]

        if status_filtro:
            query += " AND p.status_pedido = %s"
            params.append(status_filtro)

        query += " ORDER BY p.data_pedido DESC LIMIT %s"
        params.append(limite)

        return self.db.execute_select_all(query, tuple(params))

    def atualizar_status_venda(self, cpf_cliente: str, data_pedido: str, novo_status: str):
        """Atualiza o status de uma venda (pedido)"""
        
        # Lógica de conversão de data (mesmo padrão usado em 'atualizar_status_solicitacao')
        data_pedido_dt = None
        data_pedido_clean = data_pedido.strip()
        
        formatos = [
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S.%f'
        ]
        
        try:
            for formato in formatos:
                try:
                    data_pedido_dt = datetime.strptime(data_pedido_clean, formato)
                    break
                except ValueError:
                    continue
            
            if data_pedido_dt is None:
                # Tenta ISO format tratando o 'Z'
                data_pedido_clean = data_pedido_clean.replace('Z', '+00:00')
                data_pedido_dt = datetime.fromisoformat(data_pedido_clean)
        except Exception as e:
            print(f"Erro ao converter data_pedido: {e}")
            return False

        # Query de atualização usando intervalo de tempo para precisão
        update = """
            UPDATE pedido 
            SET status_pedido = %s 
            WHERE cpf_cliente = %s 
            AND data_pedido >= %s - INTERVAL '1 second'
            AND data_pedido <= %s + INTERVAL '1 second'
        """
        return self.db.execute_statement(update, (novo_status, cpf_cliente, data_pedido_dt, data_pedido_dt))

    def enviar_pedido(self, cpf_vendedor: str, cpf_cliente: str, data_pedido: str):
        """Marca um pedido como enviado (muda de 'pagamento confirmado' para 'enviado')"""
        # Verifica se o pedido pertence ao vendedor
        query_verifica = """
            SELECT 1
            FROM pedido p
            JOIN contemprod cp ON cp.cpf_cliente = p.cpf_cliente 
                AND cp.data_pedido >= p.data_pedido - INTERVAL '1 second'
                AND cp.data_pedido <= p.data_pedido + INTERVAL '1 second'
            JOIN vendeprod vp ON vp.id_produto = cp.id_produto
            WHERE vp.cpf_vendedor = %s
                AND p.cpf_cliente = %s
                AND p.data_pedido >= %s - INTERVAL '1 second'
                AND p.data_pedido <= %s + INTERVAL '1 second'
                AND p.status_pedido = 'pagamento confirmado'
            LIMIT 1
        """
        
        # Converte data_pedido para datetime
        data_pedido_dt = None
        data_pedido_clean = data_pedido.strip()
        
        formatos = [
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S.%f'
        ]
        
        try:
            for formato in formatos:
                try:
                    data_pedido_dt = datetime.strptime(data_pedido_clean, formato)
                    break
                except ValueError:
                    continue
            
            if data_pedido_dt is None:
                data_pedido_clean = data_pedido_clean.replace('Z', '+00:00')
                data_pedido_dt = datetime.fromisoformat(data_pedido_clean)
        except Exception as e:
            print(f"Erro ao converter data_pedido: {e}")
            return False
        
        # Verifica se o pedido pertence ao vendedor
        if not self.db.execute_select_one(query_verifica, (cpf_vendedor, cpf_cliente, data_pedido_dt, data_pedido_dt)):
            print(f"Pedido não encontrado ou não pertence ao vendedor {cpf_vendedor}")
            return False
        
        # Busca informações do pedido para criar entrega
        query_pedido = """
            SELECT p.total_pedido, e.metodo_entrega, e.endereco_entrega
            FROM pedido p
            LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente 
                AND e.fk_data_pedido >= p.data_pedido - INTERVAL '1 second'
                AND e.fk_data_pedido <= p.data_pedido + INTERVAL '1 second'
            WHERE p.cpf_cliente = %s 
                AND p.data_pedido >= %s - INTERVAL '1 second'
                AND p.data_pedido <= %s + INTERVAL '1 second'
        """
        pedido_info = self.db.execute_select_one(query_pedido, (cpf_cliente, data_pedido_dt, data_pedido_dt))
        
        if not pedido_info:
            print(f"Pedido não encontrado para criar entrega")
            return False
        
        # Verifica se já existe entrega
        query_entrega_existe = """
            SELECT id_entrega FROM entrega
            WHERE fk_cpf_cliente = %s 
                AND fk_data_pedido >= %s - INTERVAL '1 second'
                AND fk_data_pedido <= %s + INTERVAL '1 second'
        """
        entrega_existente = self.db.execute_select_one(query_entrega_existe, (cpf_cliente, data_pedido_dt, data_pedido_dt))
        
        # Se não existe entrega, cria uma nova
        if not entrega_existente:
            metodo_entrega = pedido_info.get('metodo_entrega') or 'Correios'
            endereco_entrega = pedido_info.get('endereco_entrega') or 'Endereço não informado'
            data_envio = datetime.now(ZoneInfo("America/Sao_Paulo"))
            # Data prevista: 7 dias após envio
            data_prevista = data_envio + timedelta(days=7)
            
            insert_entrega = """
                INSERT INTO entrega (
                    status_entrega, metodo_entrega, endereco_entrega, 
                    data_envio, data_prevista, frete,
                    fk_cpf_cliente, fk_data_pedido, fk_cpf_vendedor
                )
                VALUES ('enviado', %s, %s, %s, %s, 0, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_entrega, (
                metodo_entrega, endereco_entrega, data_envio, data_prevista,
                cpf_cliente, data_pedido_dt, cpf_vendedor
            )):
                print(f"Erro ao criar entrega")
                return False
        else:
            # Atualiza entrega existente
            data_envio = datetime.now(ZoneInfo("America/Sao_Paulo"))
            data_prevista = data_envio + timedelta(days=7)
            
            update_entrega = """
                UPDATE entrega
                SET status_entrega = 'enviado',
                    data_envio = %s,
                    data_prevista = %s
                WHERE fk_cpf_cliente = %s 
                    AND fk_data_pedido >= %s - INTERVAL '1 second'
                    AND fk_data_pedido <= %s + INTERVAL '1 second'
            """
            if not self.db.execute_statement(update_entrega, (
                data_envio, data_prevista, cpf_cliente, data_pedido_dt, data_pedido_dt
            )):
                print(f"Erro ao atualizar entrega")
                return False
        
        # Atualiza status do pedido para 'enviado'
        update = """
            UPDATE pedido 
            SET status_pedido = 'enviado'
            WHERE cpf_cliente = %s 
                AND data_pedido >= %s - INTERVAL '1 second'
                AND data_pedido <= %s + INTERVAL '1 second'
                AND status_pedido = 'pagamento confirmado'
        """
        if not self.db.execute_statement(update, (cpf_cliente, data_pedido_dt, data_pedido_dt)):
            return False
        
        return True