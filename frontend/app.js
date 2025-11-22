const API_URL = 'http://localhost:8001';

// Navegação entre views
function showCompradorView() {
    document.getElementById('comprador-view').style.display = 'block';
    document.getElementById('vendedor-view').style.display = 'none';
}

function showVendedorView() {
    document.getElementById('comprador-view').style.display = 'none';
    document.getElementById('vendedor-view').style.display = 'block';
}

// ========== FUNCIONALIDADES DO COMPRADOR ==========

// Função auxiliar para obter o CPF do comprador
function obterCPFComprador() {
    return document.getElementById('comprador-cpf-principal').value.trim();
}

// Função auxiliar para formatar data para o backend
function formatarDataParaBackend(data) {
    if (!data) {
        console.error('Data não fornecida');
        return null;
    }
    
    try {
        // Se já é string no formato correto YYYY-MM-DD HH:MM:SS, retorna
        if (typeof data === 'string') {
            const dataLimpa = data.trim();
            
            // Remove timezone e outros caracteres extras
            let dataFormatada = dataLimpa;
            
            // Se tem timezone (Z, +, -), remove
            if (dataFormatada.includes('Z')) {
                dataFormatada = dataFormatada.replace('Z', '').trim();
            }
            if (dataFormatada.includes('+') || (dataFormatada.includes('-') && dataFormatada.indexOf('-') > 10)) {
                // Remove timezone (ex: +00:00, -03:00)
                dataFormatada = dataFormatada.replace(/[+-]\d{2}:?\d{2}$/, '').trim();
            }
            
            // Remove dia da semana e GMT (ex: "Wed, 01 Oct 2025 00:00:00 GMT")
            if (dataFormatada.includes('GMT') || dataFormatada.includes('UTC')) {
                // Tenta parsear como Date do JavaScript que entende esses formatos
                const dataObj = new Date(dataLimpa);
                if (!isNaN(dataObj.getTime())) {
                    dataFormatada = dataObj.toISOString().replace('T', ' ').replace('Z', '').substring(0, 19);
                }
            }
            
            // Converte T para espaço se necessário (formato ISO)
            if (dataFormatada.includes('T')) {
                dataFormatada = dataFormatada.replace('T', ' ').substring(0, 19);
            }
            
            // Verifica se está no formato correto YYYY-MM-DD HH:MM:SS
            if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(dataFormatada)) {
                return dataFormatada;
            }
            
            // Tenta parsear como Date object e reformatar
            const dataObj = new Date(dataLimpa);
            if (!isNaN(dataObj.getTime())) {
                const ano = dataObj.getFullYear();
                const mes = String(dataObj.getMonth() + 1).padStart(2, '0');
                const dia = String(dataObj.getDate()).padStart(2, '0');
                const horas = String(dataObj.getHours()).padStart(2, '0');
                const minutos = String(dataObj.getMinutes()).padStart(2, '0');
                const segundos = String(dataObj.getSeconds()).padStart(2, '0');
                
                return `${ano}-${mes}-${dia} ${horas}:${minutos}:${segundos}`;
            }
        }
        
        // Se é objeto Date
        if (data instanceof Date) {
            if (isNaN(data.getTime())) {
                console.error('Data inválida:', data);
                return null;
            }
            const ano = data.getFullYear();
            const mes = String(data.getMonth() + 1).padStart(2, '0');
            const dia = String(data.getDate()).padStart(2, '0');
            const horas = String(data.getHours()).padStart(2, '0');
            const minutos = String(data.getMinutes()).padStart(2, '0');
            const segundos = String(data.getSeconds()).padStart(2, '0');
            
            return `${ano}-${mes}-${dia} ${horas}:${minutos}:${segundos}`;
        }
    } catch (e) {
        console.error('Erro ao formatar data:', e, 'Data original:', data);
    }
    
    console.error('Formato de data inválido:', data, typeof data);
    return null;
}

