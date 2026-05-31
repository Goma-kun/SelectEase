chrome.storage.local.get(['autoCopy'], (r) => {
  if (r.autoCopy !== undefined) document.getElementById('autoCopy').checked = r.autoCopy;
});
document.getElementById('autoCopy').addEventListener('change', (e) => {
  chrome.storage.local.set({ autoCopy: e.target.checked });
});
