const toggle = document.querySelector('.nav-toggle');
const navigation = document.querySelector('.nav-container');
function positionNavigation() {
  const bottom = document.querySelector('.toolbar').getBoundingClientRect().bottom;
  navigation.style.setProperty('--menu-top', `${bottom}px`);
}
window.addEventListener('scroll', positionNavigation, { passive: true });
window.addEventListener('resize', positionNavigation);
toggle.addEventListener('click', () => {
  positionNavigation();
  const open = navigation.classList.toggle('is-active');
  toggle.setAttribute('aria-expanded', String(open));
});
document.querySelectorAll('pre code').forEach((code) => {
  if (window.hljs) window.hljs.highlightBlock(code);
  if (!navigator.clipboard) return;
  const button = document.createElement('button');
  button.className = 'copy-code';
  button.textContent = 'Copy';
  button.setAttribute('aria-label', 'Copy code to clipboard');
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = 'Copied!';
    } catch {
      button.textContent = 'Select and copy';
    }
    setTimeout(() => { button.textContent = 'Copy'; }, 2000);
  });
  code.parentElement.before(button);
});
