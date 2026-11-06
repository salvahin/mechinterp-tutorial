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
         P presenter window · O notes window · L switch note language (EN / ES)
         S switch between the director's notes and the word-for-word script

   A slide may carry a second aside with the script to read out loud:
     <aside class="speech"><div data-lang="en">…</div><div data-lang="es">…</div></aside>
   S (or the NOTES / SPEECH button in either window) switches modes; slides with
   no script keep showing their notes, so the mode is safe to leave on.

   Second-screen windows: the buttons at the bottom right (or P / O) open two
   separate browser windows that follow the deck — a presenter view (clock, now /
   next, notes, nav buttons) and a plain notes view for reading aloud. Put the deck
   on the projector and either window on your laptop. Arrow keys work in all three.
   ========================================================================== */
(function () {
  const W = 1600, H = 900;
  const handlers = {};      // id -> {enter:[], step:[], leave:[]}
  const loops = new Map();  // slideEl -> Set of active loop tokens
  let slides = [], idx = 0, step = 0, stage, notesPanel, clockEl, helpEl, footer, progress, tools;
  let clockStart = null, clockAccum = 0;   // running since / milliseconds banked across pauses

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

  const NAMES = { miguel: 'Miguel González', salvador: 'Salvador Hinojosa', victor: 'Víctor Terrón-Macías' };
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
    const n = notesOf(slide);
    notesPanel.innerHTML = `<h4>${modeTag(slide)} · ${langTag(slide)} · slide ${idx + 1}${slide.dataset.block ? ' · ' + slide.dataset.block : ''} · step ${step}/${maxStep(slide)} · <b>${cueText(slide, step)}</b></h4>` + (n || '<em>No notes.</em>');
    markCues(notesPanel, step, maxStep(slide));
    syncAux();
  }

  /* ---- clock: counts up, pausable, shared by the overlay and the windows ---- */
  function clockMs() { return clockAccum + (clockStart ? Date.now() - clockStart : 0); }
  function clockToggle() {
    if (clockStart) { clockAccum += Date.now() - clockStart; clockStart = null; }
    else clockStart = Date.now();
  }
  function clockReset() { clockStart = null; clockAccum = 0; }
  function hms(ms) {
    const s = Math.floor(ms / 1000);
    return `${Math.floor(s / 3600)}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }

  /* ---- presenter and notes windows ---------------------------------------
     Opened from a click so popup blockers allow them. Each is an about:blank
     window we write once and then update in place; same-origin, so no
     postMessage or BroadcastChannel is needed and it all works from file://. */
  const AUX = {
    presenter: { win: null, features: 'width=1180,height=820' },
    notes: { win: null, features: 'width=820,height=940' },
  };
  const AUX_CSS = `
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body { margin: 0; height: 100vh; display: flex; flex-direction: column;
           background: #101114; color: #E9EAEC; font: 16px/1.5 Inter, system-ui, sans-serif; }
    .bar { display: flex; align-items: center; gap: 16px; padding: 12px 20px;
           border-bottom: 1px solid #272A31; flex: none; }
    .clock { font: 700 34px/1 ui-monospace, "IBM Plex Mono", monospace; letter-spacing: .02em; }
    .meta { font-size: 13px; letter-spacing: .1em; text-transform: uppercase; color: #9AA0AA; }
    .spacer { margin-left: auto; }
    button { font: 600 13px/1 Inter, system-ui, sans-serif; color: #E9EAEC; cursor: pointer;
             background: #1C1E23; border: 1px solid #343842; border-radius: 8px; padding: 9px 13px; }
    button:hover { background: #262A31; }
    .now { padding: 16px 20px 0; flex: none; }
    .label { font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: #6F7681; }
    h1 { margin: 4px 0 0; font: 700 27px/1.25 Sora, Inter, system-ui, sans-serif; color: #fff; }
    #notes { flex: 1; overflow: auto; padding: 16px 20px 24px; font-size: var(--fs, 19px); }
    #notes p { margin: 0 0 .75em; }
    #notes b { color: #fff; }
    #notes i { color: #B9BFC9; }
    .next { flex: none; padding: 12px 20px; border-top: 1px solid #272A31; background: #15171B; }
    .next h1 { font-size: 19px; color: #C7CCD4; }
    /* what the right arrow will do from here */
    .cue-bar { font: 700 12px/1 Inter, system-ui, sans-serif; letter-spacing: .08em;
               text-transform: uppercase; color: #0F1115; background: #F2B33D;
               padding: 7px 11px; border-radius: 7px; white-space: nowrap; }
    /* one block per build step, so you can see where you are in the animation */
    #notes [data-cue] { border-left: 3px solid #343842; padding: 2px 0 2px 15px; margin: 0 0 .8em; }
    #notes [data-cue]::before { content: attr(data-label); display: block;
      font: 700 11px/1 Inter, system-ui, sans-serif; letter-spacing: .14em;
      color: #6F7681; margin-bottom: 5px; }
    #notes .done { opacity: .4; }
    #notes .now { border-left-color: #5B8CFF; }
    #notes .now::before { color: #8FB0FF; }
    /* a step of a notebook, not a build of this slide: no bar, no press cue */
    #notes .ref { border-left-color: #272A31; }
    #notes .ref::before { color: #5A606B; }
    #notes .next { border-left-color: #F2B33D; }
    #notes .next::before { color: #F2B33D; }
  `;
  function auxDoc(kind) {
    const langBtn = '<button data-act="lang" id="langbtn" title="English / Español (L)"></button>'
      + '<button data-act="mode" id="modebtn" title="Director&apos;s notes / word-for-word script (S)"></button>';
    const nav = kind === 'presenter'
      ? `<span class="spacer"></span>${langBtn}
         <button data-act="prev">&larr; Prev</button>
         <button data-act="next">Next &rarr;</button>
         <button data-act="clock">Start / pause</button>
         <button data-act="reset">Reset</button>`
      : `<span class="spacer"></span>${langBtn}
         <button data-act="smaller">A&minus;</button>
         <button data-act="bigger">A+</button>`;
    const nextBlock = kind === 'presenter'
      ? `<div class="next"><p class="label">Next</p><h1 id="next"></h1></div>` : '';
    return `<!doctype html><html lang="en"><head><meta charset="utf-8">
      <title>${kind === 'presenter' ? 'Presenter' : 'Notes'} · deck</title>
      <style>${AUX_CSS}</style></head><body>
      <div class="bar"><span class="clock" id="clock">0:00:00</span>
        <span class="meta" id="meta"></span><span class="cue-bar" id="cue"></span>${nav}</div>
      <div class="now"><p class="label" id="block"></p><h1 id="title"></h1></div>
      <div id="notes"></div>${nextBlock}</body></html>`;
  }
  function openAux(kind) {
    const a = AUX[kind];
    if (a.win && !a.win.closed) { a.win.focus(); return; }
    const w = window.open('', 'deck-' + kind, a.features);
    if (!w) { alert('The browser blocked the window. Allow pop-ups for this page and click again.'); return; }
    w.document.open(); w.document.write(auxDoc(kind)); w.document.close();
    a.win = w;
    a.fs = 19;
    w.document.addEventListener('keydown', relayKey);
    w.document.addEventListener('click', (e) => {
      const b = e.target.closest('[data-act]'); if (!b) return;
      const act = b.dataset.act;
      if (act === 'next') next();
      else if (act === 'prev') prev();
      else if (act === 'clock') clockToggle();
      else if (act === 'reset') clockReset();
      else if (act === 'lang') toggleLang();
      else if (act === 'mode') toggleMode();
      else if (act === 'bigger' || act === 'smaller') {
        a.fs = Math.max(14, Math.min(34, a.fs + (act === 'bigger' ? 2 : -2)));
        w.document.getElementById('notes').style.setProperty('--fs', a.fs + 'px');
      }
      tickClocks();
    });
    lastAuxIdx = -1;       // force a scroll-to-top on the first sync
    syncAux();
  }
  function relayKey(e) {
    const k = e.key;
    if (['ArrowRight', ' ', 'PageDown'].includes(k)) { e.preventDefault(); next(); }
    else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(k)) { e.preventDefault(); prev(); }
    else if (k === 'Home') show(0, 0);
    else if (k === 'End') show(slides.length - 1, 0);
    else if (k === 'l' || k === 'L') toggleLang();
    else if (k === 's' || k === 'S') toggleMode();
  }
  /* ---- speaker-note language ---------------------------------------------
     A note may carry one block per language:
       <aside class="notes"><div data-lang="en">…</div><div data-lang="es">…</div></aside>
     Notes without data-lang blocks are used as-is, so single-language decks and
     any slide whose translation is not written yet keep working. */
  let lang = (() => { try { return localStorage.getItem('deck-lang') || 'en'; } catch (e) { return 'en'; } })();

  /* ---- notes or speech ----------------------------------------------------
     Two kinds of text can sit on a slide: aside.notes (what to do and say, in
     shorthand) and aside.speech (the sentences themselves). The mode is global
     and sticky, and a slide with no script simply keeps showing its notes. */
  let mode = (() => { try { return localStorage.getItem('deck-mode') === 'speech' ? 'speech' : 'notes'; } catch (e) { return 'notes'; } })();
  function hasSpeech(slide) { return !!slide.querySelector('aside.speech'); }
  /* which of the two is actually on screen — may differ from the chosen mode */
  function shownMode(slide) { return mode === 'speech' && hasSpeech(slide) ? 'speech' : 'notes'; }
  function modeTag(slide) {
    if (shownMode(slide) === 'speech') return 'SPEECH';
    return mode === 'speech' ? 'NOTES (no script)' : 'NOTES';
  }
  function setMode(m) {
    mode = m;
    try { localStorage.setItem('deck-mode', m); } catch (e) { /* file:// with storage off */ }
    lastAuxIdx = -1;          // different text: scroll back to the top
    updateChrome();
  }
  function toggleMode() { setMode(mode === 'speech' ? 'notes' : 'speech'); }
  Deck.setMode = setMode;

  function asideOf(slide) {
    return slide.querySelector('aside.' + shownMode(slide));
  }
  function notesOf(slide) {
    const a = asideOf(slide);
    if (!a) return null;
    const blocks = a.querySelectorAll(':scope > [data-lang]');
    if (!blocks.length) return a.innerHTML;
    const pick = a.querySelector(`:scope > [data-lang="${lang}"]`)
              || a.querySelector(':scope > [data-lang="en"]') || blocks[0];
    return pick.innerHTML;
  }
  function langsOf(slide) {
    const a = asideOf(slide);
    return a ? Array.from(a.querySelectorAll(':scope > [data-lang]'), el => el.dataset.lang) : [];
  }
  /* which language is actually on screen — may differ from the chosen one */
  function shownLang(slide) {
    const have = langsOf(slide);
    if (!have.length || have.includes(lang)) return lang;
    return have.includes('en') ? 'en' : have[0];
  }
  function langTag(slide) {
    const s = shownLang(slide);
    return s === lang ? s.toUpperCase() : s.toUpperCase() + ' (fallback)';
  }
  function setLang(l) {
    lang = l;
    try { localStorage.setItem('deck-lang', l); } catch (e) { /* file:// with storage off */ }
    lastAuxIdx = -1;          // the text changed under us: scroll back to the top
    updateChrome();
  }
  function toggleLang() {
    const have = langsOf(slides[idx]);
    setLang(lang === 'en' ? (have.includes('es') ? 'es' : 'en') : 'en');
  }
  Deck.setLang = setLang;
  Deck.get = { get lang() { return lang; } };

  /* Label every build-step block in the notes and show which one is on screen,
     which one the next → will reveal, and which are already spent. */
  const CUE_WORDS = {
    en: { arrival: 'on arrival', one: 'step ', many: 'steps ', now: ' · on screen now', press: 'press → · ' },
    es: { arrival: 'al entrar', one: 'paso ', many: 'pasos ', now: ' · en pantalla', press: 'pulsa → · ' },
  };
  function markCues(root, cur, max) {
    const w = CUE_WORDS[lang] || CUE_WORDS.en;
    root.querySelectorAll('[data-cue]').forEach(el => {
      const k = parseInt(el.dataset.cue, 10);
      const r = el.dataset.range, s = el.dataset.suffix;
      let base = r ? w.many + r : k === 0 ? w.arrival : w.one + k;
      if (s) base += ' · ' + s;
      // Some notes number the steps of a notebook, not builds of this slide.
      // Those must never say "press ->": flatten them instead.
      const build = k <= max;
      el.classList.toggle('ref', !build);
      el.classList.toggle('done', build && k < cur);
      el.classList.toggle('now', build && k === cur);
      el.classList.toggle('next', build && k === cur + 1);
      el.dataset.label = !build ? base
        : k === cur ? base + w.now
        : k === cur + 1 ? w.press + base
        : base;
    });
  }
  function cueText(slide, cur) {
    const max = maxStep(slide);
    if (cur < max) return `→ reveals step ${cur + 1} of ${max}`;
    return idx < slides.length - 1 ? '→ next slide' : '→ end of deck';
  }
  let lastAuxIdx = -1;
  function eachAux(fn) {
    for (const kind of ['presenter', 'notes']) {
      const w = AUX[kind].win;
      if (w && !w.closed && w.document.getElementById('clock')) fn(w, kind);
    }
  }
  function syncAux() {
    const slide = slides[idx];
    const titleOf = (s) => s ? (s.querySelector('h1, h2')?.textContent || s.id).trim() : '— end of deck —';
    const html = notesOf(slide) || '<em>No notes for this slide.</em>';
    const have = langsOf(slide);
    const meta = `${modeTag(slide)} · ${langTag(slide)} · slide ${idx + 1} / ${slides.length} · step ${step} / ${maxStep(slide)}`;
    const fresh = idx !== lastAuxIdx;
    eachAux((w, kind) => {
      const d = w.document, set = (id, v) => { const el = d.getElementById(id); if (el) el.innerHTML = v; };
      set('meta', meta);
      set('block', slide.dataset.block || '');
      set('title', titleOf(slide));
      set('notes', html);
      set('cue', cueText(slide, step));
      if (kind === 'presenter') set('next', titleOf(slides[idx + 1]));
      const lb = d.getElementById('langbtn');
      if (lb) {
        // show the language you would switch TO, and say when there is nothing to switch to
        const other = lang === 'en' ? 'es' : 'en';
        const can = have.includes(other);
        lb.textContent = can ? other.toUpperCase() : 'no ' + other.toUpperCase();
        lb.disabled = !can;
        lb.style.opacity = can ? '' : '.45';
        lb.title = can ? 'English / Español (L)' : 'No translation for this slide yet';
      }
      const mb = d.getElementById('modebtn');
      if (mb) {
        // show the mode you would switch TO, and say when this slide has no script
        const other = mode === 'speech' ? 'notes' : 'speech';
        const can = mode === 'speech' || hasSpeech(slide);
        mb.textContent = other === 'speech' ? (hasSpeech(slide) ? 'SPEECH' : 'no script') : 'NOTES';
        mb.disabled = !can;
        mb.style.opacity = can ? '' : '.45';
        mb.title = can ? "Director's notes / word-for-word script (S)"
                       : 'No word-for-word script for this slide';
      }
      const box = d.getElementById('notes');
      markCues(box, step, maxStep(slide));
      if (fresh) box.scrollTop = 0;                          // keep the scroll while stepping
      box.style.setProperty('--fs', (AUX[kind].fs || 19) + 'px');
    });
    lastAuxIdx = idx;
  }
  function tickClocks() {
    const t = hms(clockMs());
    clockEl.textContent = t;
    eachAux((w) => { w.document.getElementById('clock').textContent = t; });
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
    helpEl.innerHTML = '<div class="box"><b>Keys</b><br><kbd>→</kbd> <kbd>Space</kbd> next &nbsp; <kbd>←</kbd> previous<br><kbd>Home</kbd>/<kbd>End</kbd> first/last &nbsp; <kbd>N</kbd> notes &nbsp; <kbd>T</kbd> clock &nbsp; <kbd>F</kbd> fullscreen<br><kbd>P</kbd> presenter window &nbsp; <kbd>O</kbd> notes window &nbsp; <kbd>L</kbd> EN / ES notes<br><kbd>S</kbd> notes / word-for-word script<br>Type a number + <kbd>Enter</kbd> to jump &nbsp; <kbd>?</kbd> this help</div>';

    tools = document.createElement('div'); tools.className = 'deck-tools';
    tools.innerHTML = '<button type="button" data-open="presenter">Presenter</button>'
                    + '<button type="button" data-open="notes">Notes</button>';
    tools.addEventListener('click', (e) => {
      const b = e.target.closest('[data-open]');
      if (b) { e.stopPropagation(); openAux(b.dataset.open); }
    });
    document.body.append(notesPanel, clockEl, helpEl);
    // The published copy (GitHub Pages) is for participants: no Presenter / Notes buttons there.
    // P and O still open the windows, so a presenter can run the deck from the site.
    if (!/\.github\.io$/.test(location.hostname)) document.body.append(tools);

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
      else if (k === 'p' || k === 'P') openAux('presenter');
      else if (k === 'o' || k === 'O') openAux('notes');
      else if (k === 'l' || k === 'L') toggleLang();
      else if (k === 's' || k === 'S') toggleMode();
      else if (k === 't' || k === 'T') { clockEl.classList.toggle('open'); if (!clockStart && !clockAccum) clockToggle(); }
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
    setInterval(tickClocks, 500);

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
