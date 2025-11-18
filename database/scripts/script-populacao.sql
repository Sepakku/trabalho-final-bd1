---------------------------------------------------------
-- 1. População da tabela Usuario
---------------------------------------------------------
INSERT INTO Usuario (cpf, pnome, sobrenome, cep, email, senha_hash) VALUES
('11111111111', 'Ana', 'Silva', '01001000', 'ana@gmail.com', 'hash1'),
('22222222222', 'Bruno', 'Souza', '02002000', 'bruno@gmail.com', 'hash2'),
('33333333333', 'Carlos', 'Oliveira', '03003000', 'carlos@gmail.com', 'hash3'),
('44444444444', 'Daniela', 'Ferreira', '04004000', 'daniela@gmail.com', 'hash4'),
('55555555555', 'Eduardo', 'Gomes', '05005000', 'eduardo@gmail.com', 'hash5');

---------------------------------------------------------
-- 2. População de Comprador
---------------------------------------------------------
INSERT INTO Comprador (cpf_comprador, num_compras) VALUES
('11111111111', 3),
('22222222222', 1),
('33333333333', 0);

---------------------------------------------------------
-- 3. População de Vendedor
---------------------------------------------------------
INSERT INTO Vendedor (cpf_vendedor, nome_loja, desc_loja) VALUES
('44444444444', 'Loja DaniTec', 'Eletrônicos e informática'),
('55555555555', 'Loja EduArt', 'Artesanato e decoração');

---------------------------------------------------------
-- 4. População de Categoria
---------------------------------------------------------
INSERT INTO Categoria (nome_categoria, fk_categoria_pai) VALUES
('Eletrônicos', NULL),          -- 1
('Informática', 1),             -- 2
('Casa & Decoração', NULL),     -- 3
('Artesanato', 3);              -- 4

---------------------------------------------------------
-- 5. População de Produto
---------------------------------------------------------
INSERT INTO Produto (nome_produto, desc_produto, preco, origem, estoque_atual, alerta_estoque) VALUES
('Notebook X', 'Notebook rápido e leve', 3500.00, 'Brasil', 20, 5),          -- id 1
('Mouse Gamer', 'Mouse RGB 12000 DPI', 150.00, 'China', 50, 10),            -- id 2
('Quadro Decorativo', 'Quadro artístico feito à mão', 180.00, 'Brasil', 10, 2), -- id 3
('Vaso de Cerâmica', 'Vaso artesanal pintado à mão', 90.00, 'Brasil', 15, 3);   -- id 4

---------------------------------------------------------
-- 6. População de Pedido
---------------------------------------------------------
INSERT INTO Pedido (cpf_cliente, data_pedido, status_pedido, total_produtos, total_pedido) VALUES
('11111111111', '2025-01-10 10:00:00', 'enviado', 2, 3650.00),
('22222222222', '2025-01-12 14:30:00', 'pendente', 1, 150.00);

---------------------------------------------------------
-- 7. População de Pagamento
---------------------------------------------------------
INSERT INTO Pagamento (status_pagamento, valor_pago, metodo_pagamento, num_parcelas,
                       fk_cpf_vendedor, fk_cpf_cliente, fk_data_pedido)
VALUES
('aprovado', 3650.00, 'cartão', 3, '44444444444', '11111111111', '2025-01-10 10:00:00'),
('pendente', 150.00, 'pix', 1, '44444444444', '22222222222', '2025-01-12 14:30:00');

---------------------------------------------------------
-- 8. População de Entrega
---------------------------------------------------------
INSERT INTO Entrega (status_entrega, metodo_entrega, endereco_entrega, data_envio, data_prevista,
                     frete, endereco_vendedor, fk_cpf_cliente, fk_data_pedido, fk_cpf_vendedor)
VALUES
('enviado', 'Correios', 'Rua A, 123', '2025-01-11', '2025-01-20', 25.00,
 'Rua da Loja DaniTec, 100', '11111111111', '2025-01-10 10:00:00', '44444444444'),

('preparando', 'Transportadora X', 'Rua B, 456', NULL, '2025-01-25', 30.00,
 'Rua da Loja DaniTec, 100', '22222222222', '2025-01-12 14:30:00', '44444444444');

---------------------------------------------------------
-- 9. Solicitações
---------------------------------------------------------
INSERT INTO Solicitacao (cpf_cliente, data_pedido, data_solicitacao, tipo, status_solicitacao) VALUES
('11111111111', '2025-01-10 10:00:00', '2025-01-15 09:00:00', 'suporte', 'aberta'),
('22222222222', '2025-01-12 14:30:00', '2025-01-13 16:00:00', 'cancelamento', 'em_analise');

---------------------------------------------------------
-- 10. ContemProd (produtos do pedido)
---------------------------------------------------------
INSERT INTO ContemProd (cpf_cliente, data_pedido, id_produto, quantidade) VALUES
('11111111111', '2025-01-10 10:00:00', 1, 1),
('11111111111', '2025-01-10 10:00:00', 2, 1),
('22222222222', '2025-01-12 14:30:00', 2, 1);

---------------------------------------------------------
-- 11. AssociaProd (produtos associados à solicitação)
---------------------------------------------------------
INSERT INTO AssociaProd (cpf_cliente, data_pedido, data_solicitacao, id_produto) VALUES
('11111111111', '2025-01-10 10:00:00', '2025-01-15 09:00:00', 1);

---------------------------------------------------------
-- 12. AvaliaProd
---------------------------------------------------------
INSERT INTO AvaliaProd (cpf_comprador, id_produto, nota) VALUES
('11111111111', 1, 5),
('11111111111', 2, 4),
('22222222222', 2, 3);

---------------------------------------------------------
-- 13. PrefereCat
---------------------------------------------------------
INSERT INTO PrefereCat (cpf_comprador, id_categoria) VALUES
('11111111111', 1),
('11111111111', 2),
('22222222222', 3);

---------------------------------------------------------
-- 14. PertenceCat
---------------------------------------------------------
INSERT INTO PertenceCat (id_categoria, id_produto) VALUES
(1, 1),
(2, 1),
(1, 2),
(3, 3),
(4, 4);

---------------------------------------------------------
-- 15. VendeProd
---------------------------------------------------------
INSERT INTO VendeProd (cpf_vendedor, id_produto) VALUES
('44444444444', 1),
('44444444444', 2),
('55555555555', 3),
('55555555555', 4);
