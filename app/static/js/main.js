/* ══════════════════════════════════════════════
   EcoSnap  –  main.js
   Global interactivity: navbar, mobile, scroll
══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Navbar: add .scrolled class on scroll ──
  const navbar = document.getElementById('navbar');
  function updateNavbar() {
    if (window.scrollY > 48) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }
  window.addEventListener('scroll', updateNavbar, { passive: true });
  updateNavbar(); // run on load (for non-hero pages)

  // ── Mobile hamburger ───────────────────────
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.getElementById('navLinks');
  if (hamburger) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      hamburger.setAttribute('aria-expanded', isOpen);
      // Animate hamburger bars
      const bars = hamburger.querySelectorAll('span');
      if (isOpen) {
        bars[0].style.transform = 'rotate(45deg) translateY(7px)';
        bars[1].style.opacity   = '0';
        bars[2].style.transform = 'rotate(-45deg) translateY(-7px)';
      } else {
        bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
      }
    });

    // Close menu on nav-link click
    navLinks.querySelectorAll('.nav-link, .nav-btn').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        hamburger.querySelectorAll('span').forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
      });
    });
  }

  // ── Scroll reveal ──────────────────────────
  // Simple CSS-animation-based scroll reveal
  const observeTargets = document.querySelectorAll(
    '.step-card, .service-card, .kpi-card, .complaint-card, .chart-card'
  );
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animation = 'fadeUp .5s ease both';
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    observeTargets.forEach(t => io.observe(t));
  }

  // ── Active nav link highlight ──────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      link.style.fontWeight = '700';
      link.style.color = 'var(--green-400)';
    }
  });

});

// ── Inject keyframe for scroll reveal ─────────────────────
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeUp {
    from { opacity:0; transform: translateY(20px); }
    to   { opacity:1; transform: translateY(0); }
  }
`;
document.head.appendChild(style);
