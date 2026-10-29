// ===== Translations (Arabic text lives in the HTML) =====
const EN = {
  nav_work: "Work",
  nav_services: "Services",
  nav_voice: "Voice Over",
  nav_contact: "Contact",
  hello: "Hello, I'm",
  name: "SHERIF <br>TALAAT",
  role: "AI Content Creator<br>&amp; Voice Over Artist",
  bio: "I design and produce AI-powered video and image ads, and give your message a voice that lands. Creativity meets strategy to make ads people see — and remember.",
  cta_work: "View My Work",
  cta_contact: "Start a Project",
  tag: "Turning ideas into<br>ads that move people.",
  stat_exp: "Week of<br>Experience",
  stat_projects: "Projects<br>Completed",
  stat_services: "Creative<br>Services",
  work_title: "Selected Projects",
  work_all: "Request a Project",
  p1: "Luxury Perfume Ad",
  p1s: "AI Video · 30s",
  p2: "Summer Drinks Campaign",
  p2s: "AI Ad Images",
  p3: "Fashion Brand Reel",
  p3s: "AI Reel + Voice Over",
  services_title: "Services & Tools",
  services_label: "Services",
  sv1: "AI Video Ads",
  sv1s: "Commercials, reels, brand films",
  sv2: "AI Ad Images",
  sv2s: "Product shots, posters, campaigns",
  sv3: "Professional Voice Over",
  sv3s: "Egyptian & MSA Arabic · Ads & documentary",
  tools_label: "Tools",
  process_title: "Work Process",
  st1: "Discover",
  st1s: "Understanding the brand, audience and goal.",
  st2: "Ideate",
  st2s: "Script, storyboard and visual direction.",
  st3: "Produce",
  st3s: "Generating images and video with AI.",
  st4: "Voice",
  st4s: "Recording the voice over and mixing sound.",
  st5: "Deliver",
  st5s: "Every format, ready to publish.",
  quote: "A great ad<br>isn't just how<br>it looks — it's how<br>it makes you feel.",
  quote_cta: "Let's create something<br>unforgettable.",
  voice_title: "Hear My Voice",
  v1: "Commercial",
  v1s: "Egyptian · Energetic",
  v2: "Documentary",
  v2s: "MSA · Calm",
  v3: "Corporate & Explainer",
  v3s: "Egyptian · Confident",
  contact_title: "Let's Work<br>Together <span class=\"red\">✦</span>",
  contact_text: "Open to new projects and collaborations. Let's make an ad that drives results.",
  contact_btn: "Available for Freelance",
  location: "Cairo, Egypt",
  footer_name: "Sherif Talaat",
};
const TITLES = {
  ar: "شريف طلعت | AI Creator & Voice Over",
  en: "Sherif Talaat | AI Creator & Voice Over",
};

const i18nEls = [...document.querySelectorAll("[data-i18n]")];
const AR = Object.fromEntries(i18nEls.map((el) => [el.dataset.i18n, el.innerHTML]));

function setLang(lang) {
  const dict = lang === "en" ? EN : AR;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "en" ? "ltr" : "rtl";
  i18nEls.forEach((el) => {
    const v = dict[el.dataset.i18n];
    if (v !== undefined) el.innerHTML = v;
  });
  document.title = TITLES[lang];
  try { localStorage.setItem("lang", lang); } catch (e) {}
}

let saved = null;
try { saved = localStorage.getItem("lang"); } catch (e) {}
if (saved === "en") setLang("en");

document.getElementById("langBtn").addEventListener("click", () =>
  setLang(document.documentElement.lang === "en" ? "ar" : "en")
);

// ===== Giant title letters =====
const giant = document.querySelector(".giant");
giant.innerHTML = [...giant.textContent].map((c, i) => `<span style="--i:${i}">${c}</span>`).join("");

// ===== Sticky nav + scroll progress =====
const nav = document.getElementById("nav");
const progress = document.querySelector(".progress");
const onScroll = () => {
  nav.classList.toggle("scrolled", scrollY > 40);
  const max = document.documentElement.scrollHeight - innerHeight;
  progress.style.transform = `scaleX(${max > 0 ? scrollY / max : 0})`;
};
addEventListener("scroll", onScroll, { passive: true });
onScroll();

// ===== Mobile menu =====
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

// ===== Reveal on scroll + stat counters =====
const countUp = (el, delay) => {
  const target = +el.dataset.count;
  setTimeout(() => {
    const start = performance.now();
    const tick = (now) => {
      const p = Math.min((now - start) / 1200, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, delay);
};

const io = new IntersectionObserver(
  (entries) =>
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("visible");
      e.target.querySelectorAll("[data-count]").forEach((el) => countUp(el, 2100));
      io.unobserve(e.target);
    }),
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

// ===== Pointer effects (desktop only) =====
if (matchMedia("(pointer: fine)").matches && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const dot = document.querySelector(".cursor");
  const ring = document.querySelector(".cursor-ring");
  let mx = 0, my = 0, rx = 0, ry = 0;
  addEventListener("mousemove", (e) => {
    if (!document.body.classList.contains("has-cursor")) { rx = e.clientX; ry = e.clientY; document.body.classList.add("has-cursor"); }
    mx = e.clientX;
    my = e.clientY;
    dot.style.transform = `translate(${mx}px, ${my}px)`;
  });
  (function follow() {
    rx += (mx - rx) * 0.18;
    ry += (my - ry) * 0.18;
    ring.style.transform = `translate(${rx}px, ${ry}px)`;
    requestAnimationFrame(follow);
  })();
  document.querySelectorAll("a, button, .project, .voice").forEach((el) => {
    el.addEventListener("mouseenter", () => ring.classList.add("hover"));
    el.addEventListener("mouseleave", () => ring.classList.remove("hover"));
  });

  // Hero parallax
  const hero = document.querySelector(".hero");
  const figure = document.querySelector(".hero-figure");
  hero.addEventListener("mousemove", (e) => {
    const x = e.clientX / innerWidth - 0.5;
    const y = e.clientY / innerHeight - 0.5;
    figure.style.setProperty("--px", `${x * -18}px`);
    figure.style.setProperty("--py", `${y * -10}px`);
    giant.style.setProperty("--gx", `${x * 30}px`);
    giant.style.setProperty("--gy", `${y * 14}px`);
  });

  // Card tilt
  document.querySelectorAll(".shot").forEach((shot) => {
    shot.addEventListener("mousemove", (e) => {
      const r = shot.getBoundingClientRect();
      shot.style.setProperty("--ry", `${((e.clientX - r.left) / r.width - 0.5) * 8}deg`);
      shot.style.setProperty("--rx", `${((e.clientY - r.top) / r.height - 0.5) * -8}deg`);
    });
    shot.addEventListener("mouseleave", () => {
      shot.style.setProperty("--rx", "0deg");
      shot.style.setProperty("--ry", "0deg");
    });
  });

  // Magnetic buttons
  document.querySelectorAll(".magnetic").forEach((btn) => {
    btn.addEventListener("mousemove", (e) => {
      const r = btn.getBoundingClientRect();
      btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.25}px, ${(e.clientY - r.top - r.height / 2) * 0.35}px)`;
    });
    btn.addEventListener("mouseleave", () => (btn.style.transform = ""));
  });
}

// ===== Voice samples — one plays at a time =====
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
