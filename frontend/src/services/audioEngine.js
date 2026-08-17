class AudioEngine {
  constructor() {
    this.ctx = null;
    this.droneGain = null;
    this.droneOsc1 = null;
    this.droneOsc2 = null;
    this.isMuted = localStorage.getItem('kshan_audio_muted') === 'true';
  }

  init() {
    if (this.ctx) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.ctx = new AudioContext();
    } catch (e) {
      console.warn('Web Audio API not supported on this browser', e);
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    localStorage.setItem('kshan_audio_muted', this.isMuted.toString());
    if (this.droneGain && this.ctx) {
      this.droneGain.gain.setValueAtTime(this.isMuted ? 0 : 0.05, this.ctx.currentTime);
    }
    return this.isMuted;
  }

  startAmbientDrone() {
    this.init();
    if (!this.ctx || this.droneOsc1) return;
    if (this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }

    try {
      // 1. Dual oscillator drone (55Hz and 110Hz subharmonics)
      this.droneOsc1 = this.ctx.createOscillator();
      this.droneOsc2 = this.ctx.createOscillator();
      this.droneOsc1.type = 'sine';
      this.droneOsc2.type = 'triangle';
      this.droneOsc1.frequency.setValueAtTime(55.0, this.ctx.currentTime); // A1 note
      this.droneOsc2.frequency.setValueAtTime(110.0, this.ctx.currentTime); // A2 note

      // 2. Lowpass filter for smooth deep rumble
      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(180, this.ctx.currentTime);

      this.droneGain = this.ctx.createGain();
      this.droneGain.gain.setValueAtTime(this.isMuted ? 0 : 0.04, this.ctx.currentTime);

      this.droneOsc1.connect(filter);
      this.droneOsc2.connect(filter);
      filter.connect(this.droneGain);
      this.droneGain.connect(this.ctx.destination);

      this.droneOsc1.start();
      this.droneOsc2.start();
    } catch (e) {
      console.warn('Could not start ambient drone', e);
    }
  }

  playChoicePulse() {
    if (this.isMuted || !this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(432, now); // Harmonic 432 Hz
      osc.frequency.exponentialRampToValueAtTime(864, now + 0.35);

      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.4);
    } catch (e) {
      // ignore
    }
  }

  playRewindWarp() {
    if (this.isMuted || !this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(800, now);
      osc.frequency.exponentialRampToValueAtTime(100, now + 0.6);

      gain.gain.setValueAtTime(0.06, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.65);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.65);
    } catch (e) {
      // ignore
    }
  }

  playChime() {
    if (this.isMuted || !this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(528, now); // Love frequency
      gain.gain.setValueAtTime(0.07, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.5);
    } catch (e) {
      // ignore
    }
  }
}

export const audioEngine = new AudioEngine();
