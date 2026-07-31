const timeline = [
  {
    title: "Red card → automatic ban",
    plain: "Normal football punishment",
    detail: "<strong>What happened:</strong> Balogun (USA) is sent off. Under FIFA rules, a red card usually means he sits out the <em>next</em> match automatically.<br><br><strong>Why it matters:</strong> This is the standard process — no politics yet.",
  },
  {
    title: "Trump calls Infantino",
    plain: "A president picks up the phone",
    detail: "<strong>What happened:</strong> U.S. President Trump <em>publicly says</em> he called Gianni Infantino (FIFA president) about <strong>this specific</strong> suspension and asked for a review.<br><br><strong>Why it matters:</strong> Heads of state don't normally call FIFA about one player's red card. This isn't a rumor — he admitted it.",
  },
  {
    title: "FIFA committee acts",
    plain: "The case gets reopened",
    detail: "<strong>What happened:</strong> After that call, FIFA's disciplinary committee deals with Balogun's file.<br><br><strong>Why it matters:</strong> The political contact and the official action are on the same timeline. Coincidence? That's what people are fighting about.",
  },
  {
    title: "Ban paused (Article 27)",
    plain: "Player can play — with fine",
    detail: "<strong>What happened:</strong> FIFA says they didn't \"cancel\" the ban — they <strong>paused enforcing it</strong> under <strong>Article 27</strong> of their rulebook. USA's federation was fined $40,000. Balogun plays the next game.<br><br><strong>Plain English:</strong> On paper the punishment still exists; in practice he plays. FIFA says that's normal procedure.",
  },
  {
    title: "Politicians claim credit",
    plain: "\"The call worked\"",
    detail: "<strong>What happened:</strong> Political figures publicly suggest the intervention produced the outcome Trump wanted.<br><br><strong>Why it matters:</strong> Makes it harder for FIFA to say \"this had nothing to do with politics.\"",
  },
  {
    title: "Football world pushes back",
    plain: "UEFA & others condemn it",
    detail: "<strong>What happened:</strong> UEFA (Europe's football body) condemns the move. Belgium's federation calls it unjustifiable. Watchdog group FairSquare wants an ethics probe.<br><br><strong>Why it matters:</strong> This isn't only Twitter angry — institutional insiders see an integrity problem.",
  },
];

