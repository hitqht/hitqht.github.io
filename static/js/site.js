(() => {
  const nav = document.getElementById("site-nav");
  const toggle = document.getElementById("nav-toggle");
  const onScroll = () => {
    if (nav) nav.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("#site-menu a").forEach((a) => {
      a.addEventListener("click", () => {
        nav.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hero = document.getElementById("hero");
  if (hero && !reduce) {
    hero.addEventListener("pointermove", (e) => {
      const r = hero.getBoundingClientRect();
      hero.style.setProperty("--mx", `${e.clientX - r.left}px`);
      hero.style.setProperty("--my", `${e.clientY - r.top}px`);
    });
  }

  const bar = document.getElementById("read-progress");
  const article = document.querySelector("article.post");
  if (bar && article) {
    bar.hidden = false;
    const update = () => {
      const top = article.offsetTop;
      const total = Math.max(1, article.offsetHeight - window.innerHeight * 0.35);
      const scrolled = Math.min(1, Math.max(0, (window.scrollY - top + 80) / total));
      bar.style.transform = `scaleX(${scrolled})`;
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  const nodes = document.querySelectorAll(
    ".reveal, .tile, .member-card, .post-item, .pi-card, .feed-item, ol.list li, table.info tr, .featured, .timeline li, .cv-creds li, .proj-card, .book-card, .pub-card, .award-card, .engineer-feature"
  );
  if (reduce || !("IntersectionObserver" in window)) {
    nodes.forEach((el) => el.classList.add("is-in"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
    );
    nodes.forEach((el, i) => {
      el.style.setProperty("--d", `${Math.min(i * 55, 330)}ms`);
      io.observe(el);
    });
  }

  const axis = document.getElementById("cv-axis");
  if (axis) {
    const board = document.querySelector("main") || document.body;
    board.classList.add("cv-board");
    const items = () => document.querySelectorAll(".timeline li[data-year]");
    const setYear = (year, scroll) => {
      const same = axis.dataset.active === year;
      const next = same ? "" : year;
      axis.dataset.active = next;
      axis.querySelectorAll(".cv-axis-node").forEach((b) => {
        b.classList.toggle("is-on", next ? b.dataset.year === next : b.dataset.year === axis.dataset.latest);
      });
      board.classList.toggle("is-filtering", Boolean(next));
      items().forEach((li) => li.classList.toggle("is-focus", Boolean(next) && li.dataset.year === next));
      if (scroll && next) {
        const first = document.querySelector(`.timeline li[data-year="${next}"]`);
        if (first) first.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
      }
    };
    axis.querySelectorAll(".cv-axis-node").forEach((btn) => {
      btn.addEventListener("click", () => setYear(btn.dataset.year, true));
    });
  }

  document.querySelectorAll(".member-card.is-pop").forEach((card) => {
    const btn = card.querySelector(".member-face");
    const sheet = card.querySelector(".member-sheet");
    if (!btn || !sheet) return;
    document.body.appendChild(sheet);

    const setOpen = (open) => {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      card.classList.toggle("is-open", open);
    };

    btn.addEventListener("click", () => {
      document.querySelectorAll(".member-sheet[open]").forEach((other) => {
        if (other !== sheet && typeof other.close === "function") other.close();
      });
      if (typeof sheet.showModal === "function") sheet.showModal();
      else sheet.setAttribute("open", "");
      setOpen(true);
    });

    sheet.addEventListener("close", () => setOpen(false));
    sheet.addEventListener("click", (e) => {
      if (e.target === sheet) sheet.close();
    });
  });
})();

/* ---------- 论文检索 + 复制引用 ---------- */
(() => {
  const board = document.querySelector(".pub-board");
  if (!board) return;
  const cards = Array.from(board.querySelectorAll(".pub-card"));
  const groups = Array.from(board.querySelectorAll(".pub-year-group"));
  const tools = document.getElementById("pub-tools");
  const input = document.getElementById("pub-search");
  const count = document.getElementById("pub-count");
  const none = document.getElementById("pub-none");
  const lang = board.dataset.lang;

  if (tools && input) {
    tools.hidden = false;
    const norm = (s) => (s || "").toLowerCase().replace(/\s+/g, " ");
    const hay = cards.map((c) => norm([c.dataset.title, c.dataset.authors, c.dataset.journal, c.dataset.year].join(" ")));
    const apply = () => {
      const terms = norm(input.value).trim().split(" ").filter(Boolean);
      let shown = 0;
      cards.forEach((c, i) => {
        const ok = terms.every((t) => hay[i].includes(t));
        c.hidden = !ok;
        if (ok) { shown++; c.classList.add("is-in"); }
      });
      groups.forEach((g) => { g.hidden = !g.querySelector(".pub-card:not([hidden])"); });
      if (count) count.textContent = `${shown} ${count.dataset.unit}`;
      if (none) none.hidden = shown > 0;
    };
    input.addEventListener("input", apply);
    const q = new URLSearchParams(location.search).get("q");
    if (q) { input.value = q; apply(); }
  }

  // 作者 "Wang Yu, Qi Hongtuo*, et al." → 列表
  const authorList = (s) => (s || "").split(",").map((a) => a.replace(/\*/g, "").trim()).filter(Boolean);
  // "2025, 68: 103702" → {volume, pages}；"2025: 114105" → {pages}
  const parseRest = (rest) => {
    const out = {};
    const m = (rest || "").match(/^\s*\d{4}\s*(?:,\s*([^:]+))?\s*(?::\s*(.+))?$/);
    if (m) { if (m[1]) out.volume = m[1].trim(); if (m[2]) out.pages = m[2].trim(); }
    return out;
  };
  const toText = (d) => {
    const au = authorList(d.authors).join(", ").replace(/\.$/, "");
    const doi = d.doi ? ` https://doi.org/${d.doi}` : "";
    return lang === "zh"
      ? `${au}. ${d.title}[J]. ${d.journal}, ${d.rest || d.year}.${doi}`
      : `${au} (${d.year}). ${d.title}. ${d.journal}${d.rest ? `, ${d.rest.replace(/^\d{4}\s*[,:]\s*/, "")}` : ""}.${doi}`;
  };
  const toBib = (d) => {
    const names = authorList(d.authors).map((a) => {
      if (/^et al\.?$/i.test(a)) return "others";
      const parts = a.split(/\s+/);
      return parts.length > 1 ? `${parts[0]}, ${parts.slice(1).join(" ")}` : a;
    });
    const first = (names[0] || "anon").split(",")[0].toLowerCase().replace(/[^a-z]/g, "");
    const word = (d.title.match(/[A-Za-z]{4,}/) || ["paper"])[0].toLowerCase();
    const r = parseRest(d.rest);
    const f = [
      `  title   = {${d.title}}`,
      `  author  = {${names.join(" and ")}}`,
      `  journal = {${d.journal}}`,
      `  year    = {${d.year}}`,
    ];
    if (r.volume) f.push(`  volume  = {${r.volume}}`);
    if (r.pages) f.push(`  pages   = {${r.pages}}`);
    if (d.doi) f.push(`  doi     = {${d.doi}}`);
    return `@article{${first}${d.year}${word},\n${f.join(",\n")}\n}`;
  };
  const copy = async (text) => {
    try { await navigator.clipboard.writeText(text); return true; } catch (e) {}
    const ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    let ok = false; try { ok = document.execCommand("copy"); } catch (e) {}
    ta.remove(); return ok;
  };
  board.querySelectorAll(".pub-actions").forEach((el) => { el.hidden = false; });
  board.addEventListener("click", async (e) => {
    const btn = e.target.closest(".pub-cite");
    if (!btn) return;
    const d = btn.closest(".pub-card").dataset;
    const ok = await copy(btn.dataset.fmt === "bibtex" ? toBib(d) : toText(d));
    if (!ok) return;
    const label = btn.textContent;
    btn.textContent = board.dataset.copied;
    btn.classList.add("is-done");
    setTimeout(() => { btn.textContent = label; btn.classList.remove("is-done"); }, 1600);
  });
})();
