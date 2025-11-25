--------------------------------------------------------
-- RESET DATABASE (truncate everything + reset sequences)
--------------------------------------------------------

SET session_replication_role = 'replica';

TRUNCATE TABLE
    AssociaProd,
    AvaliaProd,
    PrefereCat,
    PertenceCat,
    VendeProd,
    ContemProd,
    Solicitacao,
    Entrega,
    Pagamento,
    Pedido,
    Produto,
    Categoria,
    Vendedor,
    Comprador,
    Usuario
RESTART IDENTITY CASCADE;

SET session_replication_role = 'origin';

--------------------------------------------------------
-- INSERÇÃO DE DADOS
-- Mínimo de 25 registros por tabela
--------------------------------------------------------

-- ============================================
-- 1. USUARIO (25 registros)
-- ============================================
INSERT INTO Usuario (cpf, pnome, sobrenome, cep, email, senha_hash) VALUES
('11111111111', 'João', 'Silva', '01310100', 'joao.silva@email.com', 'hash_senha_1'),
('22222222222', 'Maria', 'Oliveira', '20040020', 'maria.oliveira@email.com', 'hash_senha_2'),
('33333333333', 'Carlos', 'Souza', '30130100', 'carlos.souza@email.com', 'hash_senha_3'),
('44444444444', 'Ana', 'Pereira', '40020100', 'ana.pereira@email.com', 'hash_senha_4'),
('55555555555', 'Lucas', 'Costa', '50050100', 'lucas.costa@email.com', 'hash_senha_5'),
('66666666666', 'Juliana', 'Alves', '60060100', 'juliana.alves@email.com', 'hash_senha_6'),
('77777777777', 'Pedro', 'Martins', '70070100', 'pedro.martins@email.com', 'hash_senha_7'),
('88888888888', 'Fernanda', 'Santos', '80080100', 'fernanda.santos@email.com', 'hash_senha_8'),
('99999999999', 'Rafael', 'Ferreira', '90090100', 'rafael.ferreira@email.com', 'hash_senha_9'),
('10101010101', 'Beatriz', 'Rodrigues', '01010100', 'beatriz.rodrigues@email.com', 'hash_senha_10'),
('12121212121', 'Ricardo', 'Lima', '12121200', 'ricardo.lima@email.com', 'hash_senha_11'),
('13131313131', 'Patrícia', 'Gomes', '13131300', 'patricia.gomes@email.com', 'hash_senha_12'),
('14141414141', 'Gustavo', 'Sousa', '14141400', 'gustavo.sousa@email.com', 'hash_senha_13'),
('15151515151', 'Mariana', 'Nascimento', '15151500', 'mariana.nascimento@email.com', 'hash_senha_14'),
('16161616161', 'Eduardo', 'Barbosa', '16161600', 'eduardo.barbosa@email.com', 'hash_senha_15'),
('17171717171', 'Tatiane', 'Rocha', '17171700', 'tatiane.rocha@email.com', 'hash_senha_16'),
('18181818181', 'Leonardo', 'Dias', '18181800', 'leonardo.dias@email.com', 'hash_senha_17'),
('19191919191', 'Jéssica', 'Melo', '19191900', 'jessica.melo@email.com', 'hash_senha_18'),
('20202020202', 'Vitor', 'Farias', '20202000', 'vitor.farias@email.com', 'hash_senha_19'),
('21212121212', 'Carla', 'Vieira', '21212100', 'carla.vieira@email.com', 'hash_senha_20'),
('23232323232', 'Marcos', 'Pinto', '23232300', 'marcos.pinto@email.com', 'hash_senha_21'),
('24242424242', 'Larissa', 'Mendes', '24242400', 'larissa.mendes@email.com', 'hash_senha_22'),
('25252525252', 'Felipe', 'Carvalho', '25252500', 'felipe.carvalho@email.com', 'hash_senha_23'),
('26262626262', 'Camila', 'Araújo', '26262600', 'camila.araujo@email.com', 'hash_senha_24'),
('27272727272', 'Bruno', 'Cardoso', '27272700', 'bruno.cardoso@email.com', 'hash_senha_25');

-- ============================================
-- 2. COMPRADOR (25 registros)
-- ============================================
INSERT INTO Comprador (cpf_comprador, num_compras) VALUES
('11111111111', 15),
('22222222222', 8),
('33333333333', 12),
('44444444444', 5),
('55555555555', 20),
('66666666666', 7),
('77777777777', 10),
('88888888888', 18),
('99999999999', 3),
('10101010101', 25),
('12121212121', 9),
('13131313131', 14),
('14141414141', 6),
('15151515151', 11),
('16161616161', 16),
('17171717171', 4),
('18181818181', 13),
('19191919191', 19),
('20202020202', 8),
('21212121212', 22),
('23232323232', 10),
('24242424242', 17),
('25252525252', 6),
('26262626262', 21),
('27272727272', 12);