const flaws = [
  {
    id: "jurisdiction",
    title: "Wrong rulebook",
    aiQuote: "\"To prove corruption you'd need U.S. federal bribery law — honest services fraud, FCPA…\"",
    whyWrong: "This is a <strong>FIFA governance</strong> story, not a U.S. criminal court case. Leading with American bribery statutes sounds smart but sends you to the hardest, least relevant legal path.",
    jargon: "<strong>Jurisdiction</strong> = which country's rules / which organization's rules apply. Here: FIFA's own ethics code and disciplinary code come first.",
    fix: "Start with FIFA's rules on independence and fair process. Ask: did political access corrupt <em>that</em> process?",
    rightHeadline: "Use FIFA's rulebook first",
    rightBody: "The question isn't \"did Trump commit U.S. bribery?\" It's \"did FIFA's disciplinary process stay independent after a president called about one player?\" That's FIFA Ethics + Disciplinary Code — not the FBI.",
  },
  {
    id: "appearance",
    title: "It's not just \"bad optics\"",
    aiQuote: "\"The criticism is about the <em>appearance</em> of influence — not necessarily corruption.\"",
    whyWrong: "When Trump <em>admits</em> he called, we're past \"it looks suspicious.\" The intervention itself is on the record. The fight is over <strong>what that contact did</strong> to the process.",
    jargon: "<strong>Appearance vs substance</strong> = looks bad vs actually was bad. Admissions move you into substance territory.",
    fix: "Treat the call as established fact. Then analyze access, timing, and outcome — don't hide behind \"optics.\"",
    rightHeadline: "Admissions change the game",
    rightBody: "You don't need to speculate that politics got involved. Trump said he called. The remaining question: did that contact shape which cases FIFA reviewed and when? That's real analysis, not vibes.",
  },
  {
    id: "causation",
    title: "\"Maybe it would've happened anyway\"",
    aiQuote: "\"You have correlation, not causation — the review might have happened on its own.\"",
    whyWrong: "Saying something <em>could</em> have happened anyway isn't an explanation. Ordinary fans don't get a presidential hotline to FIFA's president for one red card.",
    jargon: "<strong>Causation</strong> = did A actually lead to B? Lawyers still infer it from sequence + access when direct proof is hidden.",
    fix: "Demand FIFA explain why <em>this</em> case entered review right after the call — not hand-wave with hypotheticals.",
    rightHeadline: "Possibility ≠ explanation",
    rightBody: "\"Maybe they would've reviewed it anyway\" is a guess. What we know: presidential contact → case action → player plays. FIFA owes a neutral explanation — especially when the access was extraordinary.",
  },
  {
    id: "burden",
    title: "Who has to explain what?",
    aiQuote: "\"You haven't proven corruption beyond a reasonable doubt.\"",
    whyWrong: "Criminal court standards aren't the only frame. When a powerful outsider intervenes and the outcome flips, people rightly expect <strong>FIFA to prove the process was clean</strong> — not the public to prove a secret deal.",
    jargon: "<strong>Burden of proof</strong> = who must convince whom. In governance scandals, the institution often must explain itself once the sequence looks rotten.",
    fix: "Shift the question: what did FIFA do to insulate the committee from political contact?",
    rightHeadline: "FIFA should explain — not you",
    rightBody: "You don't need a signed note saying \"do this for Trump.\" Once a head of state gets case-specific access and the player benefits, FIFA must show the committee acted independently. Silence or vague rule citations aren't enough.",
  },
  {
    id: "anchor",
    title: "Missing the key question",
    aiQuote: "(Never asks the obvious question.)",
    whyWrong: "The cleanest line in the whole story gets skipped.",
    jargon: "<strong>Anchor question</strong> = the one question that cuts through noise and forces an answer.",
    fix: "Ask it out loud: Why was a president's intervention entertained at all?",
    rightHeadline: "The question that matters",
    rightBody: "<em>Why was presidential intervention entertained before this case entered review?</em><br><br>If the honest answer is \"because he called,\" political access is already baked into the process — regardless of whether the red card was fair on football merits.",
  },
  {
    id: "asymmetry",
    title: "Ignores FIFA's track record",
    aiQuote: "\"This is an isolated controversy — we can't infer a pattern.\"",
    whyWrong: "FIFA suspended <strong>Kenya and Zimbabwe in Feb 2022</strong> for government interference — entire countries banned. Same president, different response when a U.S. president called about <strong>one red card</strong>.",
    jargon: "<strong>Enforcement asymmetry</strong> = same institution, harsher when small federations get political interference, softer when a superpower president calls about one player.",
    fix: "Compare comparable political touchpoints. Ask why one gets extinction-level punishment and the other gets Art. 27 relief.",
    rightHeadline: "Same boss, different treatment",
    rightBody: "Kenya/Zimbabwe: govt seized federations → FIFA banned all football. Balogun: presidential call → review → player plays. Different facts, same credibility test: does political access get neutral treatment? That's how you reach the conclusion without claiming \"bribery proved.\"",
  },
  {
    id: "hedge",
    title: "Hiding behind \"perspectives\"",
    aiQuote: "\"Whether it's pathetic depends on your perspective.\"",
    whyWrong: "When you have admitted facts + timeline + outcome, retreating to \"everyone sees it differently\" replaces actual analysis.",
    jargon: "<strong>Hedging</strong> = staying vague to avoid committing to a conclusion the facts support.",
    fix: "Map the facts to a conclusion. You can still note what's disputed — but don't dodge.",
    rightHeadline: "Facts deserve a real answer",
    rightBody: "Good legal analysis doesn't say \"you decide.\" It walks through: intervention (admitted) → review (happened) → benefit (player plays) → backlash (UEFA, federations). Then it asks FIFA for a credible independent explanation.",
  },
];