async function buscarProdutos() {
    const nome = document.getElementById('search-nome').value;
    const origem = document.getElementById('search-origem').value;
    const loja = document.getElementById('search-loja').value;
    const precoMin = document.getElementById('search-preco-min').value;
    const precoMax = document.getElementById('search-preco-max').value;

    const params = new URLSearchParams();
    if (nome) params.append('nome', nome);
    if (origem) params.append('origem', origem);
    if (loja) params.append('loja', loja);
    if (precoMin) params.append('preco_min', precoMin);
    if (precoMax) params.append('preco_max', precoMax);

    try {
        const response = await fetch(`${API_URL}/produtos_comprador?${params}`);
        const produtos = await response.json();
        exibirProdutos(produtos);
    } catch (error) {
        console.error('Erro ao buscar produtos:', error);
        mostrarMensagem('Erro ao buscar produtos', 'error');
    }
}

function exibirProdutos(produtos) {
    const container = document.getElementById('produtos-lista');
    if (!produtos || produtos.length === 0) {
        container.innerHTML = '<p>Nenhum produto encontrado.</p>';
        return;
    }

    container.innerHTML = produtos.map(produto => `
        <div class="produto-card">
            <h4>${produto.nome_produto || 'Produto sem nome'}</h4>
            <div class="preco">R$ ${parseFloat(produto.preco || 0).toFixed(2)}</div>
            <div class="info">Loja: ${produto.nome_loja || 'N/A'}</div>
            <div class="info">Categoria: ${produto.nome_categoria || 'N/A'}</div>
            <div class="info">Origem: ${produto.origem || 'N/A'}</div>
            <div class="info estoque ${produto.estoque_atual > 0 ? 'ok' : ''}">
                Estoque: ${produto.estoque_atual || 0}
            </div>
            ${produto.media_nota ? `<div class="info">⭐ ${parseFloat(produto.media_nota).toFixed(1)}</div>` : ''}
            <div style="margin-top: 1rem;">
                <input type="number" id="qtd-produto-${produto.id_produto}" placeholder="Quantidade" value="1" min="1" style="margin-bottom: 0.5rem;">
                <button onclick="adicionarAoCarrinho(${produto.id_produto})" class="btn btn-primary" style="width: 100%;">
                    Adicionar ao Carrinho
                </button>
            </div>
        </div>
    `).join('');
}

// Variáveis globais para armazenar dados do produto que está sendo adicionado
let produtoPendente = null;

