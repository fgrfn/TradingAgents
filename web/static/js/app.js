// TradingAgents Web UI - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 TradingAgents UI wird geladen...');
    
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
    
    // Debug: Überprüfe ob alle Elemente gefunden wurden
    console.log('Elements gefunden:', {
        form: !!form,
        providerSelect: !!providerSelect,
        openaiKeyInput: !!openaiKeyInput,
        alphaVantageKeyInput: !!alphaVantageKeyInput,
        discordWebhookInput: !!discordWebhookInput
    });
    
    // State Elements
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    const errorState = document.getElementById('errorState');
    const progressFill = document.getElementById('progressFill');
    const statusText = document.getElementById('statusText');

    // Set default date to today
    if (dateInput) {
        dateInput.valueAsDate = new Date();
        console.log('✓ Datum gesetzt');
    }

    // Load saved configuration and form data
    console.log('📥 Lade gespeicherte Konfiguration...');
    loadSavedConfig();
    loadFormData();

    // Load providers on page load
    console.log('🔌 Lade LLM Provider...');
    loadProviders();
    
    // Attach auto-save listeners
    console.log('🔗 Richte Auto-Save ein...');
    attachAutoSaveListeners();

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
        if (input) {
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    saveConfig();
                }, 1000); // Save 1 second after user stops typing
            });
        }
    });

    // Load saved configuration from .env
    async function loadSavedConfig() {
        try {
            console.log('Rufe /api/config auf...');
            const response = await fetch('/api/config');
            const config = await response.json();
            console.log('Konfiguration geladen:', config);
            
            if (config.openai_api_key && openaiKeyInput) {
                openaiKeyInput.value = config.openai_api_key;
                console.log('✓ OpenAI Key wiederhergestellt');
            }
            if (config.alpha_vantage_api_key && alphaVantageKeyInput) {
                alphaVantageKeyInput.value = config.alpha_vantage_api_key;
                console.log('✓ Alpha Vantage Key wiederhergestellt');
            }
            if (config.discord_webhook && discordWebhookInput) {
                discordWebhookInput.value = config.discord_webhook;
                console.log('✓ Discord Webhook wiederhergestellt');
            }
        } catch (error) {
            console.error('❌ Fehler beim Laden der Konfiguration:', error);
        }
    }

    // Save configuration to .env
    async function saveConfig() {
        try {
            if (!openaiKeyInput || !alphaVantageKeyInput || !discordWebhookInput) {
                console.error('Nicht alle Input-Elemente gefunden');
                return;
            }

            const config = {
                openai_api_key: openaiKeyInput.value.trim(),
                alpha_vantage_api_key: alphaVantageKeyInput.value.trim(),
                discord_webhook: discordWebhookInput.value.trim()
            };

            console.log('Speichere Konfiguration:', config);

            const response = await fetch('/api/save-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            if (result.success) {
                console.log('✓ Konfiguration gespeichert');
            } else {
                console.error('Fehler:', result.message);
            }
        } catch (error) {
            console.error('Fehler beim Speichern der Konfiguration:', error);
        }
    }

    // Load available providers
    async function loadProviders() {
        try {
            console.log('Rufe /api/providers auf...');
            const response = await fetch('/api/providers');
            const data = await response.json();
            console.log('Provider geladen:', data);
            
            if (!providerSelect) {
                console.error('❌ providerSelect Element nicht gefunden!');
                return;
            }
            
            providerSelect.innerHTML = '<option value="">Bitte wählen...</option>';
            data.providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider.name;
                option.textContent = provider.name;
                option.dataset.url = provider.url;
                providerSelect.appendChild(option);
            });
            console.log(`✓ ${data.providers.length} Provider hinzugefügt`);
        } catch (error) {
            console.error('❌ Fehler beim Laden der Provider:', error);
            if (typeof showError === 'function') {
                showError('Fehler beim Laden der Provider');
            }
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

        // Get selected analysts
        const analysts = [];
        document.querySelectorAll('input[name="analysts"]:checked').forEach(checkbox => {
            analysts.push(checkbox.value);
        });

        // Validation
        if (!ticker || !date || !openaiKey || !alphaVantageKey || !provider || !quickModel || !deepModel) {
            showError('Bitte füllen Sie alle Pflichtfelder aus');
            return;
        }

        if (analysts.length === 0) {
            showError('Bitte wählen Sie mindestens einen Analysten aus');
            return;
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
            // Start analysis
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                showError(`Server-Fehler (${response.status}): ${errorText.substring(0, 200)}`);
                return;
            }

            const startData = await response.json();
            
            if (!startData.success) {
                showError(startData.message || 'Fehler beim Starten der Analyse');
                return;
            }

            const analysisId = startData.analysis_id;
            console.log('Analyse gestartet mit ID:', analysisId);

            // Show loading state and simulate progress
            simulateProgress();

            // Poll for results
            await pollAnalysisResult(analysisId);

        } catch (error) {
            console.error('Fehler bei der Analyse:', error);
            showError('Fehler bei der Kommunikation mit dem Server: ' + error.message);
        }
    }

    // Poll for analysis results
    async function pollAnalysisResult(analysisId) {
        const maxAttempts = 180; // 3 minutes max (180 * 1 second)
        let attempts = 0;

        const poll = async () => {
            try {
                const response = await fetch(`/api/analysis/${analysisId}`);
                const data = await response.json();

                if (data.status === 'completed' && data.success) {
                    showResults(data.result);
                    return;
                } else if (data.status === 'error' || !data.success) {
                    showError(data.message || 'Fehler bei der Analyse');
                    return;
                } else if (data.status === 'running') {
                    attempts++;
                    if (attempts >= maxAttempts) {
                        showError('Timeout: Analyse dauert zu lange');
                        return;
                    }
                    // Poll again after 1 second
                    setTimeout(poll, 1000);
                } else {
                    showError('Unbekannter Status: ' + data.status);
                }
            } catch (error) {
                console.error('Polling error:', error);
                showError('Fehler beim Abrufen der Ergebnisse: ' + error.message);
            }
        };

        poll();
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
    
    // Auto-save form data to localStorage
    let formSaveTimeout;
    function saveFormData() {
        const formData = {
            ticker: document.getElementById('ticker').value,
            date: document.getElementById('date').value,
            provider: providerSelect.value,
            quickModel: quickModelSelect.value,
            deepModel: deepModelSelect.value,
            depth: depthSlider.value,
            discordWebhook: discordWebhookInput.value,
            discordNotify: document.getElementById('discordNotify').checked,
            analystMarket: document.getElementById('analystMarket').checked,
            analystSocial: document.getElementById('analystSocial').checked,
            analystNews: document.getElementById('analystNews').checked,
            analystFundamentals: document.getElementById('analystFundamentals').checked
        };
        localStorage.setItem('tradingagents_formdata', JSON.stringify(formData));
    }

    function loadFormData() {
        const savedData = localStorage.getItem('tradingagents_formdata');
        if (savedData) {
            try {
                const formData = JSON.parse(savedData);
                
                if (formData.ticker) document.getElementById('ticker').value = formData.ticker;
                if (formData.date) document.getElementById('date').value = formData.date;
                if (formData.discordWebhook) discordWebhookInput.value = formData.discordWebhook;
                if (formData.discordNotify !== undefined) document.getElementById('discordNotify').checked = formData.discordNotify;
                if (formData.depth) {
                    depthSlider.value = formData.depth;
                    depthValue.textContent = formData.depth;
                }
                
                // Analysten wiederherstellen
                if (formData.analystMarket !== undefined) document.getElementById('analystMarket').checked = formData.analystMarket;
                if (formData.analystSocial !== undefined) document.getElementById('analystSocial').checked = formData.analystSocial;
                if (formData.analystNews !== undefined) document.getElementById('analystNews').checked = formData.analystNews;
                if (formData.analystFundamentals !== undefined) document.getElementById('analystFundamentals').checked = formData.analystFundamentals;
                
                // Provider und Modelle werden nach dem Laden der Provider gesetzt
                if (formData.provider) {
                    setTimeout(() => {
                        providerSelect.value = formData.provider;
                        loadModels(formData.provider);
                        
                        setTimeout(() => {
                            if (formData.quickModel) quickModelSelect.value = formData.quickModel;
                            if (formData.deepModel) deepModelSelect.value = formData.deepModel;
                        }, 200);
                    }, 200);
                }
            } catch (e) {
                console.error('Fehler beim Laden der Formulardaten:', e);
            }
        }
    }

    function attachAutoSaveListeners() {
        const formElements = [
            'ticker', 'date', 'discordWebhook', 'discordNotify',
            'analystMarket', 'analystSocial', 'analystNews', 'analystFundamentals'
        ];
        
        formElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', () => {
                    clearTimeout(formSaveTimeout);
                    formSaveTimeout = setTimeout(saveFormData, 500);
                });
                element.addEventListener('change', saveFormData);
            }
        });
        
        // Zusätzliche Listener für selects und slider
        providerSelect.addEventListener('change', saveFormData);
        quickModelSelect.addEventListener('change', saveFormData);
        deepModelSelect.addEventListener('change', saveFormData);
        depthSlider.addEventListener('input', () => {
            clearTimeout(formSaveTimeout);
            formSaveTimeout = setTimeout(saveFormData, 500);
        });
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