const patternCases = [
  {
    id: "kenya",
    flag: "🇰🇪",
    title: "Kenya — Feb 2022",
    subtitle: "Government took over the federation",
    body: "<strong>Trigger:</strong> Nov 2021 — Kenya's sports minister dissolved the Football Kenya Federation and installed a caretaker committee.<br><br><strong>FIFA response (25 Feb 2022):</strong> Infantino announced <strong>full suspension</strong> — Kenya couldn't play FIFA/CAF matches, funding cut, AFCON qualifying hit.<br><br><strong>Lifted:</strong> Nov 2022, after govt reinstated the federation's leadership.",
    outcome: "hard",
    outcomeLabel: "Entire country banned from football",
  },
  {
    id: "zimbabwe",
    flag: "🇿🇼",
    title: "Zimbabwe — Feb 2022",
    subtitle: "Government seized federation control",
    body: "<strong>Trigger:</strong> Zimbabwe's Sports Commission removed ZIFA leaders and took control (corruption/abuse allegations — FIFA said investigate <em>without</em> govt takeover).<br><br><strong>FIFA response (same day as Kenya):</strong> Same announcement — <strong>full suspension</strong>, no international play, no FIFA money.<br><br><strong>History:</strong> Zimbabwe had been suspended before for the same theme. Lifted July 2023.",
    outcome: "hard",
    outcomeLabel: "Entire country banned from football",
  },
  {
    id: "balogun",
    flag: "🇺🇸",
    title: "Balogun — 2026",
    subtitle: "President called about one red card",
    body: "<strong>Trigger:</strong> Trump <em>admits</em> calling Infantino about <strong>this player's</strong> automatic ban and asking for review.<br><br><strong>FIFA response:</strong> Committee acts → <strong>Article 27</strong> pauses the ban → USA federation fined $40k → <strong>player plays next match</strong>.<br><br><strong>Not:</strong> No federation suspension. UEFA and others still condemn it.",
    outcome: "soft",
    outcomeLabel: "Player plays — favorable outcome",
  },
];

const compareRows = [
  { label: "Political touch", left: "Government replaced federation leadership", right: "Head of state called about one player's sanction" },
  { label: "Who announced", left: "Infantino — Feb 2022 press conference", right: "Disciplinary committee + Art. 27 (after call)" },
  { label: "Immediate hit", left: "No matches, no FIFA money, qualifying damage", right: "Ban paused — player eligible" },
  { label: "FIFA framing", left: "\"Government interference\" — integrity violation", right: "\"Normal rule\" — same as Ronaldo etc." },
  { label: "Entry point", left: "Govt seized control → FIFA punished fast", right: "Presidential call → review → relief" },
];

const steelman = [
  { defense: "We used Article 27 — it's in the rulebook.", counter: "Having a rule doesn't mean you used it fairly. Did the presidential call open the door to this case?" },
  { defense: "We did the same for Ronaldo, Otamendi, Caicedo.", counter: "Those cases don't have a public record of a head-of-state call first. Same tool, different entry point." },
  { defense: "We didn't lift the ban — we paused it.", counter: "Word games. He plays = practical win. The label doesn't erase the political timeline." },
  { defense: "The committee is independent.", counter: "Independence means ignoring political pressure — not citing a rule after the president called." },
];

const rubric = [
  {
    question: "Does it talk about FIFA's rules first?",
    hint: "Not U.S. bribery law as the main frame.",
    check: "Mentions FIFA ethics / disciplinary process as the lead framework.",
  },
  {
    question: "Does it get the outcome right?",
    hint: "Ban paused under Art. 27 — not simply \"erased.\"",
    check: "Distinguishes suspended implementation vs. vacating the sanction.",
  },
  {
    question: "Does it use Trump's admission?",
    hint: "He said he called — not just \"rumors.\"",
    check: "Treats the call as established fact in the analysis.",
  },
  {
    question: "Does it address FIFA's defense?",
    hint: "Article 27 + other players' cases.",
    check: "Engages the real excuse — doesn't only attack a weak strawman.",
  },
  {
    question: "Does it ask the anchor question?",
    hint: "Why was presidential contact entertained?",
    check: "States explicitly why intervention being entertained matters.",
  },
  {
    question: "Is it clear enough for a non-lawyer?",
    hint: "No endless \"on the one hand…\"",
    check: "Plain chain: call → review → outcome → who must explain.",
  },
  {
    question: "Does it note FIFA's double standard?",
    hint: "Kenya/Zimbabwe 2022 vs Balogun.",
    check: "Compares hard federation suspensions to accommodating individual outcome.",
  },
];

