/* Dotted US map: each state is a field of lights. Hover makes them flicker. */
(() => {
  const NAMES = {
    AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California",
    CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "D.C.", FL: "Florida",
    GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois", IN: "Indiana",
    IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana", ME: "Maine",
    MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota",
    MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada",
    NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York",
    NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma",
    OR: "Oregon", PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina",
    SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont",
    VA: "Virginia", WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming",
  };

  let canvas, ctx, tip;
  let counts = {};
  let selected = "";
  let hover = "";
  let mouse = { x: -999, y: -999 };
  let raf = 0;
  let scale = 1;
  let onHover = () => {};
  let onPick = () => {};

  function heat(n) {
    const max = Math.max(1, ...Object.values(counts), 1);
    return Math.sqrt(n / max);
  }

  function color(t, bright) {
    // dingy rust → live red. t = data heat, bright = flicker 0..1
    const r = Math.round(70 + t * 140 + bright * 70);
    const g = Math.round(18 + t * 28 + bright * 22);
    const b = Math.round(16 + t * 12 + bright * 10);
    return `rgb(${Math.min(255, r)},${Math.min(80, g)},${Math.min(50, b)})`;
  }

  function hit(mx, my) {
    const pack = window.STATE_DOTS;
    if (!pack) return "";
    const lim = 11 * 11;
    let best = "";
    let bestD = lim;
    for (const [st, pts] of Object.entries(pack.dots)) {
      for (const p of pts) {
        const dx = p[0] * scale - mx;
        const dy = p[1] * scale - my;
        const d = dx * dx + dy * dy;
        if (d < bestD) {
          bestD = d;
          best = st;
        }
      }
    }
    return best;
  }

  function resize() {
    const pack = window.STATE_DOTS;
    if (!canvas || !pack) return;
    const w = canvas.parentElement.clientWidth;
    scale = w / pack.w;
    const h = pack.h * scale;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(now) {
    const pack = window.STATE_DOTS;
    if (!pack || !ctx) return;
    const w = pack.w * scale;
    const h = pack.h * scale;
    ctx.clearRect(0, 0, w, h);
    const t = now * 0.001;
    const r = Math.max(1.05, 1.35 * scale);

    for (const [st, pts] of Object.entries(pack.dots)) {
      const n = counts[st] || 0;
      const ht = heat(n);
      const alive = hover === st || selected === st;
      const dim = hover && hover !== st ? 0.38 : 1;

      for (let i = 0; i < pts.length; i += 1) {
        const px = pts[i][0] * scale;
        const py = pts[i][1] * scale;
        let bright = 0.22 + ht * 0.45;
        if (alive) {
          const phase = (i * 2.399 + st.charCodeAt(0)) % (Math.PI * 2);
          const twinkle = 0.5 + 0.5 * Math.sin(t * 7.2 + phase);
          const twinkle2 = 0.5 + 0.5 * Math.sin(t * 3.1 + phase * 1.7);
          bright = 0.18 + 0.82 * (0.55 * twinkle + 0.45 * twinkle2);
          const dx = px - mouse.x;
          const dy = py - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 90) bright = Math.min(1, bright + (1 - dist / 90) * 0.55);
        }
        bright *= dim;
        ctx.beginPath();
        ctx.fillStyle = color(ht, bright);
        ctx.arc(px, py, alive ? r * (0.95 + bright * 0.35) : r, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    if (hover && pack.labels[hover]) {
      const [lx, ly] = pack.labels[hover];
      tip.hidden = false;
      tip.style.left = `${lx * scale}px`;
      tip.style.top = `${ly * scale - 18}px`;
      const n = counts[hover] || 0;
      tip.innerHTML = `<b>${NAMES[hover] || hover}</b><span>${n.toLocaleString("en-US")} tails</span>`;
    } else {
      tip.hidden = true;
    }

    raf = requestAnimationFrame(draw);
  }

  function pointer(ev) {
    const box = canvas.getBoundingClientRect();
    mouse.x = ev.clientX - box.left;
    mouse.y = ev.clientY - box.top;
    const next = hit(mouse.x, mouse.y);
    if (next !== hover) {
      hover = next;
      canvas.style.cursor = next ? "pointer" : "default";
      onHover(next);
    }
  }

  window.HangarMap = {
    mount(el, opts = {}) {
      canvas = el.querySelector("canvas");
      tip = el.querySelector(".map-tip");
      ctx = canvas.getContext("2d");
      onHover = opts.onHover || onHover;
      onPick = opts.onPick || onPick;
      resize();
      window.addEventListener("resize", resize);
      canvas.addEventListener("pointermove", pointer);
      canvas.addEventListener("pointerleave", () => {
        hover = "";
        mouse.x = -999;
        onHover("");
      });
      canvas.addEventListener("click", () => {
        if (hover) onPick(hover);
      });
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(draw);
    },
    setCounts(next) {
      counts = next || {};
    },
    setSelected(st) {
      selected = st || "";
    },
    pulse(st) {
      hover = st || hover;
    },
  };
})();