-- ============================================
-- 3. VENDEDOR (25 registros)
-- ============================================
INSERT INTO Vendedor (cpf_vendedor, nome_loja, desc_loja) VALUES
('11111111111', 'TechStore', 'Loja especializada em eletrônicos e tecnologia'),
('22222222222', 'ModaFashion', 'Loja de moda e acessórios femininos e masculinos'),
('33333333333', 'BelezaTotal', 'Produtos de beleza e cuidados pessoais'),
('44444444444', 'BrinquedosKids', 'Loja de brinquedos e artigos infantis'),
('55555555555', 'SportLife', 'Artigos esportivos e equipamentos de fitness'),
('66666666666', 'LivrariaCultura', 'Livros, revistas e material escolar'),
('77777777777', 'InfoTech', 'Produtos de informática e gadgets'),
('88888888888', 'PetShopAmigo', 'Produtos para pets e animais de estimação'),
('99999999999', 'FerramentasPro', 'Ferramentas e equipamentos profissionais'),
('10101010101', 'DecoraCasa', 'Produtos de decoração e móveis'),
('12121212121', 'JardimVerde', 'Produtos de jardinagem e plantas'),
('13131313131', 'GourmetShop', 'Alimentos e bebidas gourmet'),
('14141414141', 'BijouxElegance', 'Bijuterias e acessórios finos'),
('15151515151', 'FestasEventos', 'Artigos para festas e eventos'),
('16161616161', 'CozinhaChef', 'Produtos de cozinha e utensílios'),
('17171717171', 'MobileAccess', 'Acessórios e gadgets para celular'),
('18181818181', 'CosmeticBeauty', 'Cosméticos e perfumes importados'),
('19191919191', 'AutoParts', 'Peças automotivas e acessórios'),
('20202020202', 'PapelariaPlus', 'Produtos de papelaria e escritório'),
('21212121212', 'SaudeVida', 'Produtos de saúde e bem-estar'),
('23232323232', 'MoveisDesign', 'Móveis planejados e decoração'),
('24242424242', 'FitnessZone', 'Equipamentos de fitness e suplementos'),
('25252525252', 'EletroCasa', 'Eletrodomésticos e utilidades'),
('26262626262', 'KidsWorld', 'Produtos infantis e educativos'),
('27272727272', 'HomeDecor', 'Decoração e organização para casa');

-- ============================================
-- 4. CATEGORIA (25 registros)
-- ============================================
INSERT INTO Categoria (nome_categoria, fk_categoria_pai) VALUES
('Eletrônicos', NULL),
('Roupas', NULL),
('Beleza', NULL),
('Brinquedos', NULL),
('Esportes', NULL),
('Livros', NULL),
('Informática', NULL),
('Pets', NULL),
('Ferramentas', NULL),
('Decoração', NULL),
('Jardinagem', NULL),
('Alimentos', NULL),
('Bijuterias', NULL),
('Festas e Eventos', NULL),
('Cozinha', NULL),
('Acessórios para Celular', NULL),
('Cosméticos', NULL),
('Automotivos', NULL),
('Papelaria', NULL),
('Saúde', NULL),
('Móveis', NULL),
('Fitness', NULL),
('Eletrodomésticos', NULL),
('Infantil', NULL),
('Casa e Jardim', NULL);

