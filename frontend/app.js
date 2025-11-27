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

// Função auxiliar para obter o CPF do vendedor
function obterCPFVendedor() {
    return document.getElementById('vendedor-cpf-principal').value.trim();
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

async function carregarCategorias() {
    try {
        const response = await fetch(`${API_URL}/categorias`);
        const categorias = await response.json();
        const selectCategoria = document.getElementById('search-categoria');
        
        // Limpa opções existentes (exceto a primeira)
        selectCategoria.innerHTML = '<option value="">Todas as categorias</option>';
        
        // Adiciona categorias
        categorias.forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria.nome_categoria;
            option.textContent = categoria.nome_categoria;
            selectCategoria.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar categorias:', error);
    }
}

async function buscarProdutos() {
    const nome = document.getElementById('search-nome').value;
    const categoria = document.getElementById('search-categoria').value;
    const origem = document.getElementById('search-origem').value;
    const loja = document.getElementById('search-loja').value;
    const precoMin = document.getElementById('search-preco-min').value;
    const precoMax = document.getElementById('search-preco-max').value;

    const params = new URLSearchParams();
    if (nome) params.append('nome', nome);
    if (categoria) params.append('categoria', categoria);
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
            // Atualiza a visualização do carrinho após um pequeno delay para garantir que o backend atualizou os totais
            setTimeout(() => {
                visualizarCarrinho();
            }, 300);
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

async function mostrarModalCadastro(cpf) {
    const modal = document.getElementById('modal-cadastro');
    const cpfInput = document.getElementById('cadastro-cpf');
    cpfInput.value = cpf;
    
    // Verifica se o usuário já existe
    try {
        const response = await fetch(`${API_URL}/comprador/verificar-usuario?cpf=${cpf}`);
        const info = await response.json();
        
        if (info.usuario_existe && !info.comprador_existe) {
            // Usuário existe mas não é comprador - preenche campos automaticamente
            if (info.dados_usuario) {
                document.getElementById('cadastro-pnome').value = info.dados_usuario.pnome || '';
                document.getElementById('cadastro-sobrenome').value = info.dados_usuario.sobrenome || '';
                document.getElementById('cadastro-cep').value = info.dados_usuario.cep || '';
                document.getElementById('cadastro-email').value = info.dados_usuario.email || '';
                // Torna campos readonly e oculta senha
                document.getElementById('cadastro-pnome').readOnly = true;
                document.getElementById('cadastro-sobrenome').readOnly = true;
                document.getElementById('cadastro-cep').readOnly = true;
                document.getElementById('cadastro-email').readOnly = true;
                document.getElementById('cadastro-senha').style.display = 'none';
                document.getElementById('cadastro-senha').required = false;
                // Adiciona label informativo
                const form = document.getElementById('form-cadastro');
                let infoMsg = form.querySelector('.info-usuario-existente');
                if (!infoMsg) {
                    infoMsg = document.createElement('p');
                    infoMsg.className = 'info-usuario-existente';
                    infoMsg.style.cssText = 'color: #28a745; font-size: 0.9rem; margin-bottom: 1rem;';
                    infoMsg.textContent = '✓ Usuário já cadastrado. Apenas será criado o perfil de comprador.';
                    form.insertBefore(infoMsg, form.firstChild);
                }
            }
        } else {
            // Novo usuário - campos editáveis
            document.getElementById('cadastro-pnome').readOnly = false;
            document.getElementById('cadastro-sobrenome').readOnly = false;
            document.getElementById('cadastro-cep').readOnly = false;
            document.getElementById('cadastro-email').readOnly = false;
            document.getElementById('cadastro-senha').style.display = 'block';
            document.getElementById('cadastro-senha').required = true;
            const infoMsg = document.querySelector('.info-usuario-existente');
            if (infoMsg) infoMsg.remove();
        }
    } catch (error) {
        console.error('Erro ao verificar usuário:', error);
        // Em caso de erro, mantém comportamento padrão (novo usuário)
    }
    
    modal.style.display = 'block';
}

function fecharModalCadastro() {
    const modal = document.getElementById('modal-cadastro');
    modal.style.display = 'none';
    // Limpa o formulário e restaura campos
    const form = document.getElementById('form-cadastro');
    form.reset();
    document.getElementById('cadastro-pnome').readOnly = false;
    document.getElementById('cadastro-sobrenome').readOnly = false;
    document.getElementById('cadastro-cep').readOnly = false;
    document.getElementById('cadastro-email').readOnly = false;
    document.getElementById('cadastro-senha').style.display = 'block';
    document.getElementById('cadastro-senha').required = true;
    const infoMsg = form.querySelector('.info-usuario-existente');
    if (infoMsg) infoMsg.remove();
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
    const senhaOculta = document.getElementById('cadastro-senha').style.display === 'none';

    // Validações básicas
    if (!cpf || cpf.length !== 11) {
        mostrarMensagem('CPF deve ter 11 dígitos', 'error');
        return;
    }

    // Se senha está oculta, usuário já existe - não precisa de senha
    if (!senhaOculta && !senha) {
        mostrarMensagem('Por favor, preencha a senha', 'error');
        return;
    }

    if (!pnome || !sobrenome || !email) {
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
            body: JSON.stringify({ 
                cpf, 
                pnome, 
                sobrenome, 
                cep: cep || null, 
                email, 
                senha: senhaOculta ? null : senha 
            })
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
                            // Atualiza a visualização do carrinho
                            setTimeout(() => {
                                visualizarCarrinho();
                            }, 300);
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

async function mostrarModalCadastroVendedor(cpf) {
    const modal = document.getElementById('modal-cadastro-vendedor');
    const cpfInput = document.getElementById('cadastro-vendedor-cpf');
    cpfInput.value = cpf;
    
    // Verifica se o usuário já existe
    try {
        const response = await fetch(`${API_URL}/vendedor/verificar-usuario?cpf=${cpf}`);
        const info = await response.json();
        
        if (info.usuario_existe && !info.vendedor_existe) {
            // Usuário existe mas não é vendedor - preenche campos automaticamente
            if (info.dados_usuario) {
                document.getElementById('cadastro-vendedor-pnome').value = info.dados_usuario.pnome || '';
                document.getElementById('cadastro-vendedor-sobrenome').value = info.dados_usuario.sobrenome || '';
                document.getElementById('cadastro-vendedor-cep').value = info.dados_usuario.cep || '';
                document.getElementById('cadastro-vendedor-email').value = info.dados_usuario.email || '';
                // Torna campos readonly e oculta senha
                document.getElementById('cadastro-vendedor-pnome').readOnly = true;
                document.getElementById('cadastro-vendedor-sobrenome').readOnly = true;
                document.getElementById('cadastro-vendedor-cep').readOnly = true;
                document.getElementById('cadastro-vendedor-email').readOnly = true;
                document.getElementById('cadastro-vendedor-senha').style.display = 'none';
                document.getElementById('cadastro-vendedor-senha').required = false;
                // Adiciona label informativo
                const form = document.getElementById('form-cadastro-vendedor');
                let infoMsg = form.querySelector('.info-usuario-existente');
                if (!infoMsg) {
                    infoMsg = document.createElement('p');
                    infoMsg.className = 'info-usuario-existente';
                    infoMsg.style.cssText = 'color: #28a745; font-size: 0.9rem; margin-bottom: 1rem;';
                    infoMsg.textContent = '✓ Usuário já cadastrado. Apenas preencha os dados da loja.';
                    form.insertBefore(infoMsg, form.firstChild);
                }
            }
        } else {
            // Novo usuário - campos editáveis
            document.getElementById('cadastro-vendedor-pnome').readOnly = false;
            document.getElementById('cadastro-vendedor-sobrenome').readOnly = false;
            document.getElementById('cadastro-vendedor-cep').readOnly = false;
            document.getElementById('cadastro-vendedor-email').readOnly = false;
            document.getElementById('cadastro-vendedor-senha').style.display = 'block';
            document.getElementById('cadastro-vendedor-senha').required = true;
            const infoMsg = document.querySelector('.info-usuario-existente');
            if (infoMsg) infoMsg.remove();
        }
    } catch (error) {
        console.error('Erro ao verificar usuário:', error);
        // Em caso de erro, mantém comportamento padrão (novo usuário)
    }
    
    modal.style.display = 'block';
}

function fecharModalCadastroVendedor() {
    const modal = document.getElementById('modal-cadastro-vendedor');
    modal.style.display = 'none';
    // Limpa o formulário e restaura campos
    const form = document.getElementById('form-cadastro-vendedor');
    form.reset();
    document.getElementById('cadastro-vendedor-pnome').readOnly = false;
    document.getElementById('cadastro-vendedor-sobrenome').readOnly = false;
    document.getElementById('cadastro-vendedor-cep').readOnly = false;
    document.getElementById('cadastro-vendedor-email').readOnly = false;
    document.getElementById('cadastro-vendedor-senha').style.display = 'block';
    document.getElementById('cadastro-vendedor-senha').required = true;
    const infoMsg = form.querySelector('.info-usuario-existente');
    if (infoMsg) infoMsg.remove();
    produtoPendenteVendedor = null;
}

async function cadastrarVendedor(event) {
    event.preventDefault();
    
    const cpf = document.getElementById('cadastro-vendedor-cpf').value.trim();
    const pnome = document.getElementById('cadastro-vendedor-pnome').value.trim();
    const sobrenome = document.getElementById('cadastro-vendedor-sobrenome').value.trim();
    const cep = document.getElementById('cadastro-vendedor-cep').value.trim();
    const email = document.getElementById('cadastro-vendedor-email').value.trim();
    const senha = document.getElementById('cadastro-vendedor-senha').value;
    const nomeLoja = document.getElementById('cadastro-vendedor-nome-loja').value.trim();
    const descLoja = document.getElementById('cadastro-vendedor-desc-loja').value.trim();
    const senhaOculta = document.getElementById('cadastro-vendedor-senha').style.display === 'none';

    // Validações básicas
    if (!cpf || cpf.length !== 11) {
        mostrarMensagem('CPF deve ter 11 dígitos', 'error');
        return;
    }

    if (!nomeLoja) {
        mostrarMensagem('Nome da loja é obrigatório', 'error');
        return;
    }

    // Se senha está oculta, usuário já existe - não precisa de senha
    if (!senhaOculta && !senha) {
        mostrarMensagem('Por favor, preencha a senha', 'error');
        return;
    }

    if (!pnome || !sobrenome || !email) {
        mostrarMensagem('Por favor, preencha todos os campos obrigatórios', 'error');
        return;
    }

    if (cep && cep.length !== 8) {
        mostrarMensagem('CEP deve ter 8 dígitos', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/cadastrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cpf, 
                pnome, 
                sobrenome, 
                cep: cep || null, 
                email, 
                senha: senhaOculta ? null : senha, 
                nome_loja: nomeLoja, 
                desc_loja: descLoja || null 
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Cadastro realizado com sucesso!', 'success');
            fecharModalCadastroVendedor();
            
            // Se havia um produto pendente, adiciona agora
            if (produtoPendenteVendedor) {
                setTimeout(async () => {
                    try {
                        const produtoResponse = await fetch(`${API_URL}/vendedor/produtos`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                cpf,
                                nome: produtoPendenteVendedor.nome,
                                descricao: produtoPendenteVendedor.descricao,
                                preco: produtoPendenteVendedor.preco,
                                estoque: produtoPendenteVendedor.estoque,
                                alerta_estoque: produtoPendenteVendedor.alerta,
                                origem: produtoPendenteVendedor.origem
                            })
                        });

                        const produtoResult = await produtoResponse.json();
                        if (produtoResponse.ok) {
                            mostrarMensagem('Produto adicionado com sucesso!', 'success');
                            carregarProdutosVendedor();
                        } else {
                            mostrarMensagem(produtoResult.error || 'Erro ao adicionar produto', 'error');
                        }
                    } catch (error) {
                        console.error('Erro ao adicionar produto após cadastro:', error);
                        mostrarMensagem('Erro ao adicionar produto', 'error');
                    }
                    produtoPendenteVendedor = null;
                }, 500);
            } else {
                // Recarrega dados do vendedor se estava tentando carregar
                carregarDadosVendedor();
            }
        } else {
            mostrarMensagem(result.error || 'Erro ao cadastrar vendedor', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao cadastrar vendedor. Verifique sua conexão e tente novamente.', 'error');
    }
}

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modalCadastro = document.getElementById('modal-cadastro');
    const modalCadastroVendedor = document.getElementById('modal-cadastro-vendedor');
    const modalEntrega = document.getElementById('modal-entrega');
    if (event.target === modalCadastro) {
        fecharModalCadastro();
    }
    if (event.target === modalCadastroVendedor) {
        fecharModalCadastroVendedor();
    }
    if (event.target === modalEntrega) {
        fecharModalEntrega();
    }
}

async function verDetalhesEntrega(cpf, dataPedido) {
    if (!cpf) {
        cpf = obterCPFComprador();
        if (!cpf) {
            mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
            return;
        }
    }

    try {
        const response = await fetch(`${API_URL}/comprador/pedido?cpf=${cpf}&data_pedido=${encodeURIComponent(dataPedido)}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status} ao buscar detalhes do pedido`);
        }
        
        const pedido = await response.json();
        
        if (!pedido) {
            mostrarMensagem('Pedido não encontrado', 'error');
            return;
        }

        // Formata as datas
        const formatarData = (data) => {
            if (!data) return 'Não informado';
            try {
                return new Date(data).toLocaleString('pt-BR');
            } catch (e) {
                return data;
            }
        };

        const conteudo = `
            <div style="margin-top: 1.5rem;">
                <div style="margin-bottom: 1rem; padding: 1rem; background-color: #f9fafb; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">Informações da Entrega</h3>
                    <p><strong>Status:</strong> <span class="status ${pedido.status_entrega || ''}">${pedido.status_entrega || 'Não informado'}</span></p>
                    <p><strong>Método de Entrega:</strong> ${pedido.metodo_entrega || 'Não informado'}</p>
                    <p><strong>Endereço:</strong> ${pedido.endereco_entrega || 'Não informado'}</p>
                    <p><strong>Frete:</strong> R$ ${parseFloat(pedido.frete || 0).toFixed(2)}</p>
                </div>
                <div style="margin-bottom: 1rem; padding: 1rem; background-color: #f9fafb; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">Datas</h3>
                    <p><strong>Data de Envio:</strong> ${formatarData(pedido.data_envio)}</p>
                    <p><strong>Data Prevista:</strong> ${formatarData(pedido.data_prevista)}</p>
                </div>
            </div>
        `;

        document.getElementById('detalhes-entrega-conteudo').innerHTML = conteudo;
        document.getElementById('modal-entrega').style.display = 'block';
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar detalhes da entrega', 'error');
    }
}

function fecharModalEntrega() {
    const modal = document.getElementById('modal-entrega');
    modal.style.display = 'none';
    document.getElementById('detalhes-entrega-conteudo').innerHTML = '';
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
        const response = await fetch(`${API_URL}/comprador/carrinho?cpf=${cpf}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status} ao buscar carrinho`);
        }
        
        const pedidoCarrinho = await response.json();
        
        if (!pedidoCarrinho) {
            container.innerHTML = '<p>Nenhum item no carrinho. Adicione produtos para ver seu carrinho aqui.</p>';
            return;
        }

        // Se o pedido não tem produtos ainda, mostra mensagem
        if (!pedidoCarrinho.total_produtos || pedidoCarrinho.total_produtos === 0) {
            container.innerHTML = '<p>Seu carrinho está vazio. Adicione produtos para ver seu carrinho aqui.</p>';
            return;
        }

        // Tenta buscar detalhes do pedido para mostrar os itens
        const dataPedidoFormatada = formatarDataParaBackend(pedidoCarrinho.data_pedido);
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
        const dataPedidoParaBotao = dataPedidoFormatada || pedidoCarrinho.data_pedido;
        
        // Calcula o total dos itens caso o total do pedido não esteja correto
        let totalCalculado = parseFloat(pedidoCarrinho.total_pedido || 0);
        let totalItens = parseInt(pedidoCarrinho.total_produtos || 0);
        
        if (detalhes && detalhes.itens && detalhes.itens.length > 0) {
            // Recalcula o total baseado nos itens
            const totalRecalculado = detalhes.itens.reduce((sum, item) => {
                const subtotal = parseFloat(item.subtotal || 0);
                return sum + subtotal;
            }, 0);
            
            // Usa o total recalculado se for diferente (com margem de erro de 0.01)
            if (Math.abs(totalCalculado - totalRecalculado) > 0.01) {
                totalCalculado = totalRecalculado;
                console.warn('Total do pedido inconsistente, usando total recalculado dos itens');
            }
            
            // Recalcula a quantidade total de itens
            const quantidadeRecalculada = detalhes.itens.reduce((sum, item) => {
                return sum + parseInt(item.quantidade || 0);
            }, 0);
            
            if (totalItens !== quantidadeRecalculada) {
                totalItens = quantidadeRecalculada;
                console.warn('Quantidade de itens inconsistente, usando quantidade recalculada');
            }
        }
        
        container.innerHTML = `
            <div class="carrinho-item" style="background-color: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>Carrinho</h4>
                <p><strong>Total:</strong> R$ ${totalCalculado.toFixed(2)}</p>
                <p><strong>Quantidade de itens:</strong> ${totalItens}</p>
                ${detalhes && detalhes.itens && detalhes.itens.length > 0 ? `
                    <h5 style="margin-top: 1rem;">Itens do carrinho:</h5>
                    <ul style="margin-top: 0.5rem; list-style: none; padding: 0;">
                        ${detalhes.itens.map(item => {
                            const subtotal = parseFloat(item.subtotal || 0);
                            return `
                            <li style="padding: 0.5rem; background-color: #f9f9f9; margin-bottom: 0.5rem; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>${item.nome_produto}</strong> - Qtd: ${item.quantidade} - R$ ${subtotal.toFixed(2)}
                                </div>
                                <button onclick="removerDoCarrinho(${item.id_produto})" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.875rem; margin-left: 1rem;">
                                    Remover
                                </button>
                            </li>
                        `;
                        }).join('')}
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
                ${pedido.status_entrega && pedido.status_entrega.trim() !== '' ? `<p><strong>Entrega:</strong> ${pedido.status_entrega} ${pedido.metodo_entrega ? `(${pedido.metodo_entrega})` : ''}</p>` : ''}
                ${pedido.endereco_entrega ? `<p><strong>Endereço:</strong> ${pedido.endereco_entrega}</p>` : ''}
                ${pedido.status_pedido === 'aguardando pagamento' ? `
                    <button onclick="simularPagamento('${cpf}', '${dataPedidoFormatada}')" class="btn btn-success" style="margin-top: 0.5rem;">
                        Simular Pagamento
                    </button>
                ` : ''}
                ${pedido.status_entrega ? `
                    <button onclick="verDetalhesEntrega('${cpf}', '${dataPedidoFormatada}')" class="btn btn-primary" style="margin-top: 0.5rem;">
                        Ver Detalhes da Entrega
                    </button>
                ` : ''}
                <button onclick="criarSolicitacao('${cpf}', '${dataPedidoFormatada}')" class="btn btn-secondary" style="margin-top: 0.5rem;">
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
    if (!confirm('Deseja simular o pagamento deste pedido? O status será atualizado para "pagamento confirmado".')) {
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

async function carregarRecomendacoes() {
    const cpf = obterCPFComprador();
    const container = document.getElementById('recomendacao-lista');

    if (!cpf) {
        container.innerHTML = '<p class="message error" style="grid-column: 1/-1;">Informe seu CPF para receber recomendações personalizadas</p>';
        return;
    }

    container.innerHTML = '<p>Buscando recomendações...</p>';

    try {
        const response = await fetch(`${API_URL}/comprador/recomendacoes?cpf=${cpf}`);
        const produtos = await response.json();

        if (!produtos || produtos.length === 0) {
            container.innerHTML = '<p class="message" style="background: #e0f7fa; color: #006064; grid-column: 1/-1;">Nenhuma recomendação encontrada. Verifique se você possui uma categoria preferida cadastrada.</p>';
            return;
        }

        container.innerHTML = produtos.map(produto => `
            <div class="produto-card" style="border: 2px solid #764ba2;">
                <div style="background: #764ba2; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; display: inline-block; margin-bottom: 5px;">Recomendado</div>
                <h4>${produto.nome_produto}</h4>
                <div class="preco">R$ ${parseFloat(produto.preco).toFixed(2)}</div>
                <div class="info">Categoria: ${produto.nome_categoria}</div>
                ${produto.media_nota > 0 ? `<div class="info">⭐ ${parseFloat(produto.media_nota).toFixed(1)}</div>` : ''}
                
                <div style="margin-top: 1rem; display: flex; gap: 5px;">
                    <input type="number" id="qtd-rec-${produto.id_produto}" value="1" min="1" style="width: 60px; margin: 0;">
                    <button onclick="adicionarAoCarrinhoRecomendado(${produto.id_produto})" class="btn btn-primary" style="flex: 1; padding: 0.5rem;">
                        Adicionar ao Carrinho
                    </button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Erro:', error);
        container.innerHTML = '<p class="message error">Erro ao carregar recomendações.</p>';
    }
}

// Função wrapper para adicionar ao carrinho a partir da aba de recomendação
async function adicionarAoCarrinhoRecomendado(idProduto) {
    const cpf = obterCPFComprador();
    const qtdInput = document.getElementById(`qtd-rec-${idProduto}`);
    const quantidade = parseInt(qtdInput.value) || 1;

    // Reutiliza a lógica de chamada de API existente, mas tratando o ID do input específico
    try {
        const response = await fetch(`${API_URL}/comprador/carrinho`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf, id_produto: idProduto, quantidade })
        });
        
        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Produto adicionado ao carrinho!', 'success');
        } else {
            mostrarMensagem(result.error || 'Erro ao adicionar', 'error');
        }
    } catch (e) {
        console.error(e);
        mostrarMensagem('Erro de conexão', 'error');
    }
}
// ========== FUNCIONALIDADES DO VENDEDOR ==========

async function carregarDadosVendedor() {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    // Verifica se o vendedor existe
    const vendedorExiste = await verificarVendedorExiste(cpf);
    if (!vendedorExiste) {
        mostrarModalCadastroVendedor(cpf);
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
            // Carrega alertas de estoque automaticamente após carregar dados
            carregarAlertasEstoque();
        } else {
            if (vendedor.error === 'Vendedor não encontrado') {
                mostrarModalCadastroVendedor(cpf);
            } else {
                container.innerHTML = '<p>Vendedor não encontrado.</p>';
            }
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar dados do vendedor', 'error');
    }
}

async function carregarAlertasEstoque() {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        const container = document.getElementById('alertas-estoque-lista');
        container.innerHTML = '<p style="color: #666;">Informe seu CPF para verificar alertas de estoque.</p>';
        return;
    }

    // Verifica se o vendedor existe
    const vendedorExiste = await verificarVendedorExiste(cpf);
    if (!vendedorExiste) {
        const container = document.getElementById('alertas-estoque-lista');
        container.innerHTML = '<p style="color: #666;">Vendedor não encontrado. Cadastre-se primeiro.</p>';
        return;
    }

    const container = document.getElementById('alertas-estoque-lista');
    container.innerHTML = '<p>Carregando alertas...</p>';

    try {
        const response = await fetch(`${API_URL}/vendedor/produtos/estoque-baixo?cpf=${cpf}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status} ao buscar alertas de estoque`);
        }
        
        const produtos = await response.json();
        
        if (!produtos || produtos.length === 0) {
            container.innerHTML = `
                <div style="padding: 1rem; background-color: #d4edda; border-radius: 4px; color: #155724;">
                    <strong>✅ Nenhum produto com estoque baixo!</strong>
                    <p style="margin: 0.5rem 0 0 0;">Todos os seus produtos estão com estoque adequado.</p>
                </div>
            `;
            return;
        }

        // Ordena por estoque (menor primeiro)
        produtos.sort((a, b) => (a.estoque_atual || 0) - (b.estoque_atual || 0));

        container.innerHTML = `
            <div style="padding: 1rem; background-color: #f8d7da; border-radius: 4px; color: #721c24; margin-bottom: 1rem;">
                <strong>⚠️ Atenção: ${produtos.length} produto(s) com estoque baixo!</strong>
            </div>
            <div style="display: grid; gap: 1rem;">
                ${produtos.map(produto => {
                    const estoqueAtual = parseInt(produto.estoque_atual || 0);
                    const alertaEstoque = parseInt(produto.alerta_estoque || 0);
                    const percentual = alertaEstoque > 0 ? Math.round((estoqueAtual / alertaEstoque) * 100) : 0;
                    const corAlerta = estoqueAtual === 0 ? '#dc3545' : (estoqueAtual <= alertaEstoque * 0.5 ? '#fd7e14' : '#ffc107');
                    
                    return `
                        <div style="padding: 1rem; background-color: #fff; border-left: 4px solid ${corAlerta}; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                <div>
                                    <h4 style="margin: 0 0 0.5rem 0; color: #333;">${produto.nome_produto || 'Produto sem nome'}</h4>
                                    <p style="margin: 0; color: #666; font-size: 0.9rem;">ID: ${produto.id_produto}</p>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: ${corAlerta};">
                                        ${estoqueAtual}
                                    </div>
                                    <div style="font-size: 0.8rem; color: #666;">
                                        unidades
                                    </div>
                                </div>
                            </div>
                            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #eee;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <span style="color: #666; font-size: 0.9rem;">Alerta configurado:</span>
                                    <span style="font-weight: bold; color: #333;">${alertaEstoque} unidades</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #666; font-size: 0.9rem;">Preço:</span>
                                    <span style="font-weight: bold; color: #333;">R$ ${parseFloat(produto.preco || 0).toFixed(2)}</span>
                                </div>
                                ${estoqueAtual === 0 ? `
                                    <div style="margin-top: 0.5rem; padding: 0.5rem; background-color: #f8d7da; border-radius: 4px; color: #721c24; font-size: 0.9rem;">
                                        <strong>🔴 ESTOQUE ZERADO!</strong> Reabasteça urgentemente.
                                    </div>
                                ` : estoqueAtual <= alertaEstoque * 0.5 ? `
                                    <div style="margin-top: 0.5rem; padding: 0.5rem; background-color: #fff3cd; border-radius: 4px; color: #856404; font-size: 0.9rem;">
                                        <strong>🟠 Estoque crítico!</strong> Reabasteça em breve.
                                    </div>
                                ` : `
                                    <div style="margin-top: 0.5rem; padding: 0.5rem; background-color: #fff3cd; border-radius: 4px; color: #856404; font-size: 0.9rem;">
                                        <strong>🟡 Estoque abaixo do alerta.</strong> Considere reabastecer.
                                    </div>
                                `}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar alertas de estoque:', error);
        container.innerHTML = `
            <div style="padding: 1rem; background-color: #f8d7da; border-radius: 4px; color: #721c24;">
                <strong>Erro ao carregar alertas de estoque.</strong>
                <p style="margin: 0.5rem 0 0 0;">Por favor, tente novamente.</p>
            </div>
        `;
        mostrarMensagem('Erro ao carregar alertas de estoque', 'error');
    }
}

async function carregarEstatisticas() {
    const cpf = obterCPFVendedor();
    const meses = parseInt(document.getElementById('stats-periodo').value);
    
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
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
                <h4 style="margin-top: 2rem;">Favoritos dos Clientes</h4>
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
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
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
                    <button onclick="atualizarEstoque(${produto.id_produto})" class="btn btn-primary">Atualizar Estoque</button>
                    <button onclick="removerProduto(${produto.id_produto})" class="btn btn-danger">Remover</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar produtos', 'error');
    }
}

async function atualizarEstoque(idProduto) {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

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
            // Recarrega alertas de estoque após atualizar
            carregarAlertasEstoque();
        } else {
            mostrarMensagem(result.error || 'Erro ao atualizar estoque', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao atualizar estoque', 'error');
    }
}

async function removerProduto(idProduto) {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

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

async function carregarSolicitacoes() {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    const container = document.getElementById('solicitacoes-lista');
    container.innerHTML = '<p>Carregando solicitações...</p>';

    try {
        const response = await fetch(`${API_URL}/vendedor/solicitacoes?cpf=${cpf}`);
        const solicitacoes = await response.json();
        
        if (!solicitacoes || solicitacoes.length === 0) {
            container.innerHTML = '<p>Nenhuma solicitação encontrada.</p>';
            return;
        }

        container.innerHTML = solicitacoes.map(solicitacao => {
            const dataPedidoFormatada = formatarDataParaBackend(solicitacao.data_pedido) || solicitacao.data_pedido;
            const dataSolicitacaoFormatada = formatarDataParaBackend(solicitacao.data_solicitacao) || solicitacao.data_solicitacao;
            
            // Mapear tipos para português
            const tipos = {
                'devolucao': 'Devolução',
                'troca': 'Troca',
                'suporte': 'Suporte',
                'cancelamento': 'Cancelamento'
            };
            
            // Mapear status para português
            const status = {
                'aberta': 'Aberta',
                'em_analise': 'Em Análise',
                'concluida': 'Concluída'
            };
            
            const tipoTexto = tipos[solicitacao.tipo] || solicitacao.tipo;
            const statusTexto = status[solicitacao.status_solicitacao] || solicitacao.status_solicitacao;
            
            // Botões apenas para solicitações abertas
            const botoes = solicitacao.status_solicitacao === 'aberta' ? `
                <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                    <button onclick="aceitarSolicitacao('${cpf}', '${solicitacao.cpf_cliente}', '${dataPedidoFormatada}', '${dataSolicitacaoFormatada}')" 
                            class="btn btn-success" style="flex: 1;">
                        Aceitar
                    </button>
                    <button onclick="recusarSolicitacao('${cpf}', '${solicitacao.cpf_cliente}', '${dataPedidoFormatada}', '${dataSolicitacaoFormatada}')" 
                            class="btn btn-danger" style="flex: 1;">
                        Recusar
                    </button>
                </div>
            ` : '';
            
            return `
                <div class="pedido-item" style="margin-bottom: 1rem;">
                    <h4>Solicitação de ${tipoTexto}</h4>
                    <p><strong>Cliente:</strong> ${solicitacao.nome_cliente || solicitacao.cpf_cliente}</p>
                    <p><strong>Status:</strong> <span class="status ${solicitacao.status_solicitacao}">${statusTexto}</span></p>
                    <p><strong>Pedido:</strong> ${new Date(solicitacao.data_pedido).toLocaleString('pt-BR')}</p>
                    <p><strong>Data da Solicitação:</strong> ${new Date(solicitacao.data_solicitacao).toLocaleString('pt-BR')}</p>
                    <p><strong>Valor do Pedido:</strong> R$ ${parseFloat(solicitacao.total_pedido || 0).toFixed(2)}</p>
                    ${botoes}
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro:', error);
        container.innerHTML = '<p style="color: #ef4444;">Erro ao carregar solicitações</p>';
        mostrarMensagem('Erro ao carregar solicitações', 'error');
    }
}

async function aceitarSolicitacao(cpfVendedor, cpfCliente, dataPedido, dataSolicitacao) {
    if (!confirm('Deseja aceitar esta solicitação? O status será alterado para "concluída".')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/solicitacoes`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpf_vendedor: cpfVendedor,
                cpf_cliente: cpfCliente,
                data_pedido: dataPedido,
                data_solicitacao: dataSolicitacao,
                status: 'concluida'
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Solicitação aceita! Status atualizado para "concluída".', 'success');
            setTimeout(() => {
                carregarSolicitacoes();
            }, 500);
        } else {
            mostrarMensagem(result.error || 'Erro ao aceitar solicitação', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao aceitar solicitação', 'error');
    }
}

async function recusarSolicitacao(cpfVendedor, cpfCliente, dataPedido, dataSolicitacao) {
    if (!confirm('Deseja recusar esta solicitação? O status será alterado para "concluída" (recusada).')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/solicitacoes`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpf_vendedor: cpfVendedor,
                cpf_cliente: cpfCliente,
                data_pedido: dataPedido,
                data_solicitacao: dataSolicitacao,
                status: 'concluida'
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Solicitação recusada! Status atualizado para "concluída".', 'success');
            setTimeout(() => {
                carregarSolicitacoes();
            }, 500);
        } else {
            mostrarMensagem(result.error || 'Erro ao recusar solicitação', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao recusar solicitação', 'error');
    }
}

let produtoPendenteVendedor = null;

async function verificarVendedorExiste(cpf) {
    if (!cpf) return false;
    
    try {
        const response = await fetch(`${API_URL}/vendedor/verificar?cpf=${cpf}`);
        const result = await response.json();
        return result.existe === true;
    } catch (error) {
        console.error('Erro ao verificar vendedor:', error);
        return false;
    }
}

async function adicionarProduto() {
    const cpf = obterCPFVendedor();
    const nome = document.getElementById('novo-produto-nome').value;
    const descricao = document.getElementById('novo-produto-desc').value;
    const preco = parseFloat(document.getElementById('novo-produto-preco').value);
    const estoque = parseInt(document.getElementById('novo-produto-estoque').value) || 0;
    const alerta = parseInt(document.getElementById('novo-produto-alerta').value) || 0;
    const origem = document.getElementById('novo-produto-origem').value;

    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    if (!nome || isNaN(preco)) {
        mostrarMensagem('Por favor, preencha nome e preço', 'error');
        return;
    }

    // Verifica se o vendedor existe
    const vendedorExiste = await verificarVendedorExiste(cpf);
    if (!vendedorExiste) {
        // Salva os dados do produto para adicionar após cadastro
        produtoPendenteVendedor = {
            nome,
            descricao,
            preco,
            estoque,
            alerta,
            origem
        };
        mostrarModalCadastroVendedor(cpf);
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
            carregarProdutosVendedor();
            // Recarrega alertas de estoque após adicionar produto
            carregarAlertasEstoque();
        } else {
            if (result.error === 'vendedor_nao_existe') {
                produtoPendenteVendedor = {
                    nome,
                    descricao,
                    preco,
                    estoque,
                    alerta,
                    origem
                };
                mostrarModalCadastroVendedor(cpf);
            } else {
                mostrarMensagem(result.error || 'Erro ao adicionar produto', 'error');
            }
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao adicionar produto', 'error');
    }
}

async function carregarVendasRecentes() {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Informe o CPF do vendedor.', 'error');
        return;
    }

    const limite = document.getElementById('vendas-limite').value || 5;
    const statusFiltro = document.getElementById('vendas-filtro-status').value;
    const container = document.getElementById('vendas-recentes-lista');

    container.innerHTML = '<p>Carregando vendas...</p>';

    try {
        let url = `${API_URL}/vendedor/vendas?cpf=${cpf}&limite=${limite}`;
        if (statusFiltro) url += `&status=${statusFiltro}`;

        const response = await fetch(url);
        const vendas = await response.json();

        if (!vendas || vendas.length === 0) {
            container.innerHTML = '<p>Nenhuma venda encontrada com os filtros atuais.</p>';
            return;
        }

        container.innerHTML = vendas.map(venda => {
            const dataExibicao = new Date(venda.data_pedido).toLocaleString('pt-BR');
            // Formata data para usar como ID único e para enviar ao backend
            const dataBackend = formatarDataParaBackend(venda.data_pedido);
            const idUnico = `${venda.cpf_cliente}-${dataBackend.replace(/[^0-9]/g, '')}`;

            return `
            <div class="pedido-item" style="border-left: 5px solid #667eea; display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; justify-content: space-between;">
                <div style="flex: 2; min-width: 250px;">
                    <h4 style="color: #333;">Data: ${dataExibicao}</h4>
                    <p><strong>Produto:</strong> ${venda.nome_produto}</p>
                    <p><strong>Cliente:</strong> ${venda.cpf_cliente}</p>
                    <p><strong>Valor:</strong> R$ ${parseFloat(venda.total_pedido).toFixed(2)}</p>
                    <p><strong>Status Atual:</strong> <span class="status ${venda.status_pedido}">${venda.status_pedido}</span></p>
                    ${venda.status_entrega ? `<p><strong>Entrega:</strong> ${venda.status_entrega}</p>` : ''}
                </div>
                
                <div style="flex: 1; min-width: 200px; background: #f8f9fa; padding: 10px; border-radius: 8px;">
                    ${venda.status_pedido !== 'entregue' ? `
                        <button onclick="marcarEntregaConcluida('${venda.cpf_cliente}', '${dataBackend}')" 
                                class="btn btn-success" style="width: 100%; font-size: 0.9rem; padding: 8px; margin-bottom: 10px;">
                            ✅ Marcar Entrega como Concluída
                        </button>
                    ` : ''}
                    
                    ${venda.status_entrega ? `
                        <button onclick="verDetalhesEntrega('${venda.cpf_cliente}', '${dataBackend}')" 
                                class="btn btn-primary" style="width: 100%; font-size: 0.9rem; padding: 5px;">
                            Ver Detalhes da Entrega
                        </button>
                    ` : ''}
                </div>
            </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao carregar vendas recentes.', 'error');
    }
}

async function marcarEntregaConcluida(cpfCliente, dataPedido) {
    if (!confirm('Deseja marcar esta entrega como concluída? O status do pedido será alterado para "entregue".')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/vendas/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpf_cliente: cpfCliente,
                data_pedido: dataPedido,
                status: 'entregue'
            })
        });

        const res = await response.json();
        
        if (response.ok) {
            mostrarMensagem('Entrega marcada como concluída com sucesso!', 'success');
            carregarVendasRecentes(); // Recarrega a lista para mostrar o novo status
        } else {
            mostrarMensagem(res.error || 'Erro ao marcar entrega como concluída', 'error');
        }
    } catch (e) {
        console.error(e);
        mostrarMensagem('Erro de conexão ao atualizar status', 'error');
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

async function carregarPedidosAguardandoEnvio() {
    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    const container = document.getElementById('pedidos-envio-lista');
    container.innerHTML = '<p>Carregando pedidos...</p>';

    try {
        const response = await fetch(`${API_URL}/vendedor/pedidos/aguardando-envio?cpf_vendedor=${cpf}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status} ao buscar pedidos`);
        }
        
        const pedidos = await response.json();
        
        if (!pedidos || pedidos.length === 0) {
            container.innerHTML = '<p>Nenhum pedido aguardando envio.</p>';
            return;
        }

        container.innerHTML = pedidos.map(pedido => {
            const dataPedidoFormatada = formatarDataParaBackend(pedido.data_pedido) || pedido.data_pedido;
            
            return `
                <div class="pedido-item" style="background-color: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                    <h4>Pedido de ${new Date(pedido.data_pedido).toLocaleString('pt-BR')}</h4>
                    <p><strong>Cliente:</strong> ${pedido.nome_cliente || pedido.cpf_cliente}</p>
                    <p><strong>Status:</strong> <span class="status ${pedido.status_pedido}">${pedido.status_pedido}</span></p>
                    <p><strong>Total:</strong> R$ ${parseFloat(pedido.total_pedido || 0).toFixed(2)}</p>
                    <p><strong>Itens:</strong> ${pedido.total_produtos || 0}</p>
                    ${pedido.metodo_pagamento ? `<p><strong>Pagamento:</strong> ${pedido.metodo_pagamento}</p>` : ''}
                    ${pedido.metodo_entrega ? `<p><strong>Método de Entrega:</strong> ${pedido.metodo_entrega}</p>` : ''}
                    ${pedido.endereco_entrega ? `<p><strong>Endereço:</strong> ${pedido.endereco_entrega}</p>` : ''}
                    <div style="margin-top: 1rem;">
                        <button onclick="enviarPedido('${cpf}', '${pedido.cpf_cliente}', '${dataPedidoFormatada}')" 
                                class="btn btn-success" style="width: 100%;">
                            📦 Simular Envio
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro:', error);
        container.innerHTML = '<p style="padding: 1rem; background-color: #f8d7da; border-radius: 4px; color: #721c24;">Erro ao carregar pedidos. Por favor, tente novamente.</p>';
        mostrarMensagem('Erro ao carregar pedidos aguardando envio', 'error');
    }
}

async function enviarPedido(cpfVendedor, cpfCliente, dataPedido) {
    if (!confirm('Deseja marcar este pedido como enviado? Isso criará/atualizará a entrega e mudará o status para "enviado".')) {
        return;
    }

    const cpf = obterCPFVendedor();
    if (!cpf) {
        mostrarMensagem('Por favor, informe seu CPF no topo da página', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vendedor/pedido/enviar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpf_vendedor: cpf,
                cpf_cliente: cpfCliente,
                data_pedido: dataPedido
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarMensagem('Pedido marcado como enviado com sucesso! Entrega criada/atualizada.', 'success');
            carregarPedidosAguardandoEnvio();
        } else {
            mostrarMensagem(result.error || 'Erro ao enviar pedido', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao enviar pedido', 'error');
    }
}

// Carregar produtos, categorias e recomendações ao iniciar
window.onload = function() {
    carregarCategorias();
    buscarProdutos();
};

