// TradingAgents Web UI - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Form Elements
    const form = document.getElementById('analysisForm');
    const providerSelect = document.getElementById('provider');
    const quickModelSelect = document.getElementById('quickModel');
    const deepModelSelect = document.getElementById('deepModel');
    const depthSlider = document.getElementById('depth');
    const depthValue = document.getElementById('depthValue');
    const dateInput = document.getElementById('date');
    const openaiKeyInput = document.getElementById('openaiKey');
    const alphaVantageKeyInput = document.getElementById('alphaVantageKey');
    const discordWebhookInput = document.getElementById('discordWebhook');
    
    // State Elements
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    const errorState = document.getElementById('errorState');
    const progressFill = document.getElementById('progressFill');
    const statusText = document.getElementById('statusText');

    // Set default date to today
    dateInput.valueAsDate = new Date();

    // Load saved configuration
    loadSavedConfig();

    // Load providers on page load
    loadProviders();

    // Depth slider update
    depthSlider.addEventListener('input', function() {
        depthValue.textContent = this.value;
    });

    // Provider change event
    providerSelect.addEventListener('change', async function() {
        const provider = this.value;
        if (provider) {
            await loadModels(provider);
        }
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await startAnalysis();
    });

    // Auto-save API keys when they change (with debounce)
    let saveTimeout;
    [openaiKeyInput, alphaVantageKeyInput, discordWebhookInput].forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveConfig();
            }, 1000); // Save 1 second after user stops typing
        });
    });

    // Load saved configuration from .env
    async function loadSavedConfig() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            if (config.openai_api_key) {
                openaiKeyInput.value = config.openai_api_key;
            }
            if (config.alpha_vantage_api_key) {
                alphaVantageKeyInput.value = config.alpha_vantage_api_key;
            }
            if (config.discord_webhook) {
                discordWebhookInput.value = config.discord_webhook;
            }
        } catch (error) {
            console.error('Fehler beim Laden der Konfiguration:', error);
        }
    }

    // Save configuration to .env
    async function saveConfig() {
        try {
            const config = {
                openai_api_key: openaiKeyInput.value.trim(),
                alpha_vantage_api_key: alphaVantageKeyInput.value.trim(),
                discord_webhook: discordWebhookInput.value.trim()
            };

            const response = await fetch('/api/save-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            if (result.success) {
                console.log('Konfiguration gespeichert');
            }
        } catch (error) {
            console.error('Fehler beim Speichern der Konfiguration:', error);
        }
    }

    // Load available providers
    async function loadProviders() {
        try {
            const response = await fetch('/api/providers');
            const data = await response.json();
            
            providerSelect.innerHTML = '<option value="">Bitte wählen...</option>';
            data.providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider.name;
                option.textContent = provider.name;
                option.dataset.url = provider.url;
                providerSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Fehler beim Laden der Provider:', error);
            showError('Fehler beim Laden der Provider');
        }
    }

    // Load models for selected provider
    async function loadModels(provider) {
        try {
            const response = await fetch(`/api/models/${provider}`);
            const data = await response.json();
            
            // Update quick model select
            quickModelSelect.innerHTML = '<option value="">Bitte wählen...</option>';
            data.quick.forEach(model => {
                const option = document.createElement('option');
                option.value = model.value;
                option.textContent = model.name;
                quickModelSelect.appendChild(option);
            });

            // Update deep model select
            deepModelSelect.innerHTML = '<option value="">Bitte wählen...</option>';
            data.deep.forEach(model => {
                const option = document.createElement('option');
                option.value = model.value;
                option.textContent = model.name;
                deepModelSelect.appendChild(option);
            });

            // Auto-select first options
            if (data.quick.length > 0) quickModelSelect.value = data.quick[0].value;
            if (data.deep.length > 0) deepModelSelect.value = data.deep[0].value;

        } catch (error) {
            console.error('Fehler beim Laden der Modelle:', error);
            showError('Fehler beim Laden der Modelle');
        }
    }

    // Start analysis
    async function startAnalysis() {
        // Get form data
        const ticker = document.getElementById('ticker').value.trim().toUpperCase();
        const date = document.getElementById('date').value;
        const openaiKey = document.getElementById('openaiKey').value.trim();
        const alphaVantageKey = document.getElementById('alphaVantageKey').value.trim();
        const provider = providerSelect.value;
        const providerUrl = providerSelect.options[providerSelect.selectedIndex].dataset.url;
        const quickModel = quickModelSelect.value;
        const deepModel = deepModelSelect.value;
        const depth = parseInt(depthSlider.value);
        const discordWebhook = document.getElementById('discordWebhook').value.trim();
        const discordNotify = document.getElementById('discordNotify').checked;
            if (data.success) {
                // Save config after successful analysis
                await saveConfig();
                showResults(data.result);
            } else {
                showError(data.message);
            }

        } catch (error) {
            console.error('Fehler bei der Analyse:', error);
            showError('Fehler bei der Kommunikation mit dem Server: ' + error.message);
        }
    }       return;
        }

        // Prepare request
        const requestData = {
            ticker: ticker,
            date: date,
            analysts: analysts,
            llm_provider: provider,
            provider_url: providerUrl,
            deep_think_model: deepModel,
            quick_think_model: quickModel,
            research_depth: depth,
            openai_api_key: openaiKey,
            alpha_vantage_api_key: alphaVantageKey,
            discord_webhook: discordWebhook || null,
            discord_notify: discordNotify
        };

        // Show loading state
        showLoading();

        try {
            // Simulate progress
            simulateProgress();

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                showResults(data.result);
            } else {
                showError(data.message);
            }

        } catch (error) {
            console.error('Fehler bei der Analyse:', error);
            showError('Fehler bei der Kommunikation mit dem Server: ' + error.message);
        }
    }

    // Show loading state
    function showLoading() {
        resultsContent.style.display = 'none';
        errorState.style.display = 'none';
        loadingState.style.display = 'block';
        progressFill.style.width = '0%';
        statusText.textContent = 'Initialisierung...';
        document.getElementById('analyzeBtn').disabled = true;
    }

    // Simulate progress
    function simulateProgress() {
        const stages = [
            { percent: 10, text: 'Verbindung zum LLM-Provider...' },
            { percent: 25, text: 'Analysten werden initialisiert...' },
            { percent: 40, text: 'Marktdaten werden abgerufen...' },
            { percent: 60, text: 'Analysten arbeiten...' },
            { percent: 80, text: 'Debatte läuft...' },
            { percent: 95, text: 'Finale Empfehlung wird erstellt...' }
        ];

        let currentStage = 0;
        const interval = setInterval(() => {
            if (currentStage < stages.length) {
                const stage = stages[currentStage];
                progressFill.style.width = stage.percent + '%';
                statusText.textContent = stage.text;
                currentStage++;
            } else {
                clearInterval(interval);
            }
        }, 2000);
    }

    // Show results
    function showResults(result) {
        loadingState.style.display = 'none';
        errorState.style.display = 'none';
        resultsContent.style.display = 'block';
        document.getElementById('analyzeBtn').disabled = false;

        // Parse decision
        let decision = 'HALTEN';
        let decisionClass = 'hold';
        
        if (result.decision) {
            const decisionText = result.decision.toLowerCase();
            if (decisionText.includes('kaufen') || decisionText.includes('buy')) {
                decision = 'KAUFEN';
                decisionClass = 'buy';
            } else if (decisionText.includes('verkaufen') || decisionText.includes('sell')) {
                decision = 'VERKAUFEN';
                decisionClass = 'sell';
            }
        }

        resultsContent.innerHTML = `
            <div class="result-card">
                <h3><i class="fas fa-chart-line"></i> Handelsentscheidung</h3>
                <div class="decision ${decisionClass}">
                    ${decision}
                </div>
                <div class="result-details">
                    <pre>${JSON.stringify(result, null, 2)}</pre>
                </div>
            </div>
        `;
    }

    // Show error
    function showError(message) {
        loadingState.style.display = 'none';
        resultsContent.style.display = 'none';
        errorState.style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('analyzeBtn').disabled = false;
    }

    // WebSocket connection for live updates (optional)
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'status') {
                statusText.textContent = data.message;
            }
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    }

    // Uncomment to enable WebSocket
    // connectWebSocket();
});