-- ============================================
-- 5. PRODUTO (25 registros)
-- ============================================
INSERT INTO Produto (nome_produto, desc_produto, preco, origem, estoque_atual, alerta_estoque) VALUES
('Smartphone Galaxy S24', 'Smartphone Android com tela de 6.7 polegadas, 256GB de armazenamento, câmera tripla de 108MP', 3499.99, 'Brasil', 45, 10),
('Notebook Gamer RTX 4060', 'Notebook gamer com processador Intel i7, 16GB RAM, placa de vídeo RTX 4060, SSD 512GB', 5999.99, 'China', 20, 5),
('Camiseta Básica Algodão', 'Camiseta 100% algodão, disponível em várias cores e tamanhos do P ao GG', 39.99, 'Brasil', 300, 50),
('Kit Maquiagem Profissional', 'Kit completo com 24 cores de sombras, batons, pincéis e acessórios', 199.90, 'China', 80, 15),
('Boneca Interativa Bebê', 'Boneca que chora, ri e reage ao toque, com acessórios incluídos', 249.90, 'China', 60, 10),
('Tênis Running Nike', 'Tênis esportivo com tecnologia de amortecimento, ideal para corrida', 299.99, 'Brasil', 120, 20),
('Livro: O Poder do Hábito', 'Livro best-seller sobre desenvolvimento pessoal e mudança de hábitos', 49.90, 'Brasil', 200, 30),
('Mouse Gamer RGB', 'Mouse gamer com iluminação RGB, 16000 DPI, 8 botões programáveis', 129.99, 'China', 150, 25),
('Ração Premium para Cães', 'Ração super premium 15kg, rica em proteínas e nutrientes essenciais', 189.90, 'Brasil', 400, 50),
('Furadeira Parafusadeira', 'Furadeira elétrica com 2 velocidades, kit completo com acessórios', 249.99, 'China', 70, 15),
('Sofá Retrátil 3 Lugares', 'Sofá retrátil com tecido antimofo, estrutura em madeira maciça', 1299.99, 'Brasil', 30, 5),
('Planta Artificial Decorativa', 'Planta artificial de alta qualidade, aparência realista, sem manutenção', 89.99, 'Brasil', 180, 20),
('Máquina de Café Expresso', 'Máquina de café expresso automática, capacidade para 1.5L, sistema de limpeza', 899.99, 'Itália', 40, 8),
('Smartwatch Fitness Pro', 'Relógio inteligente com GPS, monitoramento cardíaco, resistente à água', 599.99, 'China', 90, 15),
('Brinquedo Educativo Montar', 'Brinquedo de montar com 500 peças, desenvolve criatividade e coordenação', 79.90, 'Brasil', 150, 25),
('Cadeira Ergonômica Escritório', 'Cadeira ergonômica com ajuste de altura, apoio lombar, braços ajustáveis', 499.99, 'Brasil', 55, 10),
('Bicicleta Aro 26', 'Bicicleta com 21 marchas, freios a disco, suspensão dianteira', 899.99, 'Brasil', 35, 8),
('Cama para Cachorro Grande', 'Cama ortopédica para cães grandes, material antialérgico, lavável', 129.99, 'Brasil', 100, 15),
('Tablet Android 10 polegadas', 'Tablet com tela Full HD, 64GB, processador octa-core, câmera dupla', 799.99, 'China', 65, 12),
('Batedeira Planetária 5L', 'Batedeira planetária com 5 litros, 800W, 5 velocidades, acessórios incluídos', 449.99, 'Brasil', 45, 10),
('Fone Bluetooth Cancelamento Ruído', 'Fone Bluetooth com cancelamento ativo de ruído, bateria 30h', 399.99, 'China', 110, 20),
('Colchão Ortopédico Casal', 'Colchão ortopédico casal, molas ensacadas, espuma de alta densidade', 1199.99, 'Brasil', 25, 5),
('Chuveiro Elétrico Digital', 'Chuveiro elétrico digital com controle de temperatura, display LED', 299.99, 'Brasil', 85, 15),
('Almofada Decorativa Conjunto', 'Conjunto com 4 almofadas decorativas, tecido premium, estampas modernas', 149.99, 'Brasil', 220, 30),
('Cafeteira Elétrica 12 Xícaras', 'Cafeteira elétrica com capacidade para 12 xícaras, sistema anti-gotejamento', 199.99, 'Brasil', 130, 20);

-- ============================================
-- 6. PEDIDO (30 registros - mais que 25 para variedade)
-- Distribuição de status:
-- - pendente: 5
-- - aguardando pagamento: 5
-- - pagamento confirmado: 5
-- - enviado: 5
-- - entregue: 7
-- - cancelado: 3
-- ============================================
INSERT INTO Pedido (cpf_cliente, status_pedido, total_produtos, total_pedido, data_pedido) VALUES
-- Pedidos pendentes (carrinho)
('11111111111', 'pendente', 2, 3599.98, '2025-11-01 10:00:00'),
('22222222222', 'pendente', 1, 39.99, '2025-11-01 11:00:00'),
('33333333333', 'pendente', 3, 449.70, '2025-11-01 12:00:00'),
('44444444444', 'pendente', 1, 249.90, '2025-11-01 13:00:00'),
('55555555555', 'pendente', 2, 599.98, '2025-11-01 14:00:00'),

-- Pedidos aguardando pagamento
('66666666666', 'aguardando pagamento', 1, 49.90, '2025-10-25 09:00:00'),
('77777777777', 'aguardando pagamento', 2, 259.98, '2025-10-26 10:00:00'),
('88888888888', 'aguardando pagamento', 1, 189.90, '2025-10-27 11:00:00'),
('99999999999', 'aguardando pagamento', 3, 749.97, '2025-10-28 12:00:00'),
('10101010101', 'aguardando pagamento', 1, 1299.99, '2025-10-29 13:00:00'),

-- Pedidos com pagamento confirmado (aguardando envio)
('12121212121', 'pagamento confirmado', 1, 89.99, '2025-10-20 08:00:00'),
('13131313131', 'pagamento confirmado', 2, 1499.98, '2025-10-21 09:00:00'),
('14141414141', 'pagamento confirmado', 1, 599.99, '2025-10-22 10:00:00'),
('15151515151', 'pagamento confirmado', 3, 239.70, '2025-10-23 11:00:00'),
('16161616161', 'pagamento confirmado', 1, 499.99, '2025-10-24 12:00:00'),

-- Pedidos enviados
('17171717171', 'enviado', 2, 699.98, '2025-10-15 08:00:00'),
('18181818181', 'enviado', 1, 129.99, '2025-10-16 09:00:00'),
('19191919191', 'enviado', 2, 799.98, '2025-10-17 10:00:00'),
('20202020202', 'enviado', 1, 449.99, '2025-10-18 11:00:00'),
('21212121212', 'enviado', 3, 1199.97, '2025-10-19 12:00:00'),

-- Pedidos entregues
('23232323232', 'entregue', 1, 399.99, '2025-10-05 08:00:00'),
('24242424242', 'entregue', 2, 2399.98, '2025-10-06 09:00:00'),
('25252525252', 'entregue', 1, 199.99, '2025-10-07 10:00:00'),
('26262626262', 'entregue', 3, 899.70, '2025-10-08 11:00:00'),
('27272727272', 'entregue', 1, 299.99, '2025-10-09 12:00:00'),
('11111111111', 'entregue', 2, 349.98, '2025-10-10 13:00:00'),
('22222222222', 'entregue', 1, 79.90, '2025-10-11 14:00:00'),

