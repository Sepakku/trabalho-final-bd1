# SI Market - Sistema de E-commerce

Sistema de e-commerce simples com duas interfaces principais: uma para compradores e outra para vendedores.

## Estrutura do Projeto

- **backend/**: API Flask em Python
- **frontend/**: Interface web em HTML, CSS e JavaScript
- **database/**: Scripts SQL para criação e população do banco de dados

## Requisitos

- Python 3.8+
- PostgreSQL
- Flask
- psycopg2-binary
- Flask-CORS

## Configuração

### 1. Banco de Dados

1. Abra o **pgAdmin** e conecte-se ao seu servidor PostgreSQL
2. Crie um banco de dados chamado `SIMarket`:
   - Clique com o botão direito em "Databases" → "Create" → "Database"
   - Nome: `SIMarket`
   - Clique em "Save"
3. Execute os scripts SQL na ordem:
   - Selecione o banco `SIMarket` no pgAdmin
   - Clique em "Tools" → "Query Tool" (ou pressione `Alt+Shift+Q`)
   - Abra o arquivo `database/scripts/script-criacao.sql`
   - Execute o script (F5 ou botão "Execute")
   - Repita o processo para `database/scripts/script-populacao.sql`

### 2. Backend

1. Configure a senha do PostgreSQL em `backend/servicos/database/conector.py`:
   ```python
   password="sua_senha_aqui"
   ```

2. Instale as dependências:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Execute o servidor:
   ```bash
   python -m backend.main
   ```

   O servidor estará rodando em `http://localhost:8001`

### 3. Frontend

1. Abra o arquivo `frontend/index.html` em um navegador web
2. Ou use um servidor HTTP simples:
   ```bash
   cd frontend
   python -m http.server 8000
   ```
   Acesse `http://localhost:8000`

## Funcionalidades Implementadas

### Compradores

- ✅ Buscar produtos com filtros (nome, origem, loja, categoria, preço)
- ✅ Adicionar produtos ao carrinho
- ✅ Visualizar carrinho e pedidos
- ✅ Finalizar pedido com método de pagamento (Crédito, Débito, Pix) e endereço
- ✅ Visualizar status do pedido e pagamento
- ✅ Criar solicitações sobre pedidos (devolução, troca, suporte, cancelamento)
- ✅ Avaliar produtos (nota de 1 a 5)

### Vendedores

- ✅ Visualizar produtos mais vendidos (período: 1, 3, 6 ou 12 meses)
- ✅ Visualizar lucro total no período
- ✅ Visualizar produtos com estoque baixo
- ✅ Adicionar produtos à loja
- ✅ Editar estoque disponível
- ✅ Remover produtos da loja
- ✅ Visualizar produtos mais devolvidos
- ✅ Visualizar produtos com melhor avaliação

## API Endpoints

### Comprador

- `GET /produtos_comprador` - Buscar produtos
- `POST /comprador/carrinho` - Adicionar ao carrinho
- `GET /comprador/pedidos?cpf=...` - Listar pedidos
- `GET /comprador/pedido?cpf=...&data_pedido=...` - Detalhes do pedido
- `POST /comprador/pedido/finalizar` - Finalizar pedido
- `POST /comprador/pedido/solicitacao` - Criar solicitação
- `POST /comprador/avaliacao` - Avaliar produto

### Vendedor

- `GET /vendedor?cpf=...` - Informações do vendedor
- `GET /vendedor/produtos/mais-vendidos?cpf=...&meses=...` - Produtos mais vendidos
- `GET /vendedor/lucro?cpf=...&meses=...` - Lucro total
- `GET /vendedor/produtos/estoque-baixo?cpf=...` - Estoque baixo
- `GET /vendedor/produtos?cpf=...` - Listar produtos
- `POST /vendedor/produtos` - Adicionar produto
- `PATCH /vendedor/produtos/<id>/estoque` - Atualizar estoque
- `DELETE /vendedor/produtos/<id>?cpf=...` - Remover produto
- `GET /vendedor/produtos/mais-devolvidos?cpf=...&meses=...` - Mais devolvidos
- `GET /vendedor/produtos/melhor-avaliacao?cpf=...` - Melhor avaliação

## Notas

- Este é um projeto de proof of concept, sem autenticação/autorização
- O CPF é usado diretamente nas requisições para identificar usuários
- Certifique-se de que o banco de dados está populado com dados de teste

## Diagrama Conceitual

![Diagrama Entidade-Relacionamento Estendido do Sistema SI Market](database/diagrams/DEER%20final%20(min,max).drawio.png)
