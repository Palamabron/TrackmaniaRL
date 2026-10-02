document.documentElement.classList.add('js');
const film = document.querySelector('#neural-film');
const toggle = document.querySelector('#film-toggle');
toggle.addEventListener('click', () => {
  const playing = toggle.getAttribute('aria-pressed') !== 'true';
  film.src = playing ? 'assets/neural-flow.gif' : 'assets/neural-poster.jpg';
  toggle.setAttribute('aria-pressed', String(playing));
  toggle.textContent = playing ? 'Stop recorded inference' : 'Play recorded inference';
});
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      document.querySelectorAll('.contents a').forEach(link => {
        const active = link.hash === `#${entry.target.id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }
  }, { rootMargin: '-5% 0px -65% 0px' });
  document.querySelectorAll('article section').forEach(section => observer.observe(section));
}
