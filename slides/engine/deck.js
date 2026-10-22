/* ==========================================================================
   MICAI 2026 · Mech Interp Tutorial — tiny deck engine (no dependencies)

   Slide markup:
     <section class="slide" id="unique-id" data-presenter="miguel|salvador|victor"
              data-block="Block 1 · Observe"> ... <aside class="notes">…</aside></section>

   Builds: any element with data-step="k" (k = 1, 2, …) appears at step k.
     A slide may also declare data-steps="n" to have n steps without visible builds
     (useful when an animation consumes the steps).

   Animation API (call after the engine loads; scripts inside parts run at load):
     Deck.on('slide-id', 'enter', (slideEl, step) => {...})   // slide became active
     Deck.on('slide-id', 'step',  (slideEl, step) => {...})   // step changed (also fired on enter)
     Deck.on('slide-id', 'leave', (slideEl) => {...})         // slide deactivated: stop timers here
     Deck.reducedMotion   // true if the OS asks for reduced motion: jump to end states
     Deck.raf(slideEl, fn) // requestAnimationFrame loop that auto-stops when the slide leaves;
                           // fn(tSeconds) returns false to stop early.
   Keys: → Space PgDn next · ← PgUp prev · Home/End · N notes · T clock · F fullscreen · ? help
   ========================================================================== */
