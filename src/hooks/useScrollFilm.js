import { useLayoutEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { FRAMES, WINDOWS, frameUrl } from '../content.js';

gsap.registerPlugin(ScrollTrigger);

// Scroll drives a canvas frame sequence, the chapter copy, the rail and the loader.
// Only runs when index.html put .scrub on <html> (no reduced-motion preference).
export default function useScrollFilm(rootRef) {
  useLayoutEffect(() => {
    const root = rootRef.current;
    if (!document.documentElement.classList.contains('scrub')) return;

    const $ = s => root.querySelector(s);
    const $$ = s => [...root.querySelectorAll(s)];
    const cleanups = [];
    const on = (target, type, fn) => { target.addEventListener(type, fn); cleanups.push(() => target.removeEventListener(type, fn)); };

    // ---- frame sequence on canvas ----
    const canvas = $('.stage canvas');
    const ctx2d = canvas.getContext('2d');
    const portrait = () => innerWidth / innerHeight < 0.9;
    let set = portrait() ? 'mobile' : 'desktop';
    let frames = [], current = 0, alive = true;

    function load(which) {
      const list = new Array(FRAMES);
      let done = 0;
      const order = [];
      // first frame, then every 8th, then fill in: the scrub works early and sharpens as frames arrive
      for (const step of [8, 4, 2, 1]) for (let i = 0; i < FRAMES; i += step) if (!order.includes(i)) order.push(i);
      order.forEach(i => {
        const img = new Image();
        img.decoding = 'async';
        img.onload = img.onerror = () => {
          if (!alive) return;
          done++;
          if (which === set) progress(done / FRAMES);
          if (Math.abs(i - current) < 4) draw(current);
        };
        img.src = frameUrl(which, i + 1);
        list[i] = img;
      });
      return list;
    }

    function nearest(i) {
      for (let d = 0; d < FRAMES; d++) {
        const a = frames[i - d], b = frames[i + d];
        if (a && a.complete && a.naturalWidth) return a;
        if (b && b.complete && b.naturalWidth) return b;
      }
    }

    function size() {
      const dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = innerWidth * dpr;
      canvas.height = innerHeight * dpr;
      draw(current);
    }

    function draw(i) {
      const img = nearest(i);
      if (!img) return;
      const cw = canvas.width, ch = canvas.height;
      const s = Math.max(cw / img.naturalWidth, ch / img.naturalHeight);
      const w = img.naturalWidth * s, h = img.naturalHeight * s;
      ctx2d.fillStyle = '#0b0d0c';
      ctx2d.fillRect(0, 0, cw, ch);
      ctx2d.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
    }

    // ---- loader ----
    const loader = $('.loader');
    const bar = loader.querySelector('i'), pct = loader.querySelector('.loader-pct');
    let opened = false;
    function progress(p) {
      bar.style.transform = `scaleX(${p})`;
      pct.textContent = Math.round(p * 100) + '%';
      if (p >= .25) open(); // a quarter of frames (every 4th) is enough to start
    }
    function open() {
      if (opened) return;
      opened = true;
      loader.classList.add('done');
      intro();
    }
    const fallback = setTimeout(open, 8000);

    // ---- smooth scroll ----
    const lenis = new Lenis({ lerp: 0.085 });
    lenis.on('scroll', ScrollTrigger.update);
    const raf = t => lenis.raf(t * 1000);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    const film = $('.film');
    const chapters = $$('.ch');
    const filmY = p => film.offsetTop + p * (film.offsetHeight - innerHeight);
    let heroLines, heroRest;
    // tweens made through ctx.add are reverted with the rest on unmount
    const intro = () => ctx.add(() => {
      gsap.to(heroLines, { yPercent: 0, duration: 1.4, ease: 'expo.out', stagger: .09 });
      gsap.to(heroRest, { autoAlpha: 1, duration: 1.2, delay: .5 });
    });

    const ctx = gsap.context(() => {
      // ---- scroll drives the frame and the chapter copy ----
      const rail = $$('.rail span');
      const playhead = { f: 0 };

      const tl = gsap.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: { trigger: film, start: 'top top', end: 'bottom bottom', scrub: 0.6 },
      });
      tl.to(playhead, {
        f: FRAMES - 1, duration: 1,
        onUpdate: () => {
          const f = Math.round(playhead.f);
          if (f !== current) { current = f; draw(f); }
        },
      }, 0);

      chapters.forEach((el, i) => {
        const [a, b] = WINDOWS[i];
        const lines = el.querySelectorAll('.lm > *');
        const rest = el.querySelectorAll('.num, .copy .label, .copy p, .copy .meta, .swatches div');
        const span = b - a;
        if (i === 0) {
          // hero is already on screen; it only leaves
          gsap.set(el, { autoAlpha: 1 });
          tl.to(el.querySelector('.hero-t'), { yPercent: -14, autoAlpha: 0, duration: span * .6 }, b - span * .6)
            .to(el.querySelector('.scroll-cue'), { autoAlpha: 0, duration: .02 }, .01);
        } else {
          tl.set(el, { autoAlpha: 1 }, a)
            .from(lines, { yPercent: 110, stagger: span * .06, duration: span * .3, ease: 'power3.out' }, a)
            .from(rest, { autoAlpha: 0, y: 14, stagger: span * .03, duration: span * .25 }, a + span * .12)
            .to(el.querySelector('.copy'), { autoAlpha: 0, y: -30, duration: span * .22, ease: 'power1.in' }, b - span * .22)
            .set(el, { autoAlpha: 0 }, b);
          const sw = el.querySelector('.swatches');
          if (sw) tl.to(sw, { autoAlpha: 0, duration: span * .22 }, b - span * .22);
        }
      });

      ScrollTrigger.create({
        trigger: film, start: 'top top', end: 'bottom bottom',
        onUpdate: self => {
          let active = 0;
          WINDOWS.forEach(([a], i) => { if (self.progress >= a - .02) active = i; });
          rail.forEach(r => r.classList.toggle('on', +r.dataset.r === active));
        },
      });

      // hero title rises in once the loader lifts
      heroLines = chapters[0].querySelectorAll('.lm > *');
      heroRest = $$('.hero-t .label, .scroll-cue');
      gsap.set(heroLines, { yPercent: 110 });
      gsap.set(heroRest, { autoAlpha: 0 });

      // closing words
      gsap.from($$('.end-c > *'), { scrollTrigger: { trigger: $('.end'), start: 'top 70%', once: true }, autoAlpha: 0, y: 30, stagger: .1, duration: 1.1, ease: 'power3.out' });
    }, root);

    frames = load(set);
    size();
    on(window, 'resize', () => {
      const next = portrait() ? 'mobile' : 'desktop';
      if (next !== set) { set = next; frames = load(set); }
      size();
    });

    // in-page links land on the chapter's moment in the film
    on(root, 'click', e => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const id = a.getAttribute('href').slice(1);
      const el = id && document.getElementById(id);
      e.preventDefault();
      if (!id || id === 'top') return lenis.scrollTo(0, { duration: 1.8 });
      const i = chapters.indexOf(el);
      lenis.scrollTo(i > -1 ? filmY((WINDOWS[i][0] + WINDOWS[i][1]) / 2) : el, { duration: 2 });
    });

    return () => {
      alive = false;
      clearTimeout(fallback);
      cleanups.forEach(fn => fn());
      gsap.ticker.remove(raf);
      lenis.destroy();
      ctx.revert();
      loader.classList.remove('done');
    };
  }, [rootRef]);
}