-- Pedidos cancelados
('33333333333', 'cancelado', 1, 249.99, '2025-10-12 08:00:00'),
('44444444444', 'cancelado', 2, 499.98, '2025-10-13 09:00:00'),
('55555555555', 'cancelado', 1, 1199.99, '2025-10-14 10:00:00');

-- ============================================
-- 7. PAGAMENTO (25 registros - apenas para pedidos não pendentes)
-- Vendedor baseado no produto do pedido (ver ContemProd e VendeProd)
-- ============================================
INSERT INTO Pagamento (status_pagamento, valor_pago, metodo_pagamento, num_parcelas, fk_cpf_vendedor, fk_cpf_cliente, fk_data_pedido) VALUES
-- Pagamentos para pedidos aguardando pagamento (status: pendente)
-- Pedido 66666666666: produto 7 -> vendedor 66666666666
('pendente', 49.90, 'Pix', 1, '66666666666', '66666666666', '2025-10-25 09:00:00'),
-- Pedido 77777777777: produtos 8,9 -> vendedor 77777777777
('pendente', 259.98, 'Crédito', 2, '77777777777', '77777777777', '2025-10-26 10:00:00'),
-- Pedido 88888888888: produto 9 -> vendedor 88888888888
('pendente', 189.90, 'Débito', 1, '88888888888', '88888888888', '2025-10-27 11:00:00'),
-- Pedido 99999999999: produtos 10,11,12 -> vendedor 99999999999 (produto 10)
('pendente', 749.97, 'Crédito', 3, '99999999999', '99999999999', '2025-10-28 12:00:00'),
-- Pedido 10101010101: produto 11 -> vendedor 10101010101
('pendente', 1299.99, 'Crédito', 6, '10101010101', '10101010101', '2025-10-29 13:00:00'),

-- Pagamentos aprovados para pedidos com pagamento confirmado
-- Pedido 12121212121: produto 12 -> vendedor 12121212121
('aprovado', 89.99, 'Pix', 1, '12121212121', '12121212121', '2025-10-20 08:00:00'),
-- Pedido 13131313131: produtos 1,2 -> vendedor 11111111111
('aprovado', 1499.98, 'Crédito', 3, '11111111111', '13131313131', '2025-10-21 09:00:00'),
-- Pedido 14141414141: produto 14 -> vendedor 14141414141
('aprovado', 599.99, 'Débito', 1, '14141414141', '14141414141', '2025-10-22 10:00:00'),
-- Pedido 15151515151: produtos 15,16,17 -> vendedor 44444444444 (produto 15)
('aprovado', 239.70, 'Pix', 1, '44444444444', '15151515151', '2025-10-23 11:00:00'),
-- Pedido 16161616161: produto 16 -> vendedor 77777777777
('aprovado', 499.99, 'Crédito', 2, '77777777777', '16161616161', '2025-10-24 12:00:00'),

-- Pagamentos aprovados para pedidos enviados
-- Pedido 17171717171: produtos 17,18 -> vendedor 55555555555 (produto 17)
('aprovado', 699.98, 'Crédito', 2, '55555555555', '17171717171', '2025-10-15 08:00:00'),
-- Pedido 18181818181: produto 18 -> vendedor 88888888888
('aprovado', 129.99, 'Pix', 1, '88888888888', '18181818181', '2025-10-16 09:00:00'),
-- Pedido 19191919191: produtos 19,20 -> vendedor 11111111111 (produto 19)
('aprovado', 799.98, 'Débito', 1, '11111111111', '19191919191', '2025-10-17 10:00:00'),
-- Pedido 20202020202: produto 20 -> vendedor 15151515151
('aprovado', 449.99, 'Crédito', 3, '15151515151', '20202020202', '2025-10-18 11:00:00'),
-- Pedido 21212121212: produtos 21,22,23 -> vendedor 17171717171 (produto 21)
('aprovado', 1199.97, 'Crédito', 4, '17171717171', '21212121212', '2025-10-19 12:00:00'),

-- Pagamentos aprovados para pedidos entregues
-- Pedido 23232323232: produto 22 -> vendedor 18181818181
('aprovado', 399.99, 'Pix', 1, '18181818181', '23232323232', '2025-10-05 08:00:00'),
-- Pedido 24242424242: produtos 1,2 -> vendedor 11111111111
('aprovado', 2399.98, 'Crédito', 6, '11111111111', '24242424242', '2025-10-06 09:00:00'),
-- Pedido 25252525252: produto 24 -> vendedor 20202020202
('aprovado', 199.99, 'Débito', 1, '20202020202', '25252525252', '2025-10-07 10:00:00'),
-- Pedido 26262626262: produtos 25,1,3 -> vendedor 16161616161 (produto 25)
('aprovado', 899.70, 'Crédito', 2, '16161616161', '26262626262', '2025-10-08 11:00:00'),
-- Pedido 27272727272: produto 6 -> vendedor 55555555555
('aprovado', 299.99, 'Pix', 1, '55555555555', '27272727272', '2025-10-09 12:00:00'),
-- Pedido 11111111111: produtos 7,8 -> vendedor 66666666666 (produto 7)
('aprovado', 349.98, 'Débito', 1, '66666666666', '11111111111', '2025-10-10 13:00:00'),
-- Pedido 22222222222: produto 15 -> vendedor 44444444444
('aprovado', 79.90, 'Pix', 1, '44444444444', '22222222222', '2025-10-11 14:00:00'),

