// SelectEase content.js — 選択範囲を自動コピー
console.log('[SelectEase] 読み込み完了');

let autoCopyEnabled = true;

chrome.storage.local.get(['autoCopy'], (r) => {
  if (r.autoCopy !== undefined) autoCopyEnabled = r.autoCopy;
});
chrome.storage.onChanged.addListener((changes) => {
  if (changes.autoCopy) autoCopyEnabled = changes.autoCopy.newValue;
});

// ---- クリップボードコピー（フォーカスを奪わない） ----
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).catch(() => {});
}

// ---- トースト ----
let toastEl = null;
let toastTimer = null;

function showToast(msg, rect) {
  if (!toastEl) {
    toastEl = document.createElement('div');
    toastEl.id = 'selectease-toast';
    document.documentElement.appendChild(toastEl);
  }
  toastEl.textContent = msg;
  toastEl.style.left = Math.max(4, Math.min(rect.right + window.scrollX, window.innerWidth - 100)) + 'px';
  toastEl.style.top  = Math.max(4, rect.top + window.scrollY - 30) + 'px';
  toastEl.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove('show'), 900);
}

// ---- 編集可能要素は除外 ----
function isEditable(el) {
  if (!el) return false;
  return el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || !!el.isContentEditable;
}

// ---- 自動コピー ----
document.addEventListener('mouseup', (e) => {
  if (!autoCopyEnabled) return;
  if (isEditable(e.target)) return;

  const sel = window.getSelection();
  const text = sel ? sel.toString() : '';
  if (!text) return;

  const rect = sel.getRangeAt(0).getBoundingClientRect();
  copyToClipboard(text);
  showToast('コピー済み', rect);
});
