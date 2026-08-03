// ── Mobile Nav Toggle ──
const toggle   = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');
if (toggle && mobileMenu) {
  toggle.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
  });
}

// ── Auto-dismiss flash messages after 4s ──
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => el.remove(), 4000);
});

// ── Article Body: convert ## headings and *bold* markdown ──
const body = document.getElementById('articleBody');
if (body) {
  let html = body.innerHTML;
  // Convert ## Heading
  html = html.replace(/##\s+(.+?)(<br>|<\/p>)/g, '<h2>$1</h2>');
  // Convert ### Heading
  html = html.replace(/###\s+(.+?)(<br>|<\/p>)/g, '<h3>$1</h3>');
  // Convert **bold**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Convert *italic*
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Convert `code`
  html = html.replace(/`(.+?)`/g, '<code>$1</code>');
  body.innerHTML = html;
}

// ── Smooth scroll to comments on hash ──
if (window.location.hash === '#comments') {
  const el = document.querySelector('.comments-section');
  if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 300);
}