-- Pagamentos rejeitados para pedidos cancelados
-- Pedido 33333333333: produto 10 -> vendedor 99999999999
('rejeitado', 249.99, 'Crédito', 1, '99999999999', '33333333333', '2025-10-12 08:00:00'),
-- Pedido 44444444444: produtos 11,12 -> vendedor 10101010101 (produto 11)
('rejeitado', 499.98, 'Débito', 1, '10101010101', '44444444444', '2025-10-13 09:00:00'),
-- Pedido 55555555555: produto 11 -> vendedor 10101010101
('rejeitado', 1199.99, 'Crédito', 3, '10101010101', '55555555555', '2025-10-14 10:00:00');

-- ============================================
-- 8. ENTREGA (25 registros - apenas para pedidos não pendentes/cancelados sem entrega)
-- ============================================
INSERT INTO Entrega (status_entrega, metodo_entrega, endereco_entrega, data_envio, data_prevista, frete, fk_cpf_cliente, fk_data_pedido, fk_cpf_vendedor) VALUES
-- Entregas para pedidos com pagamento confirmado (status: preparando)
-- Vendedor deve ser o mesmo do pagamento
('preparando', 'Correios', 'Rua das Flores, 123, Centro, São Paulo - SP, CEP: 01310100', '2025-10-21 14:00:00', '2025-10-28 18:00:00', 15.00, '12121212121', '2025-10-20 08:00:00', '12121212121'),
('preparando', 'PAC', 'Av. Paulista, 456, Bela Vista, São Paulo - SP, CEP: 01310100', '2025-10-22 15:00:00', '2025-10-29 18:00:00', 12.50, '13131313131', '2025-10-21 09:00:00', '11111111111'),
('preparando', 'Motoboy', 'Rua Augusta, 789, Consolação, São Paulo - SP, CEP: 01310100', NULL, NULL, 25.00, '14141414141', '2025-10-22 10:00:00', '14141414141'),
('preparando', 'Correios', 'Rua Oscar Freire, 321, Jardins, São Paulo - SP, CEP: 01310100', '2025-10-24 16:00:00', '2025-10-31 18:00:00', 18.00, '15151515151', '2025-10-23 11:00:00', '44444444444'),
('preparando', 'PAC', 'Alameda Santos, 654, Cerqueira César, São Paulo - SP, CEP: 01310100', '2025-10-25 17:00:00', '2025-11-01 18:00:00', 20.00, '16161616161', '2025-10-24 12:00:00', '77777777777'),

-- Entregas para pedidos enviados (status: enviado)
('enviado', 'Correios', 'Rua Haddock Lobo, 987, Cerqueira César, São Paulo - SP, CEP: 01310100', '2025-10-16 10:00:00', '2025-10-23 18:00:00', 15.00, '17171717171', '2025-10-15 08:00:00', '55555555555'),
('enviado', 'PAC', 'Av. Rebouças, 147, Pinheiros, São Paulo - SP, CEP: 01310100', '2025-10-17 11:00:00', '2025-10-24 18:00:00', 12.50, '18181818181', '2025-10-16 09:00:00', '88888888888'),
('enviado', 'Motoboy', 'Rua dos Três Irmãos, 258, Butantã, São Paulo - SP, CEP: 01310100', '2025-10-18 12:00:00', '2025-10-18 20:00:00', 30.00, '19191919191', '2025-10-17 10:00:00', '11111111111'),
('enviado', 'Correios', 'Rua Fradique Coutinho, 369, Pinheiros, São Paulo - SP, CEP: 01310100', '2025-10-19 13:00:00', '2025-10-26 18:00:00', 18.00, '20202020202', '2025-10-18 11:00:00', '15151515151'),
('enviado', 'PAC', 'Rua Teodoro Sampaio, 741, Pinheiros, São Paulo - SP, CEP: 01310100', '2025-10-20 14:00:00', '2025-10-27 18:00:00', 20.00, '21212121212', '2025-10-19 12:00:00', '17171717171'),