const sampleAiText =
  "\"Whether this is corruption depends on perspective. Trump commenting on sports isn't unusual. " +
  "You'd need to prove causation under U.S. bribery statutes. The ban was lifted and maybe FIFA " +
  "would have reviewed it anyway. The criticism is mostly about appearances, not proof.\"";

// --- Timeline ---
const track = document.getElementById("timelineTrack");
const detail = document.getElementById("timelineDetail");

timeline.forEach((step, i) => {
  const el = document.createElement("div");
  el.className = "t-step" + (i === 0 ? " revealed" : "");
  el.innerHTML = `
    <span class="t-num">${i + 1}</span>
    <div class="t-text-wrap">
      <span class="t-text">${step.title}</span>
      <span class="t-plain">${step.plain}</span>
    </div>`;
  el.addEventListener("click", () => {
    document.querySelectorAll(".t-step").forEach((s, j) => {
      if (j <= i) s.classList.add("revealed");
    });
    document.querySelectorAll(".t-step").forEach((s) => s.classList.remove("active"));
    el.classList.add("active");
    detail.innerHTML = step.detail;
  });
  track.appendChild(el);
});

// --- Pattern / asymmetry ---
const patternGrid = document.getElementById("patternGrid");
const compareTableBody = document.getElementById("compareTableBody");
const conclusionBox = document.getElementById("conclusionBox");
const conclusionContent = document.getElementById("conclusionContent");
const lockLabel = document.getElementById("lockLabel");
const patternRead = new Set();

patternCases.forEach((c) => {
  const el = document.createElement("div");
  el.className = `pattern-card outcome-${c.outcome}`;
  el.dataset.id = c.id;
  el.innerHTML = `
    <span class="pattern-flag">${c.flag}</span>
    <h4>${c.title}</h4>
    <p class="pattern-sub">${c.subtitle}</p>
    <p class="pattern-outcome-tag">${c.outcomeLabel}</p>
    <div class="pattern-body hidden">${c.body}</div>
    <span class="pattern-cta">Tap to read</span>`;
  el.addEventListener("click", () => {
    el.classList.toggle("open");
    const body = el.querySelector(".pattern-body");
    const cta = el.querySelector(".pattern-cta");
    if (el.classList.contains("open")) {
      body.classList.remove("hidden");
      cta.textContent = "Tap to collapse";
      patternRead.add(c.id);
    } else {
      body.classList.add("hidden");
      cta.textContent = "Tap to read";
    }
    updateConclusion();
  });
  patternGrid.appendChild(el);
});

compareRows.forEach((row) => {
  const tr = document.createElement("tr");
  tr.innerHTML = `<td class="row-label">${row.label}</td><td>${row.left}</td><td>${row.right}</td>`;
  compareTableBody.appendChild(tr);
});

function updateConclusion() {
  if (patternRead.size >= 3) {
    conclusionBox.classList.remove("locked");
    conclusionContent.classList.remove("conclusion-hidden");
    lockLabel.textContent = "";
  }
}

document.getElementById("timelineReset").addEventListener("click", () => {
  document.querySelectorAll(".t-step").forEach((s, j) => {
    s.classList.toggle("revealed", j === 0);
    s.classList.remove("active");
  });
  detail.innerHTML = '<p class="placeholder">Click step 1 to start →</p>';
});

