const PERFIL_KEY = 'simAppGatoPerfil';
const REGISTROS_COMIDA_KEY = 'simAppRegistrosComida';
const API_BASE = "http://127.0.0.1:3000/api";

const formPerfil = document.getElementById('form-perfil');
const perfilDisplay = document.getElementById('perfil-display');
const btnEditar = document.getElementById('btn-editar-perfil');

const formRegistroComida = document.getElementById('form-registro-comida');
const statusMessage = document.getElementById('status-message');
const chartCanvas = document.getElementById('monitoramentoChart');
const historicoLista = document.getElementById('historico-lista');

let monitoramentoChart;

function showStatus(message, type = 'success') {
    statusMessage.textContent = message;
    statusMessage.style.backgroundColor = type === 'success' ? '#d4edda' : '#f8d7da';
    statusMessage.style.color = type === 'success' ? '#155724' : '#721c24';
    statusMessage.style.border = type === 'success' ? '1px solid #c3e6cb' : '1px solid #f5c6cb';
    statusMessage.style.display = 'block';
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 3000);
}

function getLocalData(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
}

function saveLocalData(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function carregarPerfilLocal() {
    const perfil = getLocalData(PERFIL_KEY)[0] || null;
    if (perfil) {
        toggleProfileView(false, perfil);
    } else {
        toggleProfileView(true, null);
    }
}

function toggleProfileView(isEditing, perfil) {
    if (perfil && !isEditing) {
        perfilDisplay.style.display = 'block';
        formPerfil.style.display = 'none';
        btnEditar.style.display = 'block';
        perfilDisplay.innerHTML = `
            <p><strong>Nome:</strong> ${perfil.nome}</p>
            <p><strong>Raça:</strong> ${perfil.raca || 'Não informada'}</p>
            <p><strong>Peso:</strong> ${perfil.peso} kg</p>
            <p><strong>Nascimento:</strong> ${perfil.nascimento || 'Não informada'}</p>
        `;
    } else {
        perfilDisplay.style.display = 'none';
        formPerfil.style.display = 'block';
        btnEditar.style.display = 'none';
        if (perfil) {
            document.getElementById('nome').value = perfil.nome;
            document.getElementById('raca').value = perfil.raca;
            document.getElementById('peso').value = perfil.peso;
            document.getElementById('nascimento').value = perfil.nascimento;
            formPerfil.querySelector('h3').textContent = 'Edite as informações do seu Gato';
        } else {
            formPerfil.reset();
            formPerfil.querySelector('h3').textContent = 'Preencha as informações do seu Gato';
        }
    }
}

formPerfil.addEventListener('submit', (e) => {
    e.preventDefault();
    const dadosForm = {
        nome: document.getElementById('nome').value,
        raca: document.getElementById('raca').value,
        peso: parseFloat(document.getElementById('peso').value),
        nascimento: document.getElementById('nascimento').value
    };
    saveLocalData(PERFIL_KEY, [dadosForm]);
    showStatus('Perfil salvo/atualizado com sucesso!');
    toggleProfileView(false, dadosForm);
});

btnEditar.addEventListener('click', () => {
    const perfil = getLocalData(PERFIL_KEY)[0] || null;
    toggleProfileView(true, perfil);
});

formRegistroComida.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const dataInput = document.getElementById('reg-data').value;
    const horaInput = document.getElementById('reg-hora').value;
    const descricaoInput = document.getElementById('descricao-comida');
    const quantidadeInput = document.getElementById('quantidade');
    
    const quantidade = parseInt(quantidadeInput.value, 10);
    const descricao = descricaoInput.value || 'Não informado';

    if (quantidade <= 0 || isNaN(quantidade)) {
        showStatus('🚨 Por favor, insira uma quantidade válida.', 'error');
        return;
    }

    const timestamp = new Date(`${dataInput}T${horaInput}`).toISOString();
    const novoRegistro = {
        id: Date.now(),
        data: dataInput,
        hora: horaInput,
        gramas: quantidade,
        descricao: descricao,
        timestamp: timestamp
    };

    // --- SALVA LOCALMENTE (como antes) ---
    let registros = getLocalData(REGISTROS_COMIDA_KEY);
    registros.push(novoRegistro);
    saveLocalData(REGISTROS_COMIDA_KEY, registros);

    // --- ENVIA AO BACKEND (POST /api/weight) ---
    // Nota: certifique-se de ter definido API_BASE no topo do arquivo.
    fetch(`${API_BASE}/weight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            grams: quantidade,
            timestamp: timestamp
        })
    })
    .then(async (res) => {
        if (!res.ok) {
            // tenta ler corpo do erro para diagnóstico
            const text = await res.text().catch(() => '');
            throw new Error(`HTTP ${res.status} ${text}`);
        }
        return res.json();
    })
    .then((resp) => {
        console.log('Enviado ao backend:', resp);
        showStatus(`Registrado localmente e enviado ao backend: +${quantidade}g`);
    })
    .catch((err) => {
        console.error('Erro ao enviar ao backend:', err);
        showStatus('Registrado localmente — falha ao enviar ao backend', 'error');
    });

    // limpa campos e atualiza UI
    quantidadeInput.value = '';
    descricaoInput.value = '';
    renderizarHistorico();
});


function renderizarGraficoFicticio() {
    
    const labels = ['20/10', '21/10', '22/10', '23/10', '24/10'];
    const dadosComeu = [4, 5, 4, 6, 4];
    
    if (monitoramentoChart) {
        monitoramentoChart.destroy();
    }

    const ctx = chartCanvas.getContext('2d');
    if (!ctx) { return; }

    monitoramentoChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Nº de Refeições (vezes)',
                    data: dadosComeu,
                    backgroundColor: '#5d4037', 
                    yAxisID: 'y' 
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { 
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Contagem (Vezes)' },
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Monitoramento Fictício (20/10 a 24/10)' }
            }
        }
    });
}

function renderizarHistorico() {
    const registros = getLocalData(REGISTROS_COMIDA_KEY);
    historicoLista.innerHTML = '';

    if (registros.length === 0) {
        historicoLista.innerHTML = '<li>Nenhuma refeição registrada ainda.</li>';
        return;
    }

    const registrosOrdenados = registros.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    const formatadorData = new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });

    registrosOrdenados.forEach(reg => {
        const dataFormatada = formatadorData.format(new Date(reg.timestamp));
        const itemLista = document.createElement('li');
        
        itemLista.innerHTML = `
            <div class="linha-principal">
                <span><strong>${dataFormatada}</strong> às ${reg.hora}</span>
                <span>${reg.gramas}g</span>
            </div>
            <div class="linha-descricao">
                ${reg.descricao}
            </div>
        `;
        historicoLista.appendChild(itemLista);
    });
}

function preencherDataHoraAtual() {
    const agora = new Date();
    
    const dataInput = document.getElementById('reg-data');
    dataInput.value = agora.toISOString().split('T')[0];

    const horaInput = document.getElementById('reg-hora');
    horaInput.value = agora.toTimeString().split(' ')[0].substring(0, 5);
}

document.addEventListener('DOMContentLoaded', () => {
    carregarPerfilLocal();
    renderizarGraficoFicticio();
    renderizarHistorico();
    preencherDataHoraAtual();

    const API_BASE = "http://127.0.0.1:3000/api";

    async function carregarDoBackend() {
        try {
            const res = await fetch(`${API_BASE}/readings`);
            if (!res.ok) throw new Error("Erro ao buscar leituras");
            const dados = await res.json();

            // Atualiza histórico no DOM
            historicoLista.innerHTML = "";
            if (!Array.isArray(dados) || dados.length === 0) {
                historicoLista.innerHTML = '<li>Nenhuma refeição registrada ainda.</li>';
            } else {
                // ordenar decrescente
                const ordenado = dados.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
                ordenado.forEach(reg => {
                    const dataFormatada = new Intl.DateTimeFormat('pt-BR', { 
                        day: '2-digit', month: '2-digit', year: 'numeric' 
                    }).format(new Date(reg.timestamp));
                    const itemLista = document.createElement('li');
                    itemLista.innerHTML = `
                        <div class="linha-principal">
                            <span><strong>${dataFormatada}</strong> às ${new Date(reg.timestamp).toTimeString().substring(0,5)}</span>
                            <span>${reg.grams}g</span>
                        </div>
                    `;
                    historicoLista.appendChild(itemLista);
                });
            }

            // Atualiza gráfico com os últimos N pontos
            const pontos = dados.slice(-20); // últimos 20
            const labels = pontos.map(p => new Date(p.timestamp).toLocaleString('pt-BR'));
            const valores = pontos.map(p => p.grams);

            if (monitoramentoChart) monitoramentoChart.destroy();
            const ctx = chartCanvas.getContext('2d');
            monitoramentoChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{ label: 'Peso (g)', data: valores, borderColor: '#5d4037', tension: 0.2 }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });

        } catch (err) {
            console.error("Erro ao carregar do backend:", err);
            // fallback: seu gráfico fictício
            renderizarGraficoFicticio();
            renderizarHistorico();
        }
    }

    // Dentro do DOMContentLoaded, chame:
    carregarDoBackend();
    setInterval(carregarDoBackend, 10000); // atualiza a cada 10s

});