-- Entregas para pedidos entregues (status: entregue)
('entregue', 'Correios', 'Rua Bela Cintra, 852, Consolação, São Paulo - SP, CEP: 01310100', '2025-10-06 09:00:00', '2025-10-13 18:00:00', 15.00, '23232323232', '2025-10-05 08:00:00', '18181818181'),
('entregue', 'PAC', 'Rua Estados Unidos, 963, Jardim América, São Paulo - SP, CEP: 01310100', '2025-10-07 10:00:00', '2025-10-14 18:00:00', 12.50, '24242424242', '2025-10-06 09:00:00', '11111111111'),
('entregue', 'Motoboy', 'Rua Pamplona, 159, Jardim Paulista, São Paulo - SP, CEP: 01310100', '2025-10-08 11:00:00', '2025-10-08 18:00:00', 25.00, '25252525252', '2025-10-07 10:00:00', '20202020202'),
('entregue', 'Correios', 'Rua da Consolação, 357, Consolação, São Paulo - SP, CEP: 01310100', '2025-10-09 12:00:00', '2025-10-16 18:00:00', 18.00, '26262626262', '2025-10-08 11:00:00', '16161616161'),
('entregue', 'PAC', 'Rua dos Pinheiros, 468, Pinheiros, São Paulo - SP, CEP: 01310100', '2025-10-10 13:00:00', '2025-10-17 18:00:00', 20.00, '27272727272', '2025-10-09 12:00:00', '55555555555'),
('entregue', 'Correios', 'Rua dos Três Irmãos, 579, Butantã, São Paulo - SP, CEP: 01310100', '2025-10-11 14:00:00', '2025-10-18 18:00:00', 15.00, '11111111111', '2025-10-10 13:00:00', '66666666666'),
('entregue', 'Motoboy', 'Rua Fradique Coutinho, 680, Pinheiros, São Paulo - SP, CEP: 01310100', '2025-10-12 15:00:00', '2025-10-12 20:00:00', 30.00, '22222222222', '2025-10-11 14:00:00', '44444444444'),

-- Entregas com falha para pedidos cancelados (alguns podem ter tentativa de entrega)
('falha', 'Correios', 'Rua Teodoro Sampaio, 791, Pinheiros, São Paulo - SP, CEP: 01310100', '2025-10-13 16:00:00', '2025-10-20 18:00:00', 15.00, '33333333333', '2025-10-12 08:00:00', '99999999999'),
('falha', 'PAC', 'Rua Bela Cintra, 802, Consolação, São Paulo - SP, CEP: 01310100', '2025-10-14 17:00:00', '2025-10-21 18:00:00', 12.50, '44444444444', '2025-10-13 09:00:00', '10101010101'),
('falha', 'Motoboy', 'Rua Estados Unidos, 913, Jardim América, São Paulo - SP, CEP: 01310100', '2025-10-15 18:00:00', '2025-10-15 20:00:00', 25.00, '55555555555', '2025-10-14 10:00:00', '10101010101');

-- ============================================
-- 9. SOLICITACAO (25 registros)
-- ============================================
INSERT INTO Solicitacao (cpf_cliente, data_pedido, data_solicitacao, tipo, status_solicitacao) VALUES
-- Solicitações para pedidos entregues e enviados
('23232323232', '2025-10-05 08:00:00', '2025-10-06 10:00:00', 'devolucao', 'aberta'),
('24242424242', '2025-10-06 09:00:00', '2025-10-07 11:00:00', 'troca', 'em_analise'),
('25252525252', '2025-10-07 10:00:00', '2025-10-08 12:00:00', 'suporte', 'concluida'),
('26262626262', '2025-10-08 11:00:00', '2025-10-09 13:00:00', 'cancelamento', 'aberta'),
('27272727272', '2025-10-09 12:00:00', '2025-10-10 14:00:00', 'devolucao', 'concluida'),
('11111111111', '2025-10-10 13:00:00', '2025-10-11 15:00:00', 'troca', 'em_analise'),
('22222222222', '2025-10-11 14:00:00', '2025-10-12 16:00:00', 'suporte', 'aberta'),
('17171717171', '2025-10-15 08:00:00', '2025-10-16 10:00:00', 'devolucao', 'aberta'),
('18181818181', '2025-10-16 09:00:00', '2025-10-17 11:00:00', 'troca', 'concluida'),
('19191919191', '2025-10-17 10:00:00', '2025-10-18 12:00:00', 'suporte', 'em_analise'),
('20202020202', '2025-10-18 11:00:00', '2025-10-19 13:00:00', 'cancelamento', 'aberta'),
('21212121212', '2025-10-19 12:00:00', '2025-10-20 14:00:00', 'devolucao', 'concluida'),
('12121212121', '2025-10-20 08:00:00', '2025-10-21 10:00:00', 'troca', 'aberta'),
('13131313131', '2025-10-21 09:00:00', '2025-10-22 11:00:00', 'suporte', 'em_analise'),
('14141414141', '2025-10-22 10:00:00', '2025-10-23 12:00:00', 'cancelamento', 'concluida'),
('15151515151', '2025-10-23 11:00:00', '2025-10-24 13:00:00', 'devolucao', 'aberta'),
('16161616161', '2025-10-24 12:00:00', '2025-10-25 14:00:00', 'troca', 'concluida'),
('66666666666', '2025-10-25 09:00:00', '2025-10-26 10:00:00', 'suporte', 'aberta'),
('77777777777', '2025-10-26 10:00:00', '2025-10-27 11:00:00', 'cancelamento', 'em_analise'),
('88888888888', '2025-10-27 11:00:00', '2025-10-28 12:00:00', 'devolucao', 'concluida'),
('99999999999', '2025-10-28 12:00:00', '2025-10-29 13:00:00', 'troca', 'aberta'),
('10101010101', '2025-10-29 13:00:00', '2025-10-30 14:00:00', 'suporte', 'em_analise'),
('33333333333', '2025-10-12 08:00:00', '2025-10-13 09:00:00', 'cancelamento', 'concluida'),
('44444444444', '2025-10-13 09:00:00', '2025-10-14 10:00:00', 'devolucao', 'aberta'),
('55555555555', '2025-10-14 10:00:00', '2025-10-15 11:00:00', 'troca', 'concluida');

