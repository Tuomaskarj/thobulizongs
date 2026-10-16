// nav.js — Yhteinen navigaatio kaikille sivuille
// Muuta tätä tiedostoa ja muutos näkyy joka sivulla automaattisesti

(function() {
  // Tunnista onko etusivu vai alisivu
  const onEtusivu = window.location.pathname === '/' || window.location.pathname.endsWith('index.html');

  const etusivu = onEtusivu ? '#hero'          : 'index.html';
  const yhteys  = onEtusivu ? '#yhteydenotto'  : 'index.html#yhteydenotto';

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

  function merkitseAktiivinen() {
    const sivu = window.location.pathname.split('/').pop() || 'index.html';
    if (sivu === 'index.html') return;
    document.querySelectorAll('.nav-links a').forEach(a => {
      const href = a.getAttribute('href');
      if (href && href.includes(sivu)) {
        a.style.color = '#fff';
        a.style.borderBottom = '2px solid #fff';
        a.style.paddingBottom = '2px';
      }
    });
  }

  // Lisätään navigaatio bodyn alkuun.
  // Ei document.write() — se ei toimi defer-skriptissä ja hidastaa sivua.
  function asenna() {
    document.body.insertAdjacentHTML('afterbegin', html);
    merkitseAktiivinen();
  }

  if (document.body) {
    asenna();
  } else {
    document.addEventListener('DOMContentLoaded', asenna);
  }
})();

// Mobiilivalikko — globaali, koska nav käyttää onclick-attribuuttia
function toggleMenu() {
  const links = document.querySelector('.nav-links');
  if (links) links.classList.toggle('open');
}
