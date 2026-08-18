const STORIES = [
  {
    title: "What even is this?",
    body: "The FAA publishes every US-registered airplane. We kept the Cirrus ones and threw away owner names. This is paperwork, not a live radar. A plane delivered to Germany never shows up. A 2006 SR22 in Florida still does.",
  },
  {
    title: "It’s mostly 22s",
    body: "Think of three pistons and one little jet. SR22 is the classic pile. SR22T is the turbo that took over newer years. SR20 is the smaller sibling. The Vision Jet (SF50) is the gold slice — about one in twelve.",
  },
  {
    title: "See the 2009 hole?",
    body: "The vintage chart is survivors, not sales. 2006 is fat. 2009 is a crater — the financial crisis still sitting in the metal. Then the turbo arrives, then the jet. 2026 looks short because the year isn’t finished.",
  },
  {
    title: "Minnesota is hiding factory stock",
    body: "Click MN. A huge chunk of those tails are status M: still on the factory dealer certificate. That’s inventory in Duluth, not 553 Minnesotans who all bought a Cirrus for the cabin.",
  },
  {
    title: "Delaware is a filing cabinet",
    body: "FL / CA / TX are where people actually fly. DE and WY punch way above their population because that’s where you title an airplane inside an LLC. The hangar can be in Arizona. About two-thirds of this file is an LLC, not a person’s name.",
  },
  {
    title: "Eight percent have no birthday",
    body: "If you ever age the fleet off this file and skip the blanks, you’re kidding yourself. That’s the data-quality punchline. Not a fancy tool. Just count what’s missing.",
  },
];

const MODELS = ["SR20", "SR22", "SR22T", "SF50"];
const MODEL_COLOR = { SR20: "#9bb6c9", SR22: "#e0b15a", SR22T: "#7eb6d6", SF50: "#d97868" };
const ALL_STATES = "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split(" ");

const state = {
  data: [],
  models: new Set(MODELS),
  yearMin: 1999,
  yearMax: 2026,
  knownYear: false,
  pickState: "",
  story: 0,
};

const $ = (id) => document.getElementById(id);

function filtered() {
  return state.data.filter((d) => {
    if (!state.models.has(d.m)) return false;
    if (state.pickState && d.s !== state.pickState) return false;
    if (state.knownYear && d.y == null) return false;
    if (d.y != null && (d.y < state.yearMin || d.y > state.yearMax)) return false;
    if (d.y == null && (state.yearMin > 1999 || state.yearMax < 2026)) return false;
    return true;
  });
}

function fmt(n) {
  return n.toLocaleString("en-US");
}

function renderStory() {
  const s = STORIES[state.story];
  $("storyTitle").textContent = `${state.story + 1}. ${s.title}`;
  $("storyBody").textContent = s.body;
  $("storyDots").innerHTML = STORIES.map((_, i) => `<i class="${i === state.story ? "on" : ""}"></i>`).join("");
  $("storyPrev").disabled = state.story === 0;
  $("storyNext").textContent = state.story === STORIES.length - 1 ? "Again" : "Next →";
}

function renderKpis(rows) {
  const valid = rows.filter((d) => d.st === "V").length;
  const factory = rows.filter((d) => d.st === "M").length;
  const missing = rows.filter((d) => d.y == null).length;
  const jets = rows.filter((d) => d.m === "SF50").length;
  const bits = [
    [fmt(rows.length), "in this view"],
    [fmt(valid), "valid registrations"],
    [fmt(factory), "still at the factory"],
    [fmt(jets), "Vision Jets"],
    [rows.length ? `${((missing / rows.length) * 100).toFixed(1)}%` : "—", "missing a year"],
  ];
  $("kpis").innerHTML = bits.map(([n, l]) => `<div class="kpi"><b>${n}</b><span>${l}</span></div>`).join("");
}

function renderChips() {
  $("modelChips").innerHTML = MODELS.map((m) => {
    const on = state.models.has(m) ? "on" : "";
    return `<button class="chip ${on}" data-m="${m}">${m}</button>`;
  }).join("");
}

function renderYears(rows) {
  const svg = $("yearChart");
  const years = [];
  for (let y = 1999; y <= 2026; y += 1) years.push(y);
  const counts = {};
  years.forEach((y) => {
    counts[y] = { SR20: 0, SR22: 0, SR22T: 0, SF50: 0 };
  });
  rows.forEach((d) => {
    if (d.y != null && counts[d.y] && counts[d.y][d.m] != null) counts[d.y][d.m] += 1;
  });
  const max = Math.max(1, ...years.map((y) => MODELS.reduce((s, m) => s + counts[y][m], 0)));
  const W = 640;
  const H = 220;
  const pad = { l: 28, r: 8, t: 10, b: 28 };
  const iw = W - pad.l - pad.r;
  const ih = H - pad.t - pad.b;
  const bw = iw / years.length;
  let bars = "";
  years.forEach((y, i) => {
    let acc = 0;
    MODELS.forEach((m) => {
      const h = (counts[y][m] / max) * ih;
      const x = pad.l + i * bw + 1;
      const yy = pad.t + ih - acc - h;
      bars += `<rect x="${x}" y="${yy}" width="${bw - 2}" height="${h}" fill="${MODEL_COLOR[m]}"><title>${y} ${m}: ${counts[y][m]}</title></rect>`;
      acc += h;
    });
  });
  const ticks = [2000, 2005, 2010, 2015, 2020, 2025]
    .map((y) => {
      const i = years.indexOf(y);
      const x = pad.l + i * bw + bw / 2;
      return `<text x="${x}" y="${H - 8}" fill="#b3a79a" font-size="11" text-anchor="middle">${y}</text>`;
    })
    .join("");
  svg.innerHTML = `${bars}${ticks}`;
}