async function adicionarAoCarrinho(idProduto) {
    const cpf = obterCPFComprador();
    const quantidade = parseInt(document.getElementById(`qtd-produto-${idProduto}`).value) || 1;

    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/comprador/carrinho`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf, id_produto: idProduto, quantidade })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Produto adicionado ao carrinho!', 'success');
            produtoPendente = null; // Limpa produto pendente
        } else {
            // Verifica se o erro é porque o comprador não existe
            if (result.error === 'comprador_nao_existe' || response.status === 404) {
                // Armazena os dados do produto para adicionar depois do cadastro
                produtoPendente = { idProduto, quantidade };
                // Mostra o modal de cadastro
                mostrarModalCadastro(cpf);
            } else {
                mostrarMensagem(result.error || 'Erro ao adicionar produto', 'error');
            }
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao adicionar produto ao carrinho', 'error');
    }
}

function mostrarModalCadastro(cpf) {
    const modal = document.getElementById('modal-cadastro');
    const cpfInput = document.getElementById('cadastro-cpf');
    cpfInput.value = cpf;
    modal.style.display = 'block';
}

function fecharModalCadastro() {
    const modal = document.getElementById('modal-cadastro');
    modal.style.display = 'none';
    // Limpa o formulário
    document.getElementById('form-cadastro').reset();
    produtoPendente = null;
}

async function cadastrarComprador(event) {
    event.preventDefault();
    
    const cpf = document.getElementById('cadastro-cpf').value.trim();
    const pnome = document.getElementById('cadastro-pnome').value.trim();
    const sobrenome = document.getElementById('cadastro-sobrenome').value.trim();
    const cep = document.getElementById('cadastro-cep').value.trim();
    const email = document.getElementById('cadastro-email').value.trim();
    const senha = document.getElementById('cadastro-senha').value;

    // Validações básicas
    if (!cpf || cpf.length !== 11) {
        mostrarMensagem('CPF deve ter 11 dígitos', 'error');
        return;
    }

    if (!pnome || !sobrenome || !email || !senha) {
        mostrarMensagem('Por favor, preencha todos os campos obrigatórios', 'error');
        return;
    }

    if (cep && cep.length !== 8) {
        mostrarMensagem('CEP deve ter 8 dígitos', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/comprador/cadastrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf, pnome, sobrenome, cep: cep || null, email, senha })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Cadastro realizado com sucesso!', 'success');
            fecharModalCadastro();
            
            // Se havia um produto pendente, adiciona ao carrinho agora
            if (produtoPendente) {
                setTimeout(async () => {
                    try {
                        const carrinhoResponse = await fetch(`${API_URL}/comprador/carrinho`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                cpf, 
                                id_produto: produtoPendente.idProduto, 
                                quantidade: produtoPendente.quantidade 
                            })
                        });

                        const carrinhoResult = await carrinhoResponse.json();
                        if (carrinhoResponse.ok) {
                            mostrarMensagem('Produto adicionado ao carrinho!', 'success');
                        } else {
                            mostrarMensagem(carrinhoResult.error || 'Erro ao adicionar produto ao carrinho', 'error');
                        }
                    } catch (error) {
                        console.error('Erro ao adicionar produto após cadastro:', error);
                        mostrarMensagem('Erro ao adicionar produto ao carrinho', 'error');
                    }
                    produtoPendente = null;
                }, 500);
            }
        } else {
            mostrarMensagem(result.error || 'Erro ao cadastrar comprador', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao cadastrar comprador. Verifique sua conexão e tente novamente.', 'error');
    }
}

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('modal-cadastro');
    if (event.target === modal) {
        fecharModalCadastro();
    }
}

async function visualizarCarrinho() {
    const cpf = obterCPFComprador();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    const container = document.getElementById('carrinho-lista');
    container.innerHTML = '<p>Carregando carrinho...</p>';

    try {
        const response = await fetch(`${API_URL}/comprador/pedidos?cpf=${cpf}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status} ao buscar pedidos`);
        }
        
        const pedidos = await response.json();
        
        if (!pedidos || pedidos.length === 0) {
            container.innerHTML = '<p>Nenhum item no carrinho.</p>';
            return;
        }
        
        const pedidoPendente = pedidos.find(p => p.status_pedido === 'pendente');
        
        if (!pedidoPendente) {
            container.innerHTML = '<p>Nenhum item no carrinho. Adicione produtos para ver seu carrinho aqui.</p>';
            return;
        }

        // Se o pedido não tem produtos ainda, mostra mensagem
        if (!pedidoPendente.total_produtos || pedidoPendente.total_produtos === 0) {
            container.innerHTML = '<p>Seu carrinho está vazio. Adicione produtos para ver seu carrinho aqui.</p>';
            return;
        }

        // Tenta buscar detalhes do pedido para mostrar os itens
        const dataPedidoFormatada = formatarDataParaBackend(pedidoPendente.data_pedido);
        let detalhes = null;
        
        if (dataPedidoFormatada) {
            try {
                const detalhesResponse = await fetch(`${API_URL}/comprador/pedido?cpf=${cpf}&data_pedido=${encodeURIComponent(dataPedidoFormatada)}`);
                
                if (detalhesResponse.ok) {
                    detalhes = await detalhesResponse.json();
                } else {
                    console.warn('Não foi possível buscar detalhes do pedido, mas mostraremos o resumo');
                }
            } catch (e) {
                console.warn('Erro ao buscar detalhes do pedido:', e);
            }
        }
        
        // Formatar data do pedido para o botão de finalizar
        const dataPedidoParaBotao = dataPedidoFormatada || pedidoPendente.data_pedido;
        
        container.innerHTML = `
            <div class="carrinho-item" style="background-color: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>Pedido Pendente</h4>
                <p><strong>Total:</strong> R$ ${parseFloat(pedidoPendente.total_pedido || 0).toFixed(2)}</p>
                <p><strong>Quantidade de itens:</strong> ${pedidoPendente.total_produtos || 0}</p>
                ${detalhes && detalhes.itens && detalhes.itens.length > 0 ? `
                    <h5 style="margin-top: 1rem;">Itens do carrinho:</h5>
                    <ul style="margin-top: 0.5rem; list-style: none; padding: 0;">
                        ${detalhes.itens.map(item => `
                            <li style="padding: 0.5rem; background-color: #f9f9f9; margin-bottom: 0.5rem; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>${item.nome_produto}</strong> - Qtd: ${item.quantidade} - R$ ${parseFloat(item.subtotal || 0).toFixed(2)}
                                </div>
                                <button onclick="removerDoCarrinho(${item.id_produto})" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.875rem; margin-left: 1rem;">
                                    Remover
                                </button>
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="margin-top: 1rem; color: #666;">Detalhes dos itens não disponíveis no momento.</p>'}
                <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #ddd;">
                    <input type="text" id="endereco-entrega" placeholder="Endereço de entrega" style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem; box-sizing: border-box;">
                    <select id="metodo-entrega" style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem; box-sizing: border-box;">
                        <option value="">Selecione o método de entrega</option>
                        <option value="Correios">Correios</option>
                        <option value="PAC">PAC</option>
                        <option value="Motoboy">Motoboy</option>
                    </select>
                    <select id="metodo-pagamento" style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem; box-sizing: border-box;">
                        <option value="">Selecione o método de pagamento</option>
                        <option value="credito">Crédito</option>
                        <option value="debito">Débito</option>
                        <option value="pix">Pix</option>
                    </select>
                    <button onclick="finalizarPedido('${cpf}', '${dataPedidoParaBotao}')" class="btn btn-success" style="width: 100%;">
                        Finalizar Pedido
                    </button>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Erro:', error);
        container.innerHTML = '<p style="padding: 1rem; background-color: #f8d7da; border-radius: 4px; color: #721c24;">Erro ao carregar o carrinho. Por favor, tente novamente.</p>';
        mostrarMensagem('Erro ao visualizar carrinho', 'error');
    }
}

