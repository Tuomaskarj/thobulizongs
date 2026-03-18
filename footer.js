// footer.js — Yhteinen footer kaikille sivuille
// Muuta tätä tiedostoa → muutos näkyy kaikilla sivuilla

(function() {
  const html = `
    <footer>
      <div class="footer-logo">Thö Bulizongs</div>
      <p class="footer-tagline">Tanssittavaa musiikkia · Seinäjoki</p>
      <div class="footer-links">
        <a href="index.html">Etusivu</a>
        <a href="bandi.html">Bändi</a>
        <a href="keikat.html">Keikat</a>
        <a href="setlista.html">Settilista</a>
        <a href="uutiset.html">Uutiset</a>
        <a href="index.html#yhteydenotto">Yhteystiedot</a>
      </div>
      <p class="footer-copy">
        <script>document.write("&copy; " + new Date().getFullYear() + " Thö Bulizongs")</script>
      </p>
    </footer>
  `;

  document.write(html);
})();