(function () {
  const W = 1600, H = 900;
  const handlers = {};      // id -> {enter:[], step:[], leave:[]}
  const loops = new Map();  // slideEl -> Set of active loop tokens
  let slides = [], idx = 0, step = 0, stage, notesPanel, clockEl, helpEl, footer, progress, clockStart = null;

  const Deck = {
    reducedMotion: window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    on(id, ev, fn) {
      (handlers[id] = handlers[id] || { enter: [], step: [], leave: [] })[ev].push(fn);
      // if the slide is already active (late registration), fire immediately
      const s = slides[idx];
      if (s && s.id === id && (ev === 'enter' || ev === 'step')) safe(() => fn(s, step));
    },
    raf(slideEl, fn) {
      const token = {};
      if (!loops.has(slideEl)) loops.set(slideEl, new Set());
      loops.get(slideEl).add(token);
      const t0 = performance.now();
      const tick = (now) => {
        if (!loops.get(slideEl) || !loops.get(slideEl).has(token)) return;
        let keep;
        try { keep = fn((now - t0) / 1000); } catch (e) { console.error(e); keep = false; }
        if (keep === false) { loops.get(slideEl).delete(token); return; }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      return () => loops.get(slideEl) && loops.get(slideEl).delete(token);
    },
    get index() { return idx; }, get step() { return step; }, get slides() { return slides; },
    go(i, s = 0) { show(i, s); }, next, prev,
  };
  window.Deck = Deck;

  function safe(f) { try { f(); } catch (e) { console.error('[deck]', e); } }
  function fire(slide, ev, arg) {
    const h = handlers[slide.id];
    if (h) h[ev].forEach(fn => safe(() => fn(slide, arg)));
    slide.dispatchEvent(new CustomEvent('slide:' + ev, { detail: { step: arg } }));
  }
  function maxStep(slide) {
    const declared = parseInt(slide.dataset.steps || '0', 10);
    let m = 0;
    slide.querySelectorAll('[data-step]').forEach(el => { m = Math.max(m, parseInt(el.dataset.step, 10) || 0); });
    return Math.max(declared, m);
  }
  function applyBuilds(slide, s) {
    slide.querySelectorAll('[data-step]').forEach(el => {
      const k = parseInt(el.dataset.step, 10) || 0;
      el.classList.toggle('shown', k <= s);
      el.classList.toggle('dimmed', el.classList.contains('dim-after') && k < s);
    });
  }
  function stopLoops(slide) { loops.delete(slide); }

  function show(i, s = 0) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    const prevSlide = slides[idx];
    const changing = i !== idx || !prevSlide.classList.contains('active');
    if (changing && prevSlide && prevSlide.classList.contains('active')) {
      prevSlide.classList.remove('active'); stopLoops(prevSlide); fire(prevSlide, 'leave');
    }
    idx = i; const slide = slides[idx];
    step = Math.max(0, Math.min(maxStep(slide), s));
    slide.classList.add('active');
    applyBuilds(slide, step);
    if (changing) fire(slide, 'enter', step);
    fire(slide, 'step', step);
    updateChrome();
    history.replaceState(null, '', '#/' + (idx + 1) + (step ? '.' + step : ''));
  }
  function next() {
    const slide = slides[idx];
    if (step < maxStep(slide)) show(idx, step + 1); else if (idx < slides.length - 1) show(idx + 1, 0);
  }
  function prev() {
    if (step > 0) show(idx, step - 1);
    else if (idx > 0) { const p = slides[idx - 1]; show(idx - 1, maxStep(p)); }
  }

  const NAMES = { miguel: 'Miguel González', salvador: 'Salvador Hinojosa', victor: 'Víctor Macías-Terrón' };
  function updateChrome() {
    const slide = slides[idx];
    const who = slide.dataset.presenter || '';
    footer.querySelector('.who').textContent = NAMES[who] || '';
    footer.style.setProperty('--dot', who ? `var(--${who})` : 'var(--muted)');
    footer.querySelector('.block').textContent = slide.dataset.block || '';
    footer.querySelector('.num').textContent = `${idx + 1} / ${slides.length}`;
    stage.classList.toggle('on-section', slide.classList.contains('section-slide'));
    stage.classList.toggle('on-title', slide.classList.contains('title-slide'));
    progress.style.width = ((idx + 1) / slides.length * 100) + '%';
    const n = slide.querySelector('aside.notes');
    notesPanel.innerHTML = `<h4>Notes · slide ${idx + 1}${slide.dataset.block ? ' · ' + slide.dataset.block : ''} · step ${step}/${maxStep(slide)}</h4>` + (n ? n.innerHTML : '<em>No notes.</em>');
  }

  function fit() {
    const s = Math.min(window.innerWidth / W, window.innerHeight / H);
    stage.style.transform = `scale(${s})`;
  }

  function init() {
    stage = document.querySelector('.stage');
    slides = Array.from(stage.querySelectorAll(':scope > .slide'));
    slides.forEach((s, i) => { if (!s.id) s.id = 'slide-' + (i + 1); });

    footer = document.createElement('div'); footer.className = 'chrome-footer';
    footer.innerHTML = '<span class="who"></span><span class="block"></span><span class="num"></span>';
    progress = document.createElement('div'); progress.className = 'progress';
    stage.append(footer, progress);

    notesPanel = document.createElement('div'); notesPanel.className = 'notes-panel';
    clockEl = document.createElement('div'); clockEl.className = 'clock';
    helpEl = document.createElement('div'); helpEl.className = 'help';
    helpEl.innerHTML = '<div class="box"><b>Keys</b><br><kbd>→</kbd> <kbd>Space</kbd> next &nbsp; <kbd>←</kbd> previous<br><kbd>Home</kbd>/<kbd>End</kbd> first/last &nbsp; <kbd>N</kbd> notes &nbsp; <kbd>T</kbd> clock &nbsp; <kbd>F</kbd> fullscreen<br>Type a number + <kbd>Enter</kbd> to jump &nbsp; <kbd>?</kbd> this help</div>';
    document.body.append(notesPanel, clockEl, helpEl);

    window.addEventListener('resize', fit); fit();

    let typed = '';
    document.addEventListener('keydown', (e) => {
      if (e.target.closest('input, textarea, select, [contenteditable]')) return;
      const k = e.key;
      if (/^[0-9]$/.test(k)) { typed += k; return; }
      if (k === 'Enter' && typed) { show(parseInt(typed, 10) - 1, 0); typed = ''; return; }
      typed = '';
      if (['ArrowRight', ' ', 'PageDown', 'Enter'].includes(k)) { e.preventDefault(); next(); }
      else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(k)) { e.preventDefault(); prev(); }
      else if (k === 'Home') show(0, 0);
      else if (k === 'End') show(slides.length - 1, 0);
      else if (k === 'n' || k === 'N') notesPanel.classList.toggle('open');
      else if (k === 't' || k === 'T') { clockEl.classList.toggle('open'); if (!clockStart) clockStart = Date.now(); }
      else if (k === 'f' || k === 'F') { if (!document.fullscreenElement) document.documentElement.requestFullscreen?.(); else document.exitFullscreen?.(); }
      else if (k === '?') helpEl.classList.toggle('open');
      else if (k === 'Escape') { helpEl.classList.remove('open'); notesPanel.classList.remove('open'); }
    });
    stage.addEventListener('click', (e) => {
      if (e.target.closest('a, button, input, select, label, [data-interactive]')) return;
      const r = stage.getBoundingClientRect();
      if (e.clientX - r.left < r.width * 0.25) prev(); else next();
    });
    let tx = null;
    stage.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener('touchend', e => {
      if (tx === null) return; const dx = e.changedTouches[0].clientX - tx; tx = null;
      if (Math.abs(dx) > 40) (dx < 0 ? next : prev)();
    });
    setInterval(() => {
      if (!clockStart) return;
      const s = Math.floor((Date.now() - clockStart) / 1000);
      clockEl.textContent = `${Math.floor(s / 3600)}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
    }, 500);

    const m = location.hash.match(/^#\/(\d+)(?:\.(\d+))?/);
    show(m ? parseInt(m[1], 10) - 1 : 0, m && m[2] ? parseInt(m[2], 10) : 0);
  }

  // ---- print mode: render every slide at its last step (final animation frames) ----
  // Handlers must draw their final frame synchronously when Deck.reducedMotion is true.
  let printing = false;
  function preparePrint() {
    if (printing) return;
    printing = true;
    const rm = Deck.reducedMotion;
    Deck.reducedMotion = true;
    document.body.classList.add('printing');
    slides.forEach(s => {
      const m = maxStep(s);
      s.classList.add('active');
      applyBuilds(s, m);
      fire(s, 'enter', m);
      fire(s, 'step', m);
    });
    Deck.reducedMotion = rm;
  }
  function endPrint() {
    if (!printing) return;
    printing = false;
    document.body.classList.remove('printing');
    slides.forEach((s, i) => { if (i !== idx) { s.classList.remove('active'); stopLoops(s); } });
    const cur = slides[idx], s = step;
    cur.classList.remove('active');
    show(idx, s);
  }
  Deck.preparePrint = preparePrint;
  Deck.endPrint = endPrint;
  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', endPrint);

  // For headless preview/screenshot tooling: Deck.go(i, s) and window.__deckReady
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => { init(); window.__deckReady = true; });
  else { init(); window.__deckReady = true; }
})();