// --- Compare (linked panels) ---
const flawList = document.getElementById("flawList");
const goodContent = document.getElementById("goodContent");
const goodPanel = document.getElementById("goodPanel");

function showFlaw(f) {
  document.querySelectorAll(".flaw").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === f.id);
  });
  goodPanel.classList.add("highlight");
  goodContent.innerHTML = `
    <h4 class="good-headline">${f.rightHeadline}</h4>
    <div class="good-section">
      <span class="label">What AI said</span>
      <p class="ai-quote">${f.aiQuote}</p>
    </div>
    <div class="good-section">
      <span class="label">Why that's weak</span>
      <p>${f.whyWrong}</p>
    </div>
    <div class="good-section jargon-box">
      <span class="label">Term explained</span>
      <p>${f.jargon}</p>
    </div>
    <div class="good-section fix-box">
      <span class="label">Better take</span>
      <p>${f.rightBody}</p>
    </div>`;
  setTimeout(() => goodPanel.classList.remove("highlight"), 600);
}

flaws.forEach((f, i) => {
  const el = document.createElement("div");
  el.className = "flaw";
  el.dataset.id = f.id;
  el.innerHTML = `<div class="flaw-title">${f.title}</div><div class="flaw-teaser">${f.fix}</div>`;
  el.addEventListener("click", () => showFlaw(f));
  flawList.appendChild(el);
  if (i === 0) showFlaw(f);
});

document.getElementById("anchorQuestion").textContent =
  "Big picture: Did political access decide which cases FIFA paid attention to?";

// --- Steelman ---
const sg = document.getElementById("steelmanGrid");
steelman.forEach((s) => {
  const el = document.createElement("div");
  el.className = "steelman-card";
  el.innerHTML = `
    <div class="steelman-label">FIFA says</div>
    <div class="steelman-defense">${s.defense}</div>
    <div class="steelman-counter"><strong>Why that may not be enough:</strong> ${s.counter}</div>`;
  el.addEventListener("click", () => el.classList.toggle("revealed"));
  sg.appendChild(el);
});

// --- Rubric ---
document.getElementById("sampleAi").textContent = sampleAiText;
document.getElementById("scoreMax").textContent = rubric.length * 2;

const rubricRows = document.getElementById("rubricRows");
const scores = new Array(rubric.length).fill(null);

rubric.forEach((r, i) => {
  const row = document.createElement("div");
  row.className = "rubric-row";
  const btns = document.createElement("div");
  btns.className = "score-btns";
  ["0", "1", "2"].forEach((label, v) => {
    const b = document.createElement("button");
    b.className = "score-btn";
    b.textContent = label;
    b.title = v === 0 ? "Bad" : v === 1 ? "Partly" : "Good";
    b.addEventListener("click", () => {
      scores[i] = v;
      btns.querySelectorAll(".score-btn").forEach((x) => x.classList.remove("selected"));
      b.classList.add("selected");
      updateScore();
    });
    btns.appendChild(b);
  });
  row.innerHTML = `
    <div class="rubric-text">
      <span class="rubric-q">${i + 1}. ${r.question}</span>
      <span class="rubric-hint">${r.hint}</span>
      <span class="rubric-check">Look for: ${r.check}</span>
    </div>`;
  row.appendChild(btns);
  rubricRows.appendChild(row);
});

function updateScore() {
  const filled = scores.filter((s) => s !== null);
  const total = filled.reduce((a, b) => a + b, 0);
  document.getElementById("scoreNum").textContent = total;
  const v = document.getElementById("verdict");
  if (filled.length < rubric.length) {
    v.textContent = `${filled.length} of ${rubric.length} answered`;
    v.className = "verdict";
  } else if (total <= 6) {
    v.textContent = "Correct — you rated it weak, and it is";
    v.className = "verdict pass";
  } else if (total <= 10) {
    v.textContent = "Mixed — some parts are still too generous";
    v.className = "verdict";
  } else {
    v.textContent = "Careful — this was the bad sample";
    v.className = "verdict fail";
  }
}

// --- Tabs ---
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.panel).classList.add("active");
  });
});