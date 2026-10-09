/**
 * UNEX Neural Voice Orb & Audio Waveform Visualizer
 */
class VoiceVisualizer {
    constructor(canvasId, orbId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.orb = document.getElementById(orbId);
        this.state = 'idle'; // 'idle', 'listening', 'thinking', 'speaking'
        this.phase = 0;
        this.barsCount = 48;
        this.init();
    }

    init() {
        if (!this.canvas) return;
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.animate();
    }

    resize() {
        if (!this.canvas) return;
        this.canvas.width = this.canvas.parentElement.clientWidth || 500;
        this.canvas.height = 36;
    }

    setState(state) {
        this.state = state;
        const orbCore = this.orb ? this.orb.querySelector('.orb-core') : null;
        const label = document.getElementById('voice-state-label');

        if (!orbCore) return;

        if (state === 'listening') {
            orbCore.style.boxShadow = '0 0 30px #06b6d4, 0 0 50px #38bdf8';
            if (label) label.textContent = 'UNEX LISTENING (Wake Word: "Hey Jarvis")';
        } else if (state === 'thinking') {
            orbCore.style.boxShadow = '0 0 35px #8b5cf6, 0 0 60px #c084fc';
            if (label) label.textContent = 'UNEX PROCESSING (Qwen 2.5 Active)';
        } else if (state === 'speaking') {
            orbCore.style.boxShadow = '0 0 40px #14b8a6, 0 0 70px #2dd4bf';
            if (label) label.textContent = 'UNEX SYNTHESIZING (Kokoro Neural TTS)';
        } else {
            orbCore.style.boxShadow = '0 0 24px #06b6d4, 0 0 40px #8b5cf6';
            if (label) label.textContent = 'UNEX STANDBY • SYSTEM READY';
        }
    }

    animate() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.phase += 0.05;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const centerY = height / 2;
        const barWidth = width / this.barsCount;

        for (let i = 0; i < this.barsCount; i++) {
            const x = i * barWidth;
            const progress = i / this.barsCount;

            // Generate organic sinusoids based on current state
            let amplitude = 2;
            if (this.state === 'listening') {
                amplitude = Math.sin(this.phase + i * 0.3) * 10 + 6;
            } else if (this.state === 'thinking') {
                amplitude = Math.cos(this.phase * 1.5 + i * 0.4) * 8 + 4;
            } else if (this.state === 'speaking') {
                amplitude = Math.sin(this.phase * 2 + i * 0.5) * 14 + 8;
            } else {
                // Gentle idle wave
                amplitude = Math.sin(this.phase * 0.6 + i * 0.2) * 4 + 2;
            }

            // Window function to taper edges
            const envelope = Math.sin(progress * Math.PI);
            const barHeight = Math.max(2, amplitude * envelope);

            // Gradient fill
            const grad = this.ctx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight);
            if (this.state === 'speaking') {
                grad.addColorStop(0, '#14b8a6');
                grad.addColorStop(1, '#06b6d4');
            } else if (this.state === 'thinking') {
                grad.addColorStop(0, '#8b5cf6');
                grad.addColorStop(1, '#c084fc');
            } else {
                grad.addColorStop(0, '#06b6d4');
                grad.addColorStop(1, '#8b5cf6');
            }

            this.ctx.fillStyle = grad;
            this.ctx.fillRect(x + 1, centerY - barHeight / 2, barWidth - 2, barHeight);
        }

        requestAnimationFrame(() => this.animate());
    }
}

window.VoiceVisualizer = VoiceVisualizer;