-- ============================================
-- 10. CONTEMPROD (30 registros - relaciona produtos aos pedidos)
-- ============================================
INSERT INTO ContemProd (cpf_cliente, data_pedido, id_produto, quantidade) VALUES
-- Produtos nos pedidos pendentes
('11111111111', '2025-11-01 10:00:00', 1, 1),
('11111111111', '2025-11-01 10:00:00', 2, 1),
('22222222222', '2025-11-01 11:00:00', 3, 1),
('33333333333', '2025-11-01 12:00:00', 4, 1),
('33333333333', '2025-11-01 12:00:00', 5, 1),
('33333333333', '2025-11-01 12:00:00', 6, 1),
('44444444444', '2025-11-01 13:00:00', 5, 1),
('55555555555', '2025-11-01 14:00:00', 6, 1),
('55555555555', '2025-11-01 14:00:00', 7, 1),

-- Produtos nos pedidos aguardando pagamento
('66666666666', '2025-10-25 09:00:00', 7, 1),
('77777777777', '2025-10-26 10:00:00', 8, 1),
('77777777777', '2025-10-26 10:00:00', 9, 1),
('88888888888', '2025-10-27 11:00:00', 9, 1),
('99999999999', '2025-10-28 12:00:00', 10, 1),
('99999999999', '2025-10-28 12:00:00', 11, 1),
('99999999999', '2025-10-28 12:00:00', 12, 1),
('10101010101', '2025-10-29 13:00:00', 11, 1),

-- Produtos nos pedidos com pagamento confirmado
('12121212121', '2025-10-20 08:00:00', 12, 1),
('13131313131', '2025-10-21 09:00:00', 1, 1),
('13131313131', '2025-10-21 09:00:00', 2, 1),
('14141414141', '2025-10-22 10:00:00', 14, 1),
('15151515151', '2025-10-23 11:00:00', 15, 1),
('15151515151', '2025-10-23 11:00:00', 16, 1),
('15151515151', '2025-10-23 11:00:00', 17, 1),
('16161616161', '2025-10-24 12:00:00', 16, 1),

-- Produtos nos pedidos enviados e entregues
('17171717171', '2025-10-15 08:00:00', 17, 1),
('17171717171', '2025-10-15 08:00:00', 18, 1),
('18181818181', '2025-10-16 09:00:00', 18, 1),
('19191919191', '2025-10-17 10:00:00', 19, 1),
('19191919191', '2025-10-17 10:00:00', 20, 1),
('20202020202', '2025-10-18 11:00:00', 20, 1),
('21212121212', '2025-10-19 12:00:00', 21, 1),
('21212121212', '2025-10-19 12:00:00', 22, 1),
('21212121212', '2025-10-19 12:00:00', 23, 1),
('23232323232', '2025-10-05 08:00:00', 22, 1),
('24242424242', '2025-10-06 09:00:00', 1, 1),
('24242424242', '2025-10-06 09:00:00', 2, 1),
('25252525252', '2025-10-07 10:00:00', 24, 1),
('26262626262', '2025-10-08 11:00:00', 25, 1),
('26262626262', '2025-10-08 11:00:00', 1, 1),
('26262626262', '2025-10-08 11:00:00', 3, 1),
('27272727272', '2025-10-09 12:00:00', 6, 1),
('11111111111', '2025-10-10 13:00:00', 7, 1),
('11111111111', '2025-10-10 13:00:00', 8, 1),
('22222222222', '2025-10-11 14:00:00', 15, 1),

-- Produtos nos pedidos cancelados
('33333333333', '2025-10-12 08:00:00', 10, 1),
('44444444444', '2025-10-13 09:00:00', 11, 1),
('44444444444', '2025-10-13 09:00:00', 12, 1),
('55555555555', '2025-10-14 10:00:00', 11, 1);

