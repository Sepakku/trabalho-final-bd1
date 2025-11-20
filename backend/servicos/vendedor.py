from backend.servicos.database.conector import DatabaseManager


class VendedorDatabase:
    def __init__(self, db_provider=DatabaseManager()) -> None:
        self.db = db_provider

    # Função para mostrar informações básicas dos vendedores, caso coloque o cpf e senha irá aparecer todos os dados
    def get_vendedor(self, cpf: str, senha_hash: str):
        if cpf and senha_hash:
            query = """
                SELECT * FROM usuario u
                JOIN vendedor v ON v.cpf_vendedor = u.cpf
                WHERE u.cpf = %s AND u.senha_hash = %s
                """
            return self.db.execute_select_all(query, (cpf, senha_hash))

        query = """
                SELECT 
                    v.nome_loja,
                    v.desc_loja
                FROM usuario u
                JOIN vendedor v ON v.cpf_vendedor = u.cpf
                """
        return self.db.execute_select_all(query)

    # Função para registrar novo vendedor a partir de um usuário já existente e sem ser vendedor
    def post_vendedor(self, cpf: str, senha_hash: str, nome_loja: str, desc_loja: str):
        if cpf and senha_hash and nome_loja and desc_loja:
            query1 = f"""
                     SELECT * FROM usuario
                     WHERE cpf = %s AND senha_hash = %s
                     """
            query2 = f"""
                     SELECT * FROM vendedor
                     WHERE cpf_vendedor = %s
                     """
            existe_usuario = self.db.execute_select_one(query1, (cpf, senha_hash))
            existe_vendedor = self.db.execute_select_one(query2, (cpf,))
            if existe_usuario and not existe_vendedor:
                statement = f"""
                    INSERT INTO vendedor (cpf_vendedor, nome_loja, desc_loja) 
                    VALUES (%s, %s, %s)
                """
                self.db.execute_statement(statement, (cpf, nome_loja, desc_loja))

                return True

        return False

    # Função para apagar um registro de vendedor
    def delete_vendedor(self, cpf: str, senha_hash: str):
        autoriza = self.db.execute_select_one(
            f"SELECT 1 FROM usuario WHERE cpf = %s AND senha_hash = %s",
            (cpf, senha_hash)
        )
        existe_vendedor = self.db.execute_select_one(
            f"SELECT 1 FROM vendedor WHERE cpf_vendedor = %s",
            (cpf,)
        )
        if autoriza and existe_vendedor:
            statement = f"DELETE FROM vendedor WHERE cpf_vendedor = %s"
            self.db.execute_statement(statement, (cpf,))
            return True

        return False

    # Função para atualizar os dados do vendedor (nome da loja e descrição)
    def update_vendedor(self, cpf: str, senha_hash: str, nome_loja: str, desc_loja: str):
        autoriza = self.db.execute_select_one(
            f"SELECT 1 FROM usuario WHERE cpf = %s AND senha_hash = %s",
            (cpf, senha_hash)
        )
        existe_vendedor = self.db.execute_select_one(
            f"SELECT 1 FROM vendedor WHERE cpf_vendedor = %s",
            (cpf,)
        )

        if not (autoriza and existe_vendedor):
            return False

        campos = []
        valores = []

        if nome_loja:
            campos.append(f"nome_loja = %s")
            valores.append(nome_loja)

        if desc_loja:
            campos.append(f"desc_loja = %s")
            valores.append(desc_loja)

        if not campos:
            return False

        statement = f"""
                UPDATE vendedor
                SET {", ".join(campos)}
                WHERE cpf_vendedor = %s
            """
        valores.append(cpf)
        self.db.execute_statement(statement, tuple(valores))
        return True
