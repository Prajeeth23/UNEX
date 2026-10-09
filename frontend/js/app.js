/**
 * UNEX OS - Mission Control Main Controller
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Visualizer & Telemetry
    const visualizer = new VoiceVisualizer('waveform-canvas', 'neural-orb');
    const telemetry = new TelemetryManager();

    // 2. Chat Form & Conversation Stream
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatStream = document.getElementById('chat-stream');
    let conversationHistory = [];

    function appendMessage(role, content, toolsExecuted = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg msg-${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.textContent = role === 'user' ? 'YOU' : '⬡';

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';

        const header = document.createElement('div');
        header.className = 'msg-header';
        header.textContent = role === 'user' ? 'Operator' : 'UNEX Core';

        const body = document.createElement('div');
        body.className = 'msg-content';
        body.textContent = content;

        bubble.appendChild(header);
        bubble.appendChild(body);

        // Tool badges if assistant ran tools
        if (toolsExecuted && toolsExecuted.length > 0) {
            toolsExecuted.forEach(tool => {
                const chip = document.createElement('div');
                chip.className = 'tool-chip';
                chip.innerHTML = `<span>⚙️</span> Executed: ${tool}`;
                bubble.appendChild(chip);
            });
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
        chatStream.appendChild(msgDiv);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = chatInput.value.trim();
            if (!text) return;

            appendMessage('user', text);
            conversationHistory.push({ role: 'user', content: text });
            chatInput.value = '';
            visualizer.setState('thinking');

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, history: conversationHistory })
                });

                if (!res.ok) {
                    const err = await res.json();
                    appendMessage('assistant', `Error: ${err.detail || 'Service unavailable'}`);
                    visualizer.setState('idle');
                    return;
                }

                const data = await res.json();
                appendMessage('assistant', data.response);
                conversationHistory.push({ role: 'assistant', content: data.response });
                visualizer.setState('speaking');

                setTimeout(() => visualizer.setState('idle'), 2500);
            } catch (err) {
                appendMessage('assistant', `Failed to connect to UNEX Core: ${err.message}`);
                visualizer.setState('idle');
            }
        });
    }

    // 3. Screen Preview & Capture
    const screenImg = document.getElementById('screen-img');
    const viewportLoader = document.getElementById('viewport-loader');
    const btnRefreshScreen = document.getElementById('btn-refresh-screen');
    const btnToggleOcr = document.getElementById('btn-toggle-ocr');
    const ocrOverlay = document.getElementById('ocr-overlay');
    const btnAnalyzeScene = document.getElementById('btn-analyze-scene');
    const visionText = document.getElementById('vision-text');

    async function loadScreenThumbnail() {
        try {
            viewportLoader.textContent = 'Capturing live screen...';
            viewportLoader.style.display = 'block';
            screenImg.style.display = 'none';

            const res = await fetch('/api/vision/screen-thumbnail');
            if (!res.ok) throw new Error('Capture failed');
            const data = await res.json();

            if (data.success && data.image_base64) {
                screenImg.src = `data:image/png;base64,${data.image_base64}`;
                screenImg.onload = () => {
                    viewportLoader.style.display = 'none';
                    screenImg.style.display = 'block';
                };
            }
        } catch (e) {
            viewportLoader.textContent = 'Preview unavailable';
        }
    }

    if (btnRefreshScreen) {
        btnRefreshScreen.addEventListener('click', () => loadScreenThumbnail());
    }

    // Load initial thumbnail on load
    loadScreenThumbnail();

    // OCR Toggle
    if (btnToggleOcr) {
        btnToggleOcr.addEventListener('click', async () => {
            if (ocrOverlay.style.display === 'block') {
                ocrOverlay.style.display = 'none';
                btnToggleOcr.textContent = 'Toggle OCR Text';
            } else {
                ocrOverlay.textContent = 'Reading screen text via RapidOCR...';
                ocrOverlay.style.display = 'block';
                btnToggleOcr.textContent = 'Hide OCR Text';

                try {
                    const res = await fetch('/api/vision/extract-text', { method: 'POST' });
                    const data = await res.json();
                    ocrOverlay.textContent = data.text || 'No text detected on screen.';
                } catch (e) {
                    ocrOverlay.textContent = `OCR Error: ${e.message}`;
                }
            }
        });
    }

    // Analyze Scene with Moondream
    if (btnAnalyzeScene) {
        btnAnalyzeScene.addEventListener('click', async () => {
            visionText.textContent = 'Processing visual analysis through Moondream...';
            visualizer.setState('thinking');
            try {
                const res = await fetch('/api/vision/analyze-screen?region=fullscreen', { method: 'POST' });
                const data = await res.json();
                if (data.analysis && data.analysis.description) {
                    visionText.textContent = data.analysis.description;
                } else {
                    visionText.textContent = JSON.stringify(data.analysis || data);
                }
                visualizer.setState('idle');
            } catch (e) {
                visionText.textContent = `Vision error: ${e.message}`;
                visualizer.setState('idle');
            }
        });
    }

    // 4. Clipboard Sync
    const clipBox = document.getElementById('clipboard-content');
    const btnRefreshClip = document.getElementById('btn-refresh-clip');

    async function syncClipboard() {
        try {
            // Read from chat tool execution or direct query
            clipBox.textContent = 'Syncing...';
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: "What is currently in my clipboard?", history: [] })
            });
            const data = await res.json();
            clipBox.textContent = data.response;
        } catch (e) {
            clipBox.textContent = 'Sync failed';
        }
    }

    if (btnRefreshClip) {
        btnRefreshClip.addEventListener('click', syncClipboard);
    }

    // 5. Security Approval Handlers
    const btnApprove = document.getElementById('btn-approval-approve');
    const btnDeny = document.getElementById('btn-approval-deny');

    async function handleApproval(approved) {
        try {
            await fetch('/api/security/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved })
            });
            document.getElementById('approval-banner').style.display = 'none';
        } catch (e) {
            console.error('Approval failed:', e);
        }
    }

    if (btnApprove) btnApprove.addEventListener('click', () => handleApproval(true));
    if (btnDeny) btnDeny.addEventListener('click', () => handleApproval(false));

    // 6. Drawer Tab Navigation
    const tabs = document.querySelectorAll('.drawer-tab');
    const panes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const target = document.getElementById(tab.dataset.tab);
            if (target) target.classList.add('active');
        });
    });

    // 7. Quick Window Actions (Minimize, Maximize, Restore)
    async function executeWindowAction(state) {
        const titleEl = document.getElementById('win-title');
        const title = titleEl ? titleEl.textContent : '';
        if (!title || title.includes('Detecting')) return;

        try {
            await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: `${state} the window '${title}'`, history: [] })
            });
        } catch (e) {
            console.error(e);
        }
    }

    document.getElementById('btn-minimize-active')?.addEventListener('click', () => executeWindowAction('minimize'));
    document.getElementById('btn-maximize-active')?.addEventListener('click', () => executeWindowAction('maximize'));
    document.getElementById('btn-restore-active')?.addEventListener('click', () => executeWindowAction('restore'));
});
