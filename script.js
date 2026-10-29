// Sticky nav
const nav = document.getElementById("nav");
addEventListener("scroll", () => nav.classList.toggle("scrolled", scrollY > 40), { passive: true });

// Mobile menu
const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");
menuBtn.addEventListener("click", () => {
  menuBtn.classList.toggle("open");
  navLinks.classList.toggle("open");
});
navLinks.querySelectorAll("a").forEach((a) =>
  a.addEventListener("click", () => {
    menuBtn.classList.remove("open");
    navLinks.classList.remove("open");
  })
);

// Reveal on scroll + stat counters
const countUp = (el) => {
  const target = +el.dataset.count;
  const start = performance.now();
  const tick = (now) => {
    const p = Math.min((now - start) / 1500, 1);
    el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
};

const io = new IntersectionObserver(
  (entries) =>
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("visible");
      e.target.querySelectorAll("[data-count]").forEach(countUp);
      io.unobserve(e.target);
    }),
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

// Work filters
document.querySelectorAll(".filter").forEach((btn) =>
  btn.addEventListener("click", () => {
    document.querySelector(".filter.active").classList.remove("active");
    btn.classList.add("active");
    const f = btn.dataset.filter;
    document.querySelectorAll(".project").forEach((w) =>
      w.classList.toggle("hide", f !== "all" && w.dataset.type !== f)
    );
  })
);

// Voice samples — one plays at a time
let current = null;
document.querySelectorAll(".voice").forEach((card, n) => {
  const wave = card.querySelector(".wave");
  for (let i = 0; i < 60; i++) {
    const bar = document.createElement("i");
    bar.style.height = 20 + Math.abs(Math.sin(i * 0.55 + n) * Math.cos(i * 0.17)) * 80 + "%";
    bar.style.animationDelay = -(i % 7) * 0.12 + "s";
    wave.appendChild(bar);
  }
  const audio = new Audio(card.dataset.src);
  const btn = card.querySelector(".voice-play");
  const stop = () => {
    audio.pause();
    card.classList.remove("playing");
    btn.textContent = "▶";
  };
  audio.addEventListener("ended", stop);
  btn.addEventListener("click", () => {
    if (current && current.audio !== audio) current.stop();
    if (audio.paused) {
      audio.play().catch(() => {});
      card.classList.add("playing");
      btn.textContent = "❚❚";
      current = { audio, stop };
    } else stop();
  });
});

document.getElementById("year").textContent = new Date().getFullYear();
