// nav.js — Yhteinen navigaatio kaikille sivuille
// Muuta tätä tiedostoa ja muutos näkyy joka sivulla automaattisesti

(function() {
  // Tunnista onko etusivu vai alisivu
  const onEtusivu = window.location.pathname === '/' || window.location.pathname.endsWith('index.html');

  const etusivu   = onEtusivu ? '#hero'         : 'index.html';
  const yhteys    = onEtusivu ? '#yhteydenotto'  : 'index.html#yhteydenotto';

  const html = `
    <nav id="main-nav">
      <a href="${etusivu}" class="nav-logo">Thö Bulizongs</a>
      <ul class="nav-links">
        <li><a href="${etusivu}">Etusivu</a></li>
        <li><a href="bandi.html">Bändi</a></li>
        <li><a href="keikat.html">Keikat</a></li>
        <li><a href="setlista.html">Settilista</a></li>
        <li><a href="uutiset.html">Uutiset</a></li>
        <li><a href="${yhteys}" class="nav-cta">Tilaa keikka</a></li>
      </ul>
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Valikko">
        <span></span><span></span><span></span>
      </button>
    </nav>
  `;

  // Kirjoita nav sivulle
  document.write(html);

  // Merkitse aktiivinen sivu
  document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(a => {
      const href = a.getAttribute('href');
      if (href && href.includes(path) && path !== 'index.html') {
        a.style.color = '#fff';
        a.style.borderBottom = '2px solid #c0392b';
        a.style.paddingBottom = '2px';
      }
    });
  });
})();

// Mobiilivalikko
function toggleMenu() {
  const links = document.querySelector('.nav-links');
  links.classList.toggle('open');
}
