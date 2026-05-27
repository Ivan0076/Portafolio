/* ============================================================
   PORTFOLIO — main.js
   ============================================================ */

// ── Custom Cursor ─────────────────────────────────────────────
(function () {
  const dot  = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  if (!dot || !ring) return;

  let mouseX = 0, mouseY = 0, ringX = 0, ringY = 0;
  let raf;

  document.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.left  = mouseX + 'px';
    dot.style.top   = mouseY + 'px';
  });

  function animateRing() {
    ringX += (mouseX - ringX) * 0.12;
    ringY += (mouseY - ringY) * 0.12;
    ring.style.left = ringX + 'px';
    ring.style.top  = ringY + 'px';
    raf = requestAnimationFrame(animateRing);
  }
  animateRing();

  // Expand on interactive elements
  document.querySelectorAll('a, button, [role=button], .filter-btn, .skill-card').forEach(el => {
    el.addEventListener('mouseenter', () => ring.classList.add('expanded'));
    el.addEventListener('mouseleave', () => ring.classList.remove('expanded'));
  });
})();

// ── Navbar scroll state ───────────────────────────────────────
(function () {
  const nav = document.getElementById('mainNav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 60);
  window.addEventListener('scroll', onScroll, { passive: true });
})();

// ── Scroll-triggered reveal ───────────────────────────────────
(function () {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(
    '.skill-card, .project-tile, .recent-card, .interest-item, .stat-card'
  ).forEach(el => {
    el.classList.add('reveal-target');
    observer.observe(el);
  });
})();

// ── Portfolio page: smooth re-filter via URL ──────────────────
// (filters use regular links — already works server-side)
// Add active transition on filter click for UX
(function () {
  const grid = document.getElementById('projectsGrid');
  const btns = document.querySelectorAll('.filter-btn');
  if (!grid || !btns.length) return;

  btns.forEach(btn => {
    btn.addEventListener('click', e => {
      grid.style.opacity = '0';
      grid.style.transform = 'translateY(8px)';
    });
  });
})();

// ── Auto-dismiss flash messages ───────────────────────────────
(function () {
  setTimeout(() => {
    document.querySelectorAll('.flash-msg').forEach(el => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 5000);
})();

// ── Inject `now` for footer year (template context fallback) ──
// (Flask handles this via context_processor if needed)
