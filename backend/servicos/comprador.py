from backend.servicos.database.conector import DatabaseManager
from datetime import datetime
from zoneinfo import ZoneInfo

class CompradorService:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    def adicionar_ao_carrinho(self, cpf: str, id_produto: int, quantidade: int):
        """Adiciona produto ao carrinho (cria pedido pendente se não existir)"""
        # Verifica se existe pedido pendente
        query_pedido = """
            SELECT cpf_cliente, data_pedido 
            FROM pedido 
            WHERE cpf_cliente = %s AND status_pedido = 'pendente'
            ORDER BY data_pedido DESC
            LIMIT 1
        """
        pedido = self.db.execute_select_one(query_pedido, (cpf,))
        
        if not pedido:
            # Cria novo pedido pendente
            data_pedido = datetime.now(ZoneInfo("America/Sao_Paulo"))
            insert_pedido = """
                INSERT INTO pedido (cpf_cliente, data_pedido, status_pedido, total_produtos, total_pedido)
                VALUES (%s, %s, 'pendente', 0, 0)
            """
            if not self.db.execute_statement(insert_pedido, (cpf, data_pedido)):
                return False
        else:
            data_pedido = pedido['data_pedido']
        
        # Verifica se produto já está no pedido
        query_item = """
            SELECT quantidade 
            FROM contemprod 
            WHERE cpf_cliente = %s AND data_pedido = %s AND id_produto = %s
        """
        item_existente = self.db.execute_select_one(query_item, (cpf, data_pedido, id_produto))
        
        # Busca preço do produto
        query_preco = "SELECT preco FROM produto WHERE id_produto = %s"
        produto = self.db.execute_select_one(query_preco, (id_produto,))
        if not produto:
            return False
        
        preco_unitario = float(produto['preco'])
        
        if item_existente:
            # Atualiza quantidade
            nova_quantidade = item_existente['quantidade'] + quantidade
            update_item = """
                UPDATE contemprod 
                SET quantidade = %s 
                WHERE cpf_cliente = %s AND data_pedido = %s AND id_produto = %s
            """
            if not self.db.execute_statement(update_item, (nova_quantidade, cpf, data_pedido, id_produto)):
                return False
        else:
            # Adiciona novo item
            insert_item = """
                INSERT INTO contemprod (cpf_cliente, data_pedido, id_produto, quantidade)
                VALUES (%s, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_item, (cpf, data_pedido, id_produto, quantidade)):
                return False
        
        # Atualiza totais do pedido
        self._atualizar_totais_pedido(cpf, data_pedido)
        return True

    def remover_do_carrinho(self, cpf: str, id_produto: int):
        """Remove item do carrinho (pedido pendente)"""
        # Busca pedido pendente
        query_pedido = """
            SELECT cpf_cliente, data_pedido 
            FROM pedido 
            WHERE cpf_cliente = %s AND status_pedido = 'pendente'
            ORDER BY data_pedido DESC
            LIMIT 1
        """
        pedido = self.db.execute_select_one(query_pedido, (cpf,))
        
        if not pedido:
            return False
        
        data_pedido = pedido['data_pedido']
        
        # Remove o item do pedido
        delete_item = """
            DELETE FROM contemprod 
            WHERE cpf_cliente = %s AND data_pedido = %s AND id_produto = %s
        """
        if not self.db.execute_statement(delete_item, (cpf, data_pedido, id_produto)):
            return False
        
        # Atualiza totais do pedido
        self._atualizar_totais_pedido(cpf, data_pedido)
        
        # Verifica se o pedido ficou vazio e remove se necessário
        query_itens = """
            SELECT COUNT(*) as total FROM contemprod
            WHERE cpf_cliente = %s AND data_pedido = %s
        """
        itens = self.db.execute_select_one(query_itens, (cpf, data_pedido))
        
        if itens and itens.get('total', 0) == 0:
            # Remove pedido vazio
            delete_pedido = """
                DELETE FROM pedido
                WHERE cpf_cliente = %s AND data_pedido = %s
            """
            self.db.execute_statement(delete_pedido, (cpf, data_pedido))
        
        return True

    def _atualizar_totais_pedido(self, cpf: str, data_pedido: datetime):
        """Atualiza total_produtos e total_pedido do pedido"""
        query = """
            SELECT SUM(cp.quantidade) as total_produtos,
                   SUM(cp.quantidade * p.preco) as total_pedido
            FROM contemprod cp
            JOIN produto p ON p.id_produto = cp.id_produto
            WHERE cp.cpf_cliente = %s AND cp.data_pedido = %s
        """
        totais = self.db.execute_select_one(query, (cpf, data_pedido))
        
        if totais:
            update = """
                UPDATE pedido 
                SET total_produtos = %s, total_pedido = %s
                WHERE cpf_cliente = %s AND data_pedido = %s
            """
            self.db.execute_statement(update, (
                int(totais['total_produtos'] or 0),
                float(totais['total_pedido'] or 0),
                cpf, data_pedido
            ))

    def get_pedidos(self, cpf: str):
        """Retorna todos os pedidos do comprador"""
        query = """
            SELECT 
                p.cpf_cliente,
                p.data_pedido,
                p.status_pedido,
                p.total_produtos,
                p.total_pedido,
                pg.status_pagamento,
                pg.metodo_pagamento,
                e.status_entrega,
                e.endereco_entrega
            FROM pedido p
            LEFT JOIN pagamento pg ON pg.fk_cpf_cliente = p.cpf_cliente 
                AND pg.fk_data_pedido = p.data_pedido
            LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente 
                AND e.fk_data_pedido = p.data_pedido
            WHERE p.cpf_cliente = %s
            ORDER BY p.data_pedido DESC
        """
        return self.db.execute_select_all(query, (cpf,))

    def get_pedido_detalhes(self, cpf: str, data_pedido: str):
        """Retorna detalhes completos de um pedido"""
        # Converte string para datetime
        data_pedido_dt = None
        
        # Remove espaços e caracteres especiais do início/fim
        data_pedido = data_pedido.strip()
        
        # Tenta vários formatos
        formatos = [
            '%Y-%m-%d %H:%M:%S',           # 2025-10-01 00:00:00
            '%Y-%m-%dT%H:%M:%S',           # 2025-10-01T00:00:00
            '%Y-%m-%dT%H:%M:%S.%f',        # 2025-10-01T00:00:00.000000
            '%Y-%m-%dT%H:%M:%S%z',         # 2025-10-01T00:00:00+00:00
            '%Y-%m-%dT%H:%M:%S.%f%z',      # 2025-10-01T00:00:00.000000+00:00
            '%Y-%m-%d %H:%M:%S.%f',        # 2025-10-01 00:00:00.000000
        ]
        
        try:
            # Primeiro tenta formatos conhecidos
            for formato in formatos:
                try:
                    data_pedido_dt = datetime.strptime(data_pedido, formato)
                    break
                except ValueError:
                    continue
            
            # Se não funcionou, tenta isoformat
            if data_pedido_dt is None:
                data_pedido_clean = data_pedido.replace('Z', '+00:00')
                if 'T' in data_pedido_clean or '+' in data_pedido_clean or '-' in data_pedido_clean[10:]:
                    data_pedido_dt = datetime.fromisoformat(data_pedido_clean)
            
            if data_pedido_dt is None:
                print(f"Erro: Não foi possível converter a data: {data_pedido}")
                print(f"Formatos tentados: {formatos}")
                return None
                
        except Exception as e:
            print(f"Erro ao converter data '{data_pedido}': {e}")
            return None
        
        # Usa comparação de intervalo para evitar problemas de precisão de tempo
        # Busca pedidos dentro de um intervalo de 1 segundo para garantir match
        query = """
            SELECT 
                p.cpf_cliente,
                p.data_pedido,
                p.status_pedido,
                p.total_produtos,
                p.total_pedido,
                pg.status_pagamento,
                pg.metodo_pagamento,
                pg.valor_pago,
                e.status_entrega,
                e.endereco_entrega,
                e.data_envio,
                e.data_prevista
            FROM pedido p
            LEFT JOIN pagamento pg ON pg.fk_cpf_cliente = p.cpf_cliente 
                AND pg.fk_data_pedido = p.data_pedido
            LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente 
                AND e.fk_data_pedido = p.data_pedido
            WHERE p.cpf_cliente = %s 
                AND p.data_pedido >= %s - INTERVAL '1 second'
                AND p.data_pedido <= %s + INTERVAL '1 second'
            ORDER BY p.data_pedido DESC
            LIMIT 1
        """
        pedido = self.db.execute_select_one(query, (cpf, data_pedido_dt, data_pedido_dt))
        
        if not pedido:
            print(f"Pedido não encontrado para CPF {cpf} e data {data_pedido_dt}")
            # Tenta buscar sem comparação exata, apenas pelo CPF e pedido mais recente pendente
            query_fallback = """
                SELECT 
                    p.cpf_cliente,
                    p.data_pedido,
                    p.status_pedido,
                    p.total_produtos,
                    p.total_pedido,
                    pg.status_pagamento,
                    pg.metodo_pagamento,
                    pg.valor_pago,
                    e.status_entrega,
                    e.endereco_entrega,
                    e.data_envio,
                    e.data_prevista
                FROM pedido p
                LEFT JOIN pagamento pg ON pg.fk_cpf_cliente = p.cpf_cliente 
                    AND pg.fk_data_pedido = p.data_pedido
                LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente 
                    AND e.fk_data_pedido = p.data_pedido
                WHERE p.cpf_cliente = %s 
                    AND p.status_pedido = 'pendente'
                ORDER BY p.data_pedido DESC
                LIMIT 1
            """
            pedido = self.db.execute_select_one(query_fallback, (cpf,))
        
        if pedido:
            # Busca itens do pedido usando a data do pedido encontrado
            data_pedido_encontrado = pedido['data_pedido']
            query_itens = """
                SELECT 
                    cp.id_produto,
                    cp.quantidade,
                    p.nome_produto,
                    p.preco as preco_unitario,
                    (cp.quantidade * p.preco) as subtotal
                FROM contemprod cp
                JOIN produto p ON p.id_produto = cp.id_produto
                WHERE cp.cpf_cliente = %s AND cp.data_pedido = %s
            """
            itens = self.db.execute_select_all(query_itens, (cpf, data_pedido_encontrado))
            pedido['itens'] = itens
        
        return pedido

    def finalizar_pedido(self, cpf: str, metodo_pagamento: str, endereco_entrega: str):
        """Finaliza pedido criando pagamento e entrega"""
        # Busca pedido pendente
        query_pedido = """
            SELECT cpf_cliente, data_pedido, total_pedido, total_produtos
            FROM pedido 
            WHERE cpf_cliente = %s AND status_pedido = 'pendente'
            ORDER BY data_pedido DESC
            LIMIT 1
        """
        pedido = self.db.execute_select_one(query_pedido, (cpf,))
        
        if not pedido:
            print(f"Pedido pendente não encontrado para CPF: {cpf}")
            return False
        
        data_pedido = pedido['data_pedido']
        total_pedido = float(pedido['total_pedido'] or 0)
        total_produtos = int(pedido.get('total_produtos', 0) or 0)
        
        # Verifica se o pedido tem produtos
        if total_produtos == 0 or total_pedido == 0:
            print(f"Pedido vazio para CPF: {cpf}, data: {data_pedido}")
            return False
        
        # Busca vendedor do primeiro produto (simplificado - pode ter múltiplos vendedores)
        query_vendedor = """
            SELECT DISTINCT vp.cpf_vendedor
            FROM contemprod cp
            JOIN vendeprod vp ON vp.id_produto = cp.id_produto
            WHERE cp.cpf_cliente = %s AND cp.data_pedido = %s
            LIMIT 1
        """
        vendedor = self.db.execute_select_one(query_vendedor, (cpf, data_pedido))
        
        if not vendedor:
            print(f"Vendedor não encontrado para o pedido do CPF: {cpf}, data: {data_pedido}")
            # Tenta verificar se há produtos no pedido
            query_produtos = """
                SELECT COUNT(*) as total
                FROM contemprod
                WHERE cpf_cliente = %s AND data_pedido = %s
            """
            produtos_count = self.db.execute_select_one(query_produtos, (cpf, data_pedido))
            print(f"Total de produtos no pedido: {produtos_count}")
            return False
        
        cpf_vendedor = vendedor['cpf_vendedor']
        
        # Verifica se já existe pagamento para este pedido
        query_pagamento_existe = """
            SELECT id_pagamento FROM pagamento
            WHERE fk_cpf_cliente = %s AND fk_data_pedido = %s
        """
        pagamento_existente = self.db.execute_select_one(query_pagamento_existe, (cpf, data_pedido))
        
        if not pagamento_existente:
            # Cria pagamento
            insert_pagamento = """
                INSERT INTO pagamento (
                    status_pagamento, valor_pago, metodo_pagamento, num_parcelas,
                    fk_cpf_vendedor, fk_cpf_cliente, fk_data_pedido
                )
                VALUES ('pendente', %s, %s, 1, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_pagamento, (
                total_pedido, metodo_pagamento, cpf_vendedor, cpf, data_pedido
            )):
                print(f"Erro ao criar pagamento para CPF: {cpf}")
                return False
        else:
            # Atualiza pagamento existente
            update_pagamento = """
                UPDATE pagamento
                SET metodo_pagamento = %s,
                    valor_pago = %s
                WHERE fk_cpf_cliente = %s AND fk_data_pedido = %s
            """
            if not self.db.execute_statement(update_pagamento, (
                metodo_pagamento, total_pedido, cpf, data_pedido
            )):
                print(f"Erro ao atualizar pagamento para CPF: {cpf}")
                return False
        
        # Verifica se já existe entrega para este pedido
        query_entrega_existe = """
            SELECT id_entrega FROM entrega
            WHERE fk_cpf_cliente = %s AND fk_data_pedido = %s
        """
        entrega_existente = self.db.execute_select_one(query_entrega_existe, (cpf, data_pedido))
        
        if not entrega_existente:
            # Cria entrega
            insert_entrega = """
                INSERT INTO entrega (
                    status_entrega, endereco_entrega, fk_cpf_cliente, fk_data_pedido, fk_cpf_vendedor
                )
                VALUES ('preparando', %s, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_entrega, (
                endereco_entrega, cpf, data_pedido, cpf_vendedor
            )):
                print(f"Erro ao criar entrega para CPF: {cpf}")
                return False
        else:
            # Atualiza entrega existente
            update_entrega = """
                UPDATE entrega
                SET status_entrega = 'preparando',
                    endereco_entrega = %s
                WHERE fk_cpf_cliente = %s AND fk_data_pedido = %s
            """
            if not self.db.execute_statement(update_entrega, (
                endereco_entrega, cpf, data_pedido
            )):
                print(f"Erro ao atualizar entrega para CPF: {cpf}")
                return False
        
        # Atualiza o status do pedido de 'pendente' para 'enviado'
        # Isso garante que um novo carrinho (pedido pendente) possa ser criado
        update_pedido = """
            UPDATE pedido 
            SET status_pedido = 'enviado'
            WHERE cpf_cliente = %s AND data_pedido = %s
        """
        if not self.db.execute_statement(update_pedido, (cpf, data_pedido)):
            print(f"Erro ao atualizar status do pedido para CPF: {cpf}")
            return False
        
        print(f"Pedido finalizado com sucesso para CPF: {cpf}, data: {data_pedido}")
        print(f"Status alterado para 'enviado' - pedido finalizado")
        return True

    def simular_pagamento(self, cpf: str, data_pedido: str):
        """Simula pagamento de um pedido, atualizando status de 'pendente' para 'aprovado'"""
        # Converte string para datetime
        data_pedido_dt = None
        
        # Remove espaços e caracteres especiais do início/fim
        data_pedido = data_pedido.strip()
        
        # Tenta vários formatos
        formatos = [
            '%Y-%m-%d %H:%M:%S',           # 2025-10-01 00:00:00
            '%Y-%m-%dT%H:%M:%S',           # 2025-10-01T00:00:00
            '%Y-%m-%dT%H:%M:%S.%f',        # 2025-10-01T00:00:00.000000
            '%Y-%m-%dT%H:%M:%S%z',         # 2025-10-01T00:00:00+00:00
            '%Y-%m-%dT%H:%M:%S.%f%z',      # 2025-10-01T00:00:00.000000+00:00
            '%Y-%m-%d %H:%M:%S.%f',        # 2025-10-01 00:00:00.000000
        ]
        
        try:
            # Primeiro tenta formatos conhecidos
            for formato in formatos:
                try:
                    data_pedido_dt = datetime.strptime(data_pedido, formato)
                    break
                except ValueError:
                    continue
            
            # Se não funcionou, tenta isoformat
            if data_pedido_dt is None:
                data_pedido_clean = data_pedido.replace('Z', '+00:00')
                if 'T' in data_pedido_clean or '+' in data_pedido_clean or '-' in data_pedido_clean[10:]:
                    data_pedido_dt = datetime.fromisoformat(data_pedido_clean)
            
            if data_pedido_dt is None:
                print(f"Erro: Não foi possível converter a data: {data_pedido}")
                return False
                
        except Exception as e:
            print(f"Erro ao converter data '{data_pedido}': {e}")
            return False
        
        # Verifica se existe pagamento para este pedido usando intervalo de tempo
        # (evita problemas de precisão de timestamp)
        query_pagamento = """
            SELECT id_pagamento, status_pagamento, metodo_pagamento, fk_data_pedido
            FROM pagamento
            WHERE fk_cpf_cliente = %s 
                AND fk_data_pedido >= %s - INTERVAL '1 second'
                AND fk_data_pedido <= %s + INTERVAL '1 second'
            ORDER BY fk_data_pedido DESC
            LIMIT 1
        """
        pagamento = self.db.execute_select_one(query_pagamento, (cpf, data_pedido_dt, data_pedido_dt))
        
        if not pagamento:
            # Tenta buscar pedido primeiro para verificar se existe
            query_pedido = """
                SELECT data_pedido, total_pedido, metodo_pagamento
                FROM pedido p
                LEFT JOIN pagamento pg ON pg.fk_cpf_cliente = p.cpf_cliente 
                    AND pg.fk_data_pedido >= p.data_pedido - INTERVAL '1 second'
                    AND pg.fk_data_pedido <= p.data_pedido + INTERVAL '1 second'
                WHERE p.cpf_cliente = %s 
                    AND p.data_pedido >= %s - INTERVAL '1 second'
                    AND p.data_pedido <= %s + INTERVAL '1 second'
                LIMIT 1
            """
            pedido = self.db.execute_select_one(query_pedido, (cpf, data_pedido_dt, data_pedido_dt))
            
            if not pedido:
                print(f"Pedido não encontrado para CPF {cpf} e data {data_pedido_dt}")
                return False
            
            print(f"Pedido encontrado, mas pagamento não existe para CPF {cpf} e data {pedido['data_pedido']}")
            # Se o pedido existe mas não tem pagamento, cria um pagamento pendente automaticamente
            # Busca vendedor para criar o pagamento
            query_vendedor = """
                SELECT DISTINCT vp.cpf_vendedor
                FROM contemprod cp
                JOIN vendeprod vp ON vp.id_produto = cp.id_produto
                WHERE cp.cpf_cliente = %s AND cp.data_pedido >= %s - INTERVAL '1 second'
                    AND cp.data_pedido <= %s + INTERVAL '1 second'
                LIMIT 1
            """
            vendedor = self.db.execute_select_one(query_vendedor, (cpf, data_pedido_dt, data_pedido_dt))
            
            if not vendedor:
                print(f"Vendedor não encontrado para o pedido do CPF: {cpf}")
                return False
            
            # Cria pagamento pendente automaticamente
            data_pedido_real = pedido['data_pedido']
            total_pedido = float(pedido['total_pedido'] or 0)
            metodo_pagamento = pedido.get('metodo_pagamento') or 'credito'  # Default se não tiver método
            
            insert_pagamento = """
                INSERT INTO pagamento (
                    status_pagamento, valor_pago, metodo_pagamento, num_parcelas,
                    fk_cpf_vendedor, fk_cpf_cliente, fk_data_pedido
                )
                VALUES ('pendente', %s, %s, 1, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_pagamento, (
                total_pedido, metodo_pagamento, vendedor['cpf_vendedor'], cpf, data_pedido_real
            )):
                print(f"Erro ao criar pagamento para CPF: {cpf}")
                return False
            
            print(f"Pagamento criado automaticamente para CPF: {cpf}, data: {data_pedido_real}")
            # Busca o pagamento recém-criado
            pagamento = self.db.execute_select_one(query_pagamento, (cpf, data_pedido_real, data_pedido_real))
            if not pagamento:
                print(f"Erro: Pagamento não encontrado após criação")
                return False
            # Atualiza data_pedido_dt para usar a data real do pedido
            data_pedido_dt = data_pedido_real
        
        # Verifica se o pagamento já está aprovado
        if pagamento['status_pagamento'] == 'aprovado':
            print(f"Pagamento já está aprovado para CPF {cpf} e data {pagamento.get('fk_data_pedido', data_pedido_dt)}")
            return True
        
        # Usa a data real do pagamento encontrado
        data_pedido_pagamento = pagamento.get('fk_data_pedido', data_pedido_dt)
        
        # Atualiza status do pagamento para 'aprovado' usando intervalo de tempo
        update_pagamento = """
            UPDATE pagamento
            SET status_pagamento = 'aprovado'
            WHERE fk_cpf_cliente = %s 
                AND fk_data_pedido >= %s - INTERVAL '1 second'
                AND fk_data_pedido <= %s + INTERVAL '1 second'
        """
        if not self.db.execute_statement(update_pagamento, (cpf, data_pedido_pagamento, data_pedido_pagamento)):
            print(f"Erro ao atualizar pagamento para CPF: {cpf}")
            return False
        
        print(f"Pagamento simulado com sucesso para CPF: {cpf}, data: {data_pedido_dt}")
        print(f"Método de pagamento: {pagamento['metodo_pagamento']}")
        return True

    def criar_solicitacao(self, cpf: str, data_pedido: str, tipo: str):
        """Cria solicitação sobre um pedido"""
        try:
            # Tenta vários formatos
            data_pedido = data_pedido.replace('Z', '+00:00')
            if 'T' in data_pedido:
                data_pedido_dt = datetime.fromisoformat(data_pedido)
            else:
                # Formato apenas data/hora sem timezone
                data_pedido_dt = datetime.strptime(data_pedido, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Erro ao converter data: {e}")
            return False
        
        data_solicitacao = datetime.now(ZoneInfo("America/Sao_Paulo"))
        status_solicitacao = 'aberta'
        
        query = """
            INSERT INTO solicitacao (cpf_cliente, data_pedido, data_solicitacao, tipo, status_solicitacao)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_statement(query, (
            cpf, data_pedido_dt, data_solicitacao, tipo, status_solicitacao
        ))

    def avaliar_produto(self, cpf: str, id_produto: int, nota: int, comentario: str = ""):
        """Avalia ou atualiza avaliação de um produto"""
        if nota < 1 or nota > 5:
            return False
        
        # Verifica se já existe avaliação
        query_existe = """
            SELECT 1 FROM avaliaprod 
            WHERE cpf_comprador = %s AND id_produto = %s
        """
        existe = self.db.execute_select_one(query_existe, (cpf, id_produto))
        
        if existe:
            # Atualiza avaliação existente
            query = """
                UPDATE avaliaprod 
                SET nota = %s 
                WHERE cpf_comprador = %s AND id_produto = %s
            """
            return self.db.execute_statement(query, (nota, cpf, id_produto))
        else:
            # Cria nova avaliação
            query = """
                INSERT INTO avaliaprod (cpf_comprador, id_produto, nota)
                VALUES (%s, %s, %s)
            """
            return self.db.execute_statement(query, (cpf, id_produto, nota))