function stateCounts(rows) {
  const by = {};
  ALL_STATES.forEach((s) => {
    by[s] = 0;
  });
  rows.forEach((d) => {
    if (d.s && by[d.s] != null) by[d.s] += 1;
  });
  return by;
}

function renderMap(rows) {
  if (!window.HangarMap) return;
  HangarMap.setCounts(stateCounts(rows));
  HangarMap.setSelected(state.pickState);
}

function renderRegs(rows) {
  const by = {};
  rows.forEach((d) => {
    by[d.r] = (by[d.r] || 0) + 1;
  });
  const items = Object.entries(by).sort((a, b) => b[1] - a[1]);
  const max = items[0] ? items[0][1] : 1;
  $("regBars").innerHTML = items
    .map(([name, n]) => {
      const w = Math.max(4, (n / max) * 100);
      return `<div class="bar-row"><span>${name}</span><i style="width:${w}%"></i><span>${fmt(n)}</span></div>`;
    })
    .join("");
}

function showTail(d) {
  if (!d) {
    $("tailCard").className = "tail empty";
    $("tailCard").textContent = "Nothing in this filter. Loosen it.";
    return;
  }
  const year = d.y == null ? "year unknown" : d.y;
  const where = d.s || "no state";
  $("tailCard").className = "tail";
  $("tailCard").innerHTML = `
    <div class="n">N${d.n.replace(/^N/i, "")}</div>
    <div class="meta">${d.m} · ${year} · paper home ${where}</div>
    <div class="meta">${d.r} · ${d.st === "M" ? "still on the factory cert" : d.st === "V" ? "valid registration" : "status " + d.st}</div>
  `;
}

function refresh() {
  const rows = filtered();
  renderKpis(rows);
  renderYears(rows);
  renderMap(rows);
  renderRegs(rows);
}

function surprise() {
  const rows = filtered();
  if (!rows.length) {
    showTail(null);
    return;
  }
  showTail(rows[Math.floor(Math.random() * rows.length)]);
}

function findN(q) {
  const needle = q.trim().toUpperCase().replace(/^N/, "");
  if (!needle) return;
  const hit = state.data.find((d) => d.n.replace(/^N/i, "").toUpperCase() === needle);
  showTail(hit || null);
  if (hit) {
    state.models = new Set(MODELS);
    state.pickState = "";
    state.yearMin = 1999;
    state.yearMax = 2026;
    $("yearMin").value = 1999;
    $("yearMax").value = 2026;
    $("yearLabel").textContent = "1999–2026";
    renderChips();
    refresh();
  }
}

async function boot() {
  renderStory();
  renderChips();
  state.data = window.FLEET || [];
  if (!state.data.length) {
    $("tailCard").textContent = "fleet-data.js did not load. Run py -3 play/build_play.py";
    return;
  }
  refresh();
  surprise();

  const pulseStory = () => {
    if (!window.HangarMap) return;
    if (state.story === 3) HangarMap.pulse("MN");
    else if (state.story === 4) HangarMap.pulse("DE");
  };

  $("storyNext").onclick = () => {
    state.story = (state.story + 1) % STORIES.length;
    renderStory();
    pulseStory();
  };
  $("storyPrev").onclick = () => {
    state.story = Math.max(0, state.story - 1);
    renderStory();
    pulseStory();
  };

  $("modelChips").onclick = (ev) => {
    const m = ev.target.dataset.m;
    if (!m) return;
    if (state.models.has(m)) {
      if (state.models.size === 1) return;
      state.models.delete(m);
    } else state.models.add(m);
    renderChips();
    refresh();
  };

  const syncYears = () => {
    let a = Number($("yearMin").value);
    let b = Number($("yearMax").value);
    if (a > b) [a, b] = [b, a];
    state.yearMin = a;
    state.yearMax = b;
    $("yearLabel").textContent = `${a}–${b}`;
    refresh();
  };
  $("yearMin").oninput = syncYears;
  $("yearMax").oninput = syncYears;

  $("knownYear").onchange = (ev) => {
    state.knownYear = ev.target.checked;
    refresh();
  };

  if (window.HangarMap) {
    HangarMap.mount($("mapWrap"), {
      onPick(st) {
        state.pickState = state.pickState === st ? "" : st;
        refresh();
      },
    });
  }

  $("surprise").onclick = surprise;
  $("search").onchange = (ev) => findN(ev.target.value);
  $("search").onkeydown = (ev) => {
    if (ev.key === "Enter") findN(ev.target.value);
  };
}

boot();
