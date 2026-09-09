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

  const pops = document.querySelectorAll(".member-card.is-pop");
  if (pops.length) {
    const closePops = (except) => {
      pops.forEach((card) => {
        if (card === except) return;
        card.classList.remove("is-open");
        card.querySelector(".member-face")?.setAttribute("aria-expanded", "false");
      });
    };
    pops.forEach((card) => {
      const btn = card.querySelector(".member-face");
      btn?.addEventListener("click", (e) => {
        e.preventDefault();
        const open = !card.classList.contains("is-open");
        closePops(open ? card : null);
        card.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".member-card.is-pop")) closePops();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closePops();
    });
  }
})();