-- ============================================
-- 11. ASSOCIAPROD (25 registros - relaciona produtos às solicitações)
-- ============================================
INSERT INTO AssociaProd (cpf_cliente, data_pedido, data_solicitacao, id_produto) VALUES
('23232323232', '2025-10-05 08:00:00', '2025-10-06 10:00:00', 22),
('24242424242', '2025-10-06 09:00:00', '2025-10-07 11:00:00', 1),
('25252525252', '2025-10-07 10:00:00', '2025-10-08 12:00:00', 24),
('26262626262', '2025-10-08 11:00:00', '2025-10-09 13:00:00', 25),
('27272727272', '2025-10-09 12:00:00', '2025-10-10 14:00:00', 6),
('11111111111', '2025-10-10 13:00:00', '2025-10-11 15:00:00', 7),
('22222222222', '2025-10-11 14:00:00', '2025-10-12 16:00:00', 15),
('17171717171', '2025-10-15 08:00:00', '2025-10-16 10:00:00', 17),
('18181818181', '2025-10-16 09:00:00', '2025-10-17 11:00:00', 18),
('19191919191', '2025-10-17 10:00:00', '2025-10-18 12:00:00', 19),
('20202020202', '2025-10-18 11:00:00', '2025-10-19 13:00:00', 20),
('21212121212', '2025-10-19 12:00:00', '2025-10-20 14:00:00', 21),
('12121212121', '2025-10-20 08:00:00', '2025-10-21 10:00:00', 12),
('13131313131', '2025-10-21 09:00:00', '2025-10-22 11:00:00', 1),
('14141414141', '2025-10-22 10:00:00', '2025-10-23 12:00:00', 14),
('15151515151', '2025-10-23 11:00:00', '2025-10-24 13:00:00', 15),
('16161616161', '2025-10-24 12:00:00', '2025-10-25 14:00:00', 16),
('66666666666', '2025-10-25 09:00:00', '2025-10-26 10:00:00', 7),
('77777777777', '2025-10-26 10:00:00', '2025-10-27 11:00:00', 8),
('88888888888', '2025-10-27 11:00:00', '2025-10-28 12:00:00', 9),
('99999999999', '2025-10-28 12:00:00', '2025-10-29 13:00:00', 10),
('10101010101', '2025-10-29 13:00:00', '2025-10-30 14:00:00', 11),
('33333333333', '2025-10-12 08:00:00', '2025-10-13 09:00:00', 10),
('44444444444', '2025-10-13 09:00:00', '2025-10-14 10:00:00', 11),
('55555555555', '2025-10-14 10:00:00', '2025-10-15 11:00:00', 11);

-- ============================================
-- 12. AVALIAPROD (25 registros - avaliações de produtos)
-- ============================================
INSERT INTO AvaliaProd (cpf_comprador, id_produto, nota) VALUES
('11111111111', 1, 5),
('11111111111', 2, 4),
('22222222222', 3, 5),
('33333333333', 4, 4),
('44444444444', 5, 3),
('55555555555', 6, 5),
('66666666666', 7, 4),
('77777777777', 8, 5),
('88888888888', 9, 4),
('99999999999', 10, 3),
('10101010101', 11, 5),
('12121212121', 12, 4),
('13131313131', 1, 5),
('13131313131', 2, 4),
('14141414141', 14, 5),
('15151515151', 15, 3),
('16161616161', 16, 4),
('17171717171', 17, 5),
('18181818181', 18, 4),
('19191919191', 19, 5),
('20202020202', 20, 3),
('21212121212', 21, 4),
('23232323232', 22, 5),
('24242424242', 1, 5),
('25252525252', 24, 4);

-- ============================================
-- 13. PREFERECAT (25 registros - preferências de categoria dos compradores)
-- ============================================
INSERT INTO PrefereCat (cpf_comprador, id_categoria) VALUES
('11111111111', 1),
('11111111111', 7),
('22222222222', 2),
('33333333333', 3),
('44444444444', 4),
('55555555555', 5),
('66666666666', 6),
('77777777777', 7),
('88888888888', 8),
('99999999999', 9),
('10101010101', 10),
('12121212121', 11),
('13131313131', 1),
('13131313131', 7),
('14141414141', 17),
('15151515151', 15),
('16161616161', 16),
('17171717171', 17),
('18181818181', 18),
('19191919191', 19),
('20202020202', 20),
('21212121212', 21),
('23232323232', 22),
('24242424242', 1),
('25252525252', 23);

-- ============================================
-- 14. PERTENCECAT (25 registros - produtos pertencem a categorias)
-- ============================================
INSERT INTO PertenceCat (id_categoria, id_produto) VALUES
(1, 1),
(7, 2),
(2, 3),
(3, 4),
(4, 5),
(5, 6),
(6, 7),
(7, 8),
(8, 9),
(9, 10),
(10, 11),
(11, 12),
(17, 13),
(17, 14),
(4, 15),
(7, 16),
(5, 17),
(8, 18),
(1, 19),
(15, 20),
(1, 21),
(21, 22),
(20, 23),
(10, 24),
(15, 25);

-- ============================================
-- 15. VENDEPROD (25 registros - vendedores vendem produtos)
-- ============================================
INSERT INTO VendeProd (cpf_vendedor, id_produto) VALUES
('11111111111', 1),
('11111111111', 2),
('11111111111', 19),
('22222222222', 3),
('33333333333', 4),
('44444444444', 5),
('44444444444', 15),
('55555555555', 6),
('55555555555', 17),
('66666666666', 7),
('77777777777', 8),
('77777777777', 16),
('88888888888', 9),
('88888888888', 18),
('99999999999', 10),
('10101010101', 11),
('12121212121', 12),
('13131313131', 13),
('14141414141', 14),
('15151515151', 20),
('16161616161', 25),
('17171717171', 21),
('18181818181', 22),
('19191919191', 23),
('20202020202', 24);
