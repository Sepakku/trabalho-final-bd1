from backend.servicos.database.conector import DatabaseManager
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

class CompradorService:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider
    
    def verificar_comprador_existe(self, cpf: str):
        """Verifica se o comprador existe na tabela"""
        query_comprador = "SELECT cpf_comprador FROM comprador WHERE cpf_comprador = %s"
        comprador = self.db.execute_select_one(query_comprador, (cpf,))
        return comprador is not None

    def verificar_usuario_existe(self, cpf: str):
        """Verifica se o usuário existe na tabela usuario"""
        query_usuario = "SELECT cpf FROM usuario WHERE cpf = %s"
        usuario = self.db.execute_select_one(query_usuario, (cpf,))
        return usuario is not None
    
    def obter_dados_usuario(self, cpf: str):
        """Obtém os dados do usuário da tabela usuario"""
        query_usuario = "SELECT cpf, pnome, sobrenome, cep, email FROM usuario WHERE cpf = %s"
        return self.db.execute_select_one(query_usuario, (cpf,))
    
    def criar_comprador(self, cpf: str, pnome: str = None, sobrenome: str = None, cep: str = None, email: str = None, senha_hash: str = None):
        """Cria um novo usuário e comprador, ou apenas comprador se usuário já existir"""
        # Verifica se já existe comprador
        if self.verificar_comprador_existe(cpf):
            return False, "Comprador já existe com este CPF"
        
        # Verifica se já existe usuário
        usuario_existente = self.obter_dados_usuario(cpf)
        
        if usuario_existente:
            # Usuário já existe, apenas cria o comprador usando dados existentes
            insert_comprador = """
                INSERT INTO comprador (cpf_comprador, num_compras)
                VALUES (%s, 0)
            """
            if not self.db.execute_statement(insert_comprador, (cpf,)):
                return False, "Erro ao criar comprador"
            return True, "Comprador criado com sucesso (usando dados do usuário existente)"
        else:
            # Usuário não existe, precisa criar usuário e comprador
            if not all([pnome, sobrenome, email, senha_hash]):
                return False, "Para criar novo usuário, são necessários: pnome, sobrenome, email e senha"
            
            # Cria usuário
            insert_usuario = """
                INSERT INTO usuario (cpf, pnome, sobrenome, cep, email, senha_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_usuario, (cpf, pnome, sobrenome, cep or None, email, senha_hash)):
                return False, "Erro ao criar usuário"
            
            # Cria comprador
            insert_comprador = """
                INSERT INTO comprador (cpf_comprador, num_compras)
                VALUES (%s, 0)
            """
            if not self.db.execute_statement(insert_comprador, (cpf,)):
                return False, "Erro ao criar comprador"
            
            return True, "Comprador criado com sucesso"

    def adicionar_ao_carrinho(self, cpf: str, id_produto: int, quantidade: int):
        """
        Adiciona produto ao carrinho/pedido.
        Reutiliza o pedido 'pendente' mais recente e atualiza sua data com fuso horário.
        """
        if not self.verificar_comprador_existe(cpf):
            return None # Comprador não existe

        # 1. Tenta encontrar o carrinho (pedido com status 'pendente') mais recente
        query_carrinho_pendente = """
            SELECT data_pedido
            FROM pedido
            WHERE cpf_cliente = %s AND status_pedido = 'pendente'
            ORDER BY data_pedido DESC
            LIMIT 1
        """
        carrinho_existente = self.db.execute_select_one(query_carrinho_pendente, (cpf,))
        
        # Define a data_pedido a ser usada: AGORA COM FUSO HORÁRIO
        # Isso utiliza o pacote 'tzdata' que você instalou.
        data_hora_atual = datetime.now(ZoneInfo("America/Sao_Paulo")) 

        if carrinho_existente:
            # Carrinho existe: Reutilizamos a data_pedido existente
            data_pedido_original = carrinho_existente['data_pedido']
            
            # ATUALIZA A DATA DO PEDIDO EXISTENTE para a hora atual com fuso horário
            update_pedido_data = """
                UPDATE pedido
                SET data_pedido = %s
                WHERE cpf_cliente = %s
                AND data_pedido = %s
            """
            # O ON UPDATE CASCADE na ContemProd garantirá que esta data seja propagada
            if not self.db.execute_statement(update_pedido_data, (data_hora_atual, cpf, data_pedido_original)):
                 return False

            # 2. Verifica se o produto já está no carrinho
            # Usamos a NOVA data (data_hora_atual) para buscar, devido ao CASCADE
            query_contem = """
                SELECT quantidade 
                FROM contemprod 
                WHERE cpf_cliente = %s AND data_pedido = %s AND id_produto = %s
            """
            item_existente = self.db.execute_select_one(query_contem, (cpf, data_hora_atual, id_produto))

            if item_existente:
                # Produto existe: Apenas atualiza a quantidade
                nova_quantidade = item_existente['quantidade'] + quantidade
                update_contem = """
                    UPDATE contemprod 
                    SET quantidade = %s
                    WHERE cpf_cliente = %s AND data_pedido = %s AND id_produto = %s
                """
                if not self.db.execute_statement(update_contem, (nova_quantidade, cpf, data_hora_atual, id_produto)):
                    return False
            else:
                # Produto não existe: Adiciona o item ao pedido existente
                insert_contem = """
                    INSERT INTO contemprod (cpf_cliente, data_pedido, id_produto, quantidade)
                    VALUES (%s, %s, %s, %s)
                """
                if not self.db.execute_statement(insert_contem, (cpf, data_hora_atual, id_produto, quantidade)):
                    return False
            
            # Atualiza totais do pedido
            self._atualizar_totais_pedido(cpf, data_hora_atual)
            return True
            
        else:
            # Carrinho não existe: Cria um novo pedido com status 'pendente'
            insert_pedido = """
                INSERT INTO pedido (cpf_cliente, data_pedido, status_pedido, total_pedido)
                VALUES (%s, %s, 'pendente', 0) 
                RETURNING data_pedido
            """
            # A data usada é a data_hora_atual (com fuso)
            data_criada = self.db.execute_select_one(insert_pedido, (cpf, data_hora_atual))
            
            if data_criada:
                # Adiciona o item
                insert_contem = """
                    INSERT INTO contemprod (cpf_cliente, data_pedido, id_produto, quantidade)
                    VALUES (%s, %s, %s, %s)
                """
                if not self.db.execute_statement(insert_contem, (cpf, data_criada['data_pedido'], id_produto, quantidade)):
                    return False
                
                # Atualiza totais do pedido
                self._atualizar_totais_pedido(cpf, data_criada['data_pedido'])
                return True
            
            return False

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
        # Usa intervalo de tempo para garantir que encontre o pedido mesmo com pequenas diferenças de timestamp
        query = """
            SELECT 
                COALESCE(SUM(cp.quantidade), 0) as total_produtos,
                COALESCE(SUM(cp.quantidade * p.preco), 0) as total_pedido
            FROM contemprod cp
            INNER JOIN produto p ON p.id_produto = cp.id_produto
            WHERE cp.cpf_cliente = %s 
                AND cp.data_pedido >= %s - INTERVAL '1 second'
                AND cp.data_pedido <= %s + INTERVAL '1 second'
        """
        totais = self.db.execute_select_one(query, (cpf, data_pedido, data_pedido))
        
        if totais:
            total_produtos = int(totais.get('total_produtos', 0) or 0)
            total_pedido = float(totais.get('total_pedido', 0) or 0)
            
            # Busca o data_pedido exato do banco para garantir que o UPDATE funcione
            query_pedido_exato = """
                SELECT data_pedido
                FROM pedido
                WHERE cpf_cliente = %s
                    AND data_pedido >= %s - INTERVAL '1 second'
                    AND data_pedido <= %s + INTERVAL '1 second'
                LIMIT 1
            """
            pedido_exato = self.db.execute_select_one(query_pedido_exato, (cpf, data_pedido, data_pedido))
            
            if pedido_exato:
                data_pedido_exata = pedido_exato['data_pedido']
                update = """
                    UPDATE pedido 
                    SET total_produtos = %s, total_pedido = %s
                    WHERE cpf_cliente = %s AND data_pedido = %s
                """
                self.db.execute_statement(update, (
                    total_produtos,
                    total_pedido,
                    cpf, data_pedido_exata
                ))
                print(f"Totais atualizados: total_produtos={total_produtos}, total_pedido={total_pedido:.2f}")
            else:
                print(f"Aviso: Pedido não encontrado para atualizar totais. CPF: {cpf}, Data: {data_pedido}")
        else:
            # Se não há produtos, zera os totais
            query_pedido_exato = """
                SELECT data_pedido
                FROM pedido
                WHERE cpf_cliente = %s
                    AND data_pedido >= %s - INTERVAL '1 second'
                    AND data_pedido <= %s + INTERVAL '1 second'
                LIMIT 1
            """
            pedido_exato = self.db.execute_select_one(query_pedido_exato, (cpf, data_pedido, data_pedido))
            
            if pedido_exato:
                data_pedido_exata = pedido_exato['data_pedido']
                update = """
                    UPDATE pedido 
                    SET total_produtos = 0, total_pedido = 0
                    WHERE cpf_cliente = %s AND data_pedido = %s
                """
                self.db.execute_statement(update, (cpf, data_pedido_exata))
                print(f"Totais zerados: pedido sem produtos. CPF: {cpf}, Data: {data_pedido_exata}")

    def _atualizar_estoque_pedido(self, cpf: str, data_pedido: datetime, restaurar: bool = False):
        """Atualiza o estoque dos produtos de um pedido
        Se restaurar=True, aumenta o estoque (para pedidos cancelados)
        Se restaurar=False, reduz o estoque (para pedidos confirmados)
        """
        # Busca todos os produtos do pedido
        query_produtos = """
            SELECT cp.id_produto, cp.quantidade
            FROM contemprod cp
            WHERE cp.cpf_cliente = %s AND cp.data_pedido = %s
        """
        produtos = self.db.execute_select_all(query_produtos, (cpf, data_pedido))
        
        if not produtos:
            return
        
        for produto in produtos:
            id_produto = produto['id_produto']
            quantidade = produto['quantidade']
            
            if restaurar:
                # Restaura estoque (aumenta)
                update = """
                    UPDATE produto
                    SET estoque_atual = estoque_atual + %s
                    WHERE id_produto = %s
                """
                self.db.execute_statement(update, (quantidade, id_produto))
            else:
                # Reduz estoque
                # Verifica se há estoque suficiente antes de reduzir
                query_estoque = """
                    SELECT estoque_atual FROM produto WHERE id_produto = %s
                """
                estoque_atual = self.db.execute_select_one(query_estoque, (id_produto,))
                
                if estoque_atual and estoque_atual['estoque_atual'] < quantidade:
                    print(f"Aviso: Estoque insuficiente para produto {id_produto}. Estoque atual: {estoque_atual['estoque_atual']}, necessário: {quantidade}")
                    # Continua mesmo assim, mas registra o aviso
                
                update = """
                    UPDATE produto
                    SET estoque_atual = estoque_atual - %s
                    WHERE id_produto = %s
                        AND estoque_atual >= %s
                """
                self.db.execute_statement(update, (quantidade, id_produto, quantidade))

    def get_carrinho(self, cpf: str):
        """Retorna o carrinho atual do comprador (pedido com status 'pendente')"""
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
                e.metodo_entrega,
                e.endereco_entrega,
                e.data_envio,
                e.data_prevista,
                e.frete
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
        return self.db.execute_select_one(query, (cpf,))

    def get_pedidos(self, cpf: str):
        """Retorna todos os pedidos do comprador (excluindo carrinho/pendente)"""
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
                e.metodo_entrega,
                e.endereco_entrega,
                e.data_envio,
                e.data_prevista,
                e.frete
            FROM pedido p
            LEFT JOIN pagamento pg ON pg.fk_cpf_cliente = p.cpf_cliente 
                AND pg.fk_data_pedido = p.data_pedido
            LEFT JOIN entrega e ON e.fk_cpf_cliente = p.cpf_cliente 
                AND e.fk_data_pedido = p.data_pedido
            WHERE p.cpf_cliente = %s
                AND p.status_pedido != 'pendente'
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
                e.metodo_entrega,
                e.endereco_entrega,
                e.data_envio,
                e.data_prevista,
                e.frete
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
                    e.metodo_entrega,
                    e.endereco_entrega,
                    e.data_envio,
                    e.data_prevista,
                    e.frete
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

    def finalizar_pedido(self, cpf: str, metodo_pagamento: str, endereco_entrega: str, metodo_entrega: str = None):
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
                    status_entrega, metodo_entrega, endereco_entrega, fk_cpf_cliente, fk_data_pedido, fk_cpf_vendedor
                )
                VALUES ('preparando', %s, %s, %s, %s, %s)
            """
            if not self.db.execute_statement(insert_entrega, (
                metodo_entrega, endereco_entrega, cpf, data_pedido, cpf_vendedor
            )):
                print(f"Erro ao criar entrega para CPF: {cpf}")
                return False
        else:
            # Atualiza entrega existente
            update_entrega = """
                UPDATE entrega
                SET status_entrega = 'preparando',
                    metodo_entrega = %s,
                    endereco_entrega = %s
                WHERE fk_cpf_cliente = %s AND fk_data_pedido = %s
            """
            if not self.db.execute_statement(update_entrega, (
                metodo_entrega, endereco_entrega, cpf, data_pedido
            )):
                print(f"Erro ao atualizar entrega para CPF: {cpf}")
                return False
        
        # Atualiza o status do pedido de 'pendente' para 'aguardando pagamento'
        # Isso garante que um novo carrinho (pedido pendente) possa ser criado
        update_pedido = """
            UPDATE pedido 
            SET status_pedido = 'aguardando pagamento'
            WHERE cpf_cliente = %s AND data_pedido = %s
        """
        if not self.db.execute_statement(update_pedido, (cpf, data_pedido)):
            print(f"Erro ao atualizar status do pedido para CPF: {cpf}")
            return False
        
        # Atualiza estoque quando o pedido sai de 'pendente' para 'aguardando pagamento'
        self._atualizar_estoque_pedido(cpf, data_pedido, restaurar=False)
        
        print(f"Pedido finalizado com sucesso para CPF: {cpf}, data: {data_pedido}")
        print(f"Status alterado para 'aguardando pagamento' - pedido finalizado")
        return True

    def simular_pagamento(self, cpf: str, data_pedido: str):
        """Simula pagamento de um pedido, atualizando status de 'aguardando pagamento' para 'pagamento confirmado'"""
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
        
        # Atualiza status do pedido de 'aguardando pagamento' para 'pagamento confirmado'
        update_pedido = """
            UPDATE pedido
            SET status_pedido = 'pagamento confirmado'
            WHERE cpf_cliente = %s 
                AND data_pedido >= %s - INTERVAL '1 second'
                AND data_pedido <= %s + INTERVAL '1 second'
                AND status_pedido = 'aguardando pagamento'
        """
        if not self.db.execute_statement(update_pedido, (cpf, data_pedido_pagamento, data_pedido_pagamento)):
            print(f"Erro ao atualizar status do pedido para CPF: {cpf}")
            return False
        
        print(f"Pagamento simulado com sucesso para CPF: {cpf}, data: {data_pedido_dt}")
        print(f"Método de pagamento: {pagamento['metodo_pagamento']}")
        print(f"Status do pedido alterado para 'pagamento confirmado'")
        return True

    def criar_solicitacao(self, cpf: str, data_pedido: str, tipo: str):
        """Cria solicitação sobre um pedido"""
        # Converte data_pedido para datetime usando múltiplos formatos
        data_pedido_dt = None
        data_pedido_clean = data_pedido.strip()
        
        formatos = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%d %H:%M:%S.%f',
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
        
        # Busca o pedido usando intervalo para obter a data exata do banco
        query_pedido = """
            SELECT cpf_cliente, data_pedido
            FROM pedido
            WHERE cpf_cliente = %s
                AND data_pedido >= %s - INTERVAL '1 second'
                AND data_pedido <= %s + INTERVAL '1 second'
            LIMIT 1
        """
        pedido = self.db.execute_select_one(query_pedido, (cpf, data_pedido_dt, data_pedido_dt))
        
        if not pedido:
            print(f"Pedido não encontrado para CPF {cpf} e data {data_pedido_dt}")
            return False
        
        # Usa a data exata do pedido encontrado no banco
        data_pedido_exata = pedido['data_pedido']
        data_solicitacao = datetime.now(ZoneInfo("America/Sao_Paulo"))
        status_solicitacao = 'aberta'
        
        # Cria a solicitação
        query = """
            INSERT INTO solicitacao (cpf_cliente, data_pedido, data_solicitacao, tipo, status_solicitacao)
            VALUES (%s, %s, %s, %s, %s)
        """
        if not self.db.execute_statement(query, (
            cpf, data_pedido_exata, data_solicitacao, tipo, status_solicitacao
        )):
            return False
        
        # Verifica o status atual do pedido antes de cancelar
        query_status = """
            SELECT status_pedido FROM pedido
            WHERE cpf_cliente = %s
                AND data_pedido >= %s - INTERVAL '1 second'
                AND data_pedido <= %s + INTERVAL '1 second'
        """
        pedido_info = self.db.execute_select_one(query_status, (cpf, data_pedido_exata, data_pedido_exata))
        status_anterior = pedido_info['status_pedido'] if pedido_info else None
        
        # Cancela o pedido quando a solicitação é criada
        update_pedido = """
            UPDATE pedido
            SET status_pedido = 'cancelado'
            WHERE cpf_cliente = %s
                AND data_pedido >= %s - INTERVAL '1 second'
                AND data_pedido <= %s + INTERVAL '1 second'
        """
        if not self.db.execute_statement(update_pedido, (cpf, data_pedido_exata, data_pedido_exata)):
            print(f"Erro ao cancelar pedido após criar solicitação")
            # Não retorna False aqui para não reverter a criação da solicitação
        
        # Se o pedido não estava 'pendente', restaura o estoque
        if status_anterior and status_anterior != 'pendente' and status_anterior != 'cancelado':
            self._atualizar_estoque_pedido(cpf, data_pedido_exata, restaurar=True)
        
        return True

    def get_produtos_comprados(self, cpf: str):
        """Retorna lista de produtos que o comprador já comprou (pedidos finalizados)"""
        query = """
            SELECT DISTINCT
                p.id_produto,
                p.nome_produto,
                p.preco,
                MAX(ped.data_pedido) as ultima_compra
            FROM produto p
            JOIN contemprod cp ON cp.id_produto = p.id_produto
            JOIN pedido ped ON ped.cpf_cliente = cp.cpf_cliente 
                AND ped.data_pedido = cp.data_pedido
            WHERE ped.cpf_cliente = %s
                AND ped.status_pedido != 'pendente'
                AND ped.status_pedido != 'cancelado'
            GROUP BY p.id_produto, p.nome_produto, p.preco
            ORDER BY ultima_compra DESC, p.nome_produto
        """
        return self.db.execute_select_all(query, (cpf,))

    def avaliar_produto(self, cpf: str, id_produto: int, nota: int, comentario: str = ""):
        """Avalia ou atualiza avaliação de um produto"""
        if nota < 1 or nota > 5:
            return False
        
        # Verifica se o comprador realmente comprou este produto
        query_comprou = """
            SELECT 1 
            FROM contemprod cp
            JOIN pedido ped ON ped.cpf_cliente = cp.cpf_cliente 
                AND ped.data_pedido = cp.data_pedido
            WHERE cp.cpf_cliente = %s 
                AND cp.id_produto = %s
                AND ped.status_pedido != 'pendente'
                AND ped.status_pedido != 'cancelado'
            LIMIT 1
        """
        comprou = self.db.execute_select_one(query_comprou, (cpf, id_produto))
        if not comprou:
            return False  # Comprador não comprou este produto
        
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

    def get_recomendacoes(self, cpf: str):
        """Retorna produtos baseados na categoria preferida do cliente"""
        # Verifica se o comprador tem preferência cadastrada e busca produtos dessa categoria
        query = """
            SELECT DISTINCT
                p.id_produto, 
                p.nome_produto, 
                p.preco, 
                p.estoque_atual, 
                p.origem, 
                c.nome_categoria,
                COALESCE(AVG(a.nota), 0) as media_nota
            FROM produto p
            JOIN pertencecat pc ON p.id_produto = pc.id_produto
            JOIN preferecat pr ON pc.id_categoria = pr.id_categoria
            JOIN categoria c ON pc.id_categoria = c.id_categoria
            LEFT JOIN avaliaprod a ON a.id_produto = p.id_produto
            WHERE pr.cpf_comprador = %s
            GROUP BY p.id_produto, p.nome_produto, p.preco, p.estoque_atual, p.origem, c.nome_categoria
            LIMIT 5
        """
        return self.db.execute_select_all(query, (cpf,))