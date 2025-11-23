from typing import Any
import psycopg2
from psycopg2.extras import DictCursor


class DatabaseManager:
    """Classe de Gerenciamento do database"""

    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            dbname="SI-Market",  # colocar o nome do seu database
            user="postgres",
            password="postgres",  # colocar sua senha
            host="127.0.0.1",
            port=5432,
        )
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)

        def execute_statement(self, statement: str, params=None) -> bool:
        """Usado para Inserções, Deleções, Alter Tables"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(statement, params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao executar statement: {e}")
            return False

    def execute_select_all(self, query: str, params=None):
        """Usado para SELECTS no geral"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_select_one(self, query: str, params=None):
        """Usado para SELECT com apenas uma linha de resposta"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result if result else None
    
    def execute_statement_returning(self, statement: str, params=None):
        """Usado para INSERT/UPDATE com RETURNING"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(statement, params)
                result = cursor.fetchone()
            self.conn.commit()
            return result[0] if result else None
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao executar RETURNING: {e}")
            return None