async function removerDoCarrinho(idProduto) {
    const cpf = obterCPFComprador();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    if (!confirm('Deseja remover este item do carrinho?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/comprador/carrinho/${idProduto}?cpf=${cpf}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Item removido do carrinho!', 'success');
            // Atualizar visualização do carrinho
            setTimeout(() => {
                visualizarCarrinho();
            }, 300);
        } else {
            mostrarMensagem(result.error || 'Erro ao remover item do carrinho', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao remover item do carrinho', 'error');
    }
}

async function finalizarPedido(cpf, dataPedido) {
    const endereco = document.getElementById('endereco-entrega').value.trim();
    const metodoEntrega = document.getElementById('metodo-entrega').value.trim();
    const metodoPagamento = document.getElementById('metodo-pagamento').value.trim();

    if (!endereco || !metodoEntrega || !metodoPagamento) {
        mostrarMensagem('Por favor, preencha endereço, método de entrega e método de pagamento', 'error');
        return;
    }

    // Verifica CPF
    if (!cpf) {
        cpf = obterCPFComprador();
        if (!cpf) {
            mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
            return;
        }
    }

    try {
        const response = await fetch(`${API_URL}/comprador/pedido/finalizar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cpf: cpf, 
                metodo_pagamento: metodoPagamento, 
                metodo_entrega: metodoEntrega,
                endereco_entrega: endereco 
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Pedido finalizado com sucesso!', 'success');
            // Limpar campos
            const enderecoInput = document.getElementById('endereco-entrega');
            const metodoEntregaInput = document.getElementById('metodo-entrega');
            const metodoPagamentoInput = document.getElementById('metodo-pagamento');
            if (enderecoInput) enderecoInput.value = '';
            if (metodoEntregaInput) metodoEntregaInput.value = '';
            if (metodoPagamentoInput) metodoPagamentoInput.value = '';
            // Atualizar carrinho e lista de pedidos após um delay
            setTimeout(() => {
                visualizarCarrinho();
                // Atualizar lista de pedidos também para mostrar o novo pedido finalizado
                if (typeof visualizarPedidos === 'function') {
                    visualizarPedidos();
                }
            }, 500);
        } else {
            console.error('Erro ao finalizar pedido:', result);
            mostrarMensagem(result.error || 'Erro ao finalizar pedido. Verifique se há produtos no carrinho.', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao finalizar pedido. Verifique sua conexão e tente novamente.', 'error');
    }
}

async function visualizarPedidos() {
    const cpf = obterCPFComprador();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/comprador/pedidos?cpf=${cpf}`);
        const pedidos = await response.json();
        const container = document.getElementById('pedidos-lista');
        
        if (!pedidos || pedidos.length === 0) {
            container.innerHTML = '<p>Nenhum pedido encontrado.</p>';
            return;
        }

        container.innerHTML = pedidos.map(pedido => {
            // Formatar data para o botão
            const dataPedidoFormatada = formatarDataParaBackend(pedido.data_pedido) || pedido.data_pedido;
            
            return `
            <div class="pedido-item">
                <h4>Pedido de ${new Date(pedido.data_pedido).toLocaleString('pt-BR')}</h4>
                <p><strong>Status:</strong> <span class="status ${pedido.status_pedido}">${pedido.status_pedido}</span></p>
                <p><strong>Total:</strong> R$ ${parseFloat(pedido.total_pedido || 0).toFixed(2)}</p>
                <p><strong>Itens:</strong> ${pedido.total_produtos || 0}</p>
                ${pedido.status_pagamento ? `<p><strong>Pagamento:</strong> ${pedido.status_pagamento} ${pedido.metodo_pagamento ? `(${pedido.metodo_pagamento})` : ''}</p>` : ''}
                ${pedido.status_entrega ? `<p><strong>Entrega:</strong> ${pedido.status_entrega} ${pedido.metodo_entrega ? `(${pedido.metodo_entrega})` : ''}</p>` : ''}
                ${pedido.endereco_entrega ? `<p><strong>Endereço:</strong> ${pedido.endereco_entrega}</p>` : ''}
                ${pedido.status_pagamento === 'pendente' ? `
                    <button onclick="simularPagamento('${cpf}', '${dataPedidoFormatada}')" class="btn btn-success" style="margin-top: 0.5rem;">
                        Simular Pagamento
                    </button>
                ` : ''}
                <button onclick="criarSolicitacao('${cpf}', '${pedido.data_pedido}')" class="btn btn-secondary" style="margin-top: 0.5rem;">
                    Criar Solicitação
                </button>
            </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao visualizar pedidos', 'error');
    }
}

async function simularPagamento(cpf, dataPedido) {
    if (!confirm('Deseja simular o pagamento deste pedido? O status será atualizado para "aprovado".')) {
        return;
    }

    const cpfAtual = cpf || obterCPFComprador();
    if (!cpfAtual) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    // Formatar data para o backend
    const dataPedidoFormatada = formatarDataParaBackend(dataPedido);
    if (!dataPedidoFormatada) {
        mostrarMensagem('Erro ao formatar data do pedido', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/comprador/pedido/simular-pagamento`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cpf: cpfAtual, 
                data_pedido: dataPedidoFormatada 
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Pagamento simulado com sucesso! Status atualizado para "aprovado".', 'success');
            // Atualizar lista de pedidos após um delay
            setTimeout(() => {
                visualizarPedidos();
            }, 500);
        } else {
            mostrarMensagem(result.error || 'Erro ao simular pagamento', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao simular pagamento. Verifique sua conexão e tente novamente.', 'error');
    }
}

async function criarSolicitacao(cpf, dataPedido) {
    const tipo = prompt('Tipo de solicitação (devolucao, troca, suporte, cancelamento):');
    if (!tipo) return;

    try {
        const response = await fetch(`${API_URL}/comprador/pedido/solicitacao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf, data_pedido: dataPedido, tipo })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Solicitação criada com sucesso!', 'success');
        } else {
            mostrarMensagem(result.error || 'Erro ao criar solicitação', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao criar solicitação', 'error');
    }
}

async function carregarProdutosComprados() {
    const cpf = obterCPFComprador();
    if (!cpf) {
        const selectProduto = document.getElementById('avaliacao-produto');
        selectProduto.innerHTML = '<option value="">Informe seu CPF primeiro</option>';
        selectProduto.disabled = true;
        return;
    }

    const selectProduto = document.getElementById('avaliacao-produto');
    selectProduto.innerHTML = '<option value="">Carregando produtos...</option>';
    selectProduto.disabled = true;

    try {
        const response = await fetch(`${API_URL}/comprador/produtos-comprados?cpf=${cpf}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}`);
        }
        
        const produtos = await response.json();
        
        if (!produtos || produtos.length === 0) {
            selectProduto.innerHTML = '<option value="">Nenhum produto comprado encontrado</option>';
            selectProduto.disabled = false;
            return;
        }

        selectProduto.innerHTML = '<option value="">Selecione um produto que você comprou</option>';
        produtos.forEach(produto => {
            const option = document.createElement('option');
            option.value = produto.id_produto;
            option.textContent = `${produto.nome_produto} - R$ ${parseFloat(produto.preco || 0).toFixed(2)}`;
            selectProduto.appendChild(option);
        });
        
        selectProduto.disabled = false;
    } catch (error) {
        console.error('Erro:', error);
        selectProduto.innerHTML = '<option value="">Erro ao carregar produtos</option>';
        selectProduto.disabled = false;
    }
}

async function avaliarProduto() {
    const cpf = obterCPFComprador();
    const idProduto = parseInt(document.getElementById('avaliacao-produto').value);
    const nota = parseInt(document.getElementById('avaliacao-nota').value);

    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    if (!idProduto || !nota) {
        mostrarMensagem('Por favor, selecione um produto e informe a nota', 'error');
        return;
    }

    if (nota < 1 || nota > 5) {
        mostrarMensagem('A nota deve estar entre 1 e 5', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/comprador/avaliacao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf, id_produto: idProduto, nota })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Produto avaliado com sucesso!', 'success');
            // Limpa os campos após avaliação
            document.getElementById('avaliacao-nota').value = '';
            document.getElementById('avaliacao-produto').value = '';
        } else {
            mostrarMensagem(result.error || 'Erro ao avaliar produto', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao avaliar produto', 'error');
    }
}

// ========== FUNCIONALIDADES DO VENDEDOR ==========

async function carregarDadosVendedor() {
    const cpf = document.getElementById('vendedor-cpf').value;
    if (!cpf) {
        mostrarMensagem('Por favor, informe o CPF', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor?cpf=${cpf}`);
        const vendedor = await response.json();
        const container = document.getElementById('vendedor-info');
        
        if (vendedor && !vendedor.error) {
            container.innerHTML = `
                <div class="stat-card">
                    <h4>${vendedor.nome_loja || 'Loja'}</h4>
                    <p>${vendedor.desc_loja || 'Sem descrição'}</p>
                    <p><strong>CPF:</strong> ${vendedor.cpf}</p>
                    <p><strong>Email:</strong> ${vendedor.email}</p>
                    <p><strong>CEP:</strong> ${vendedor.cep}</p>
                    <p><strong>Nome:</strong> ${vendedor.pnome} ${vendedor.sobrenome}</p>
                </div>
            `;
        } else {
            container.innerHTML = '<p>Vendedor não encontrado.</p>';
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar dados do vendedor', 'error');
    }
}

async function carregarEstatisticas() {
    const cpf = document.getElementById('stats-cpf').value;
    const meses = parseInt(document.getElementById('stats-periodo').value);
    
    if (!cpf) {
        mostrarMensagem('Por favor, informe o CPF', 'error');
        return;
    }

    try {
        const [maisVendidos, lucro, estoqueBaixo, maisDevolvidos, melhorAvaliacao] = await Promise.all([
            fetch(`${API_URL}/vendedor/produtos/mais-vendidos?cpf=${cpf}&meses=${meses}`).then(r => r.json()),
            fetch(`${API_URL}/vendedor/lucro?cpf=${cpf}&meses=${meses}`).then(r => r.json()),
            fetch(`${API_URL}/vendedor/produtos/estoque-baixo?cpf=${cpf}`).then(r => r.json()),
            fetch(`${API_URL}/vendedor/produtos/mais-devolvidos?cpf=${cpf}&meses=${meses}`).then(r => r.json()),
            fetch(`${API_URL}/vendedor/produtos/melhor-avaliacao?cpf=${cpf}`).then(r => r.json())
        ]);

        const container = document.getElementById('estatisticas');
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Receita Total</h4>
                    <div class="value">R$ ${parseFloat(lucro.receita_total || 0).toFixed(2)}</div>
                    <p>${lucro.total_vendas || 0} vendas</p>
                </div>
                <div class="stat-card">
                    <h4>Produtos Vendidos</h4>
                    <div class="value">${lucro.total_produtos_vendidos || 0}</div>
                </div>
            </div>
            
            <h4 style="margin-top: 2rem;">Top 3 Produtos Mais Vendidos</h4>
            <div class="produtos-grid">
                ${maisVendidos.map(p => `
                    <div class="produto-card">
                        <h4>${p.nome_produto}</h4>
                        <div class="preco">${p.total_vendido} unidades</div>
                        <div class="info">R$ ${parseFloat(p.preco).toFixed(2)}</div>
                    </div>
                `).join('')}
            </div>

            <h4 style="margin-top: 2rem;">Produtos com Estoque Baixo</h4>
            <div class="produtos-grid">
                ${estoqueBaixo.map(p => `
                    <div class="produto-card">
                        <h4>${p.nome_produto}</h4>
                        <div class="info estoque">Estoque: ${p.estoque_atual}</div>
                        <div class="info">Alerta: ${p.alerta_estoque}</div>
                    </div>
                `).join('')}
            </div>

            ${melhorAvaliacao.length > 0 ? `
                <h4 style="margin-top: 2rem;">Produtos Melhor Avaliados</h4>
                <div class="produtos-grid">
                    ${melhorAvaliacao.slice(0, 5).map(p => `
                        <div class="produto-card">
                            <h4>${p.nome_produto}</h4>
                            <div class="info">⭐ ${parseFloat(p.media_avaliacao).toFixed(1)}</div>
                            <div class="info">${p.total_avaliacoes} avaliações</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar estatísticas', 'error');
    }
}

async function carregarProdutosVendedor() {
    const cpf = document.getElementById('produtos-vendedor-cpf').value;
    if (!cpf) {
        mostrarMensagem('Por favor, informe o CPF', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/produtos?cpf=${cpf}`);
        const produtos = await response.json();
        const container = document.getElementById('produtos-vendedor-lista');
        
        if (!produtos || produtos.length === 0) {
            container.innerHTML = '<p>Nenhum produto encontrado.</p>';
            return;
        }

        container.innerHTML = produtos.map(produto => `
            <div class="produto-vendedor-card">
                <div class="info">
                    <h4>${produto.nome_produto}</h4>
                    <p>${produto.desc_produto || 'Sem descrição'}</p>
                    <p><strong>Preço:</strong> R$ ${parseFloat(produto.preco).toFixed(2)}</p>
                    <p><strong>Estoque:</strong> ${produto.estoque_atual} | <strong>Alerta:</strong> ${produto.alerta_estoque}</p>
                    ${produto.media_avaliacao > 0 ? `<p>⭐ ${parseFloat(produto.media_avaliacao).toFixed(1)}</p>` : ''}
                </div>
                <div class="actions">
                    <input type="number" id="estoque-${produto.id_produto}" placeholder="Novo estoque" min="0">
                    <button onclick="atualizarEstoque('${cpf}', ${produto.id_produto})" class="btn btn-primary">Atualizar Estoque</button>
                    <button onclick="removerProduto('${cpf}', ${produto.id_produto})" class="btn btn-danger">Remover</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar produtos', 'error');
    }
}

async function atualizarEstoque(cpf, idProduto) {
    const novaQuantidade = parseInt(document.getElementById(`estoque-${idProduto}`).value);
    
    if (isNaN(novaQuantidade) || novaQuantidade < 0) {
        mostrarMensagem('Por favor, informe uma quantidade válida', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/produtos/${idProduto}/estoque`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf, quantidade: novaQuantidade })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Estoque atualizado com sucesso!', 'success');
            carregarProdutosVendedor();
        } else {
            mostrarMensagem(result.error || 'Erro ao atualizar estoque', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao atualizar estoque', 'error');
    }
}

async function removerProduto(cpf, idProduto) {
    if (!confirm('Tem certeza que deseja remover este produto?')) return;

    try {
        const response = await fetch(`${API_URL}/vendedor/produtos/${idProduto}?cpf=${cpf}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Produto removido com sucesso!', 'success');
            carregarProdutosVendedor();
        } else {
            mostrarMensagem(result.error || 'Erro ao remover produto', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao remover produto', 'error');
    }
}

async function adicionarProduto() {
    const cpf = document.getElementById('novo-produto-cpf').value;
    const nome = document.getElementById('novo-produto-nome').value;
    const descricao = document.getElementById('novo-produto-desc').value;
    const preco = parseFloat(document.getElementById('novo-produto-preco').value);
    const estoque = parseInt(document.getElementById('novo-produto-estoque').value) || 0;
    const alerta = parseInt(document.getElementById('novo-produto-alerta').value) || 0;
    const origem = document.getElementById('novo-produto-origem').value;

    if (!cpf || !nome || isNaN(preco)) {
        mostrarMensagem('Por favor, preencha CPF, nome e preço', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/produtos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpf,
                nome,
                descricao,
                preco,
                estoque,
                alerta_estoque: alerta,
                origem
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Produto adicionado com sucesso!', 'success');
            // Limpar formulário
            document.getElementById('novo-produto-nome').value = '';
            document.getElementById('novo-produto-desc').value = '';
            document.getElementById('novo-produto-preco').value = '';
            document.getElementById('novo-produto-estoque').value = '0';
            document.getElementById('novo-produto-alerta').value = '0';
            document.getElementById('novo-produto-origem').value = '';
        } else {
            mostrarMensagem(result.error || 'Erro ao adicionar produto', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao adicionar produto', 'error');
    }
}

// Função auxiliar para mostrar mensagens
function mostrarMensagem(texto, tipo) {
    const mensagem = document.createElement('div');
    mensagem.className = `message ${tipo}`;
    mensagem.textContent = texto;
    document.querySelector('.container').insertBefore(mensagem, document.querySelector('.container').firstChild);
    
    setTimeout(() => {
        mensagem.remove();
    }, 5000);
}

// Carregar produtos ao iniciar
window.onload = function() {
    buscarProdutos();
};

