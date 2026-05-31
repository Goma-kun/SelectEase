// SelectEase content.js — 選択範囲を自動コピー
let autoCopyEnabled = true;

chrome.storage.local.get(['autoCopy'], (r) => {
  if (r.autoCopy !== undefined) autoCopyEnabled = r.autoCopy;
});
chrome.storage.onChanged.addListener((changes) => {
  if (changes.autoCopy) autoCopyEnabled = changes.autoCopy.newValue;
});

// ---- クリップボードコピー（選択範囲を保存・復元しながらexecCommand） ----
function copyToClipboard(text) {
  const sel = window.getSelection();
  const savedRanges = [];
  for (let i = 0; i < sel.rangeCount; i++) {
    savedRanges.push(sel.getRangeAt(i).cloneRange());
  }

  const ta = document.createElement('textarea');
  ta.value = text;
  Object.assign(ta.style, {
    position: 'fixed', top: '0', left: '0',
    width: '2px', height: '2px', opacity: '0',
    border: 'none', outline: 'none', boxShadow: 'none',
    background: 'transparent'
  });
  (document.body || document.documentElement).appendChild(ta);
  ta.focus();
  ta.select();
  let ok = false;
  try { ok = document.execCommand('copy'); } catch (e) {}
  ta.remove();

  // 選択範囲を復元
  sel.removeAllRanges();
  savedRanges.forEach(r => sel.addRange(r));

  // execCommandが失敗した場合はclipboard APIにフォールバック
  if (!ok) navigator.clipboard.writeText(text).catch(() => {});
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

// ---- 選択確定時にコピーを実行 ----
let lastCopiedText = '';

function handleSelection() {
  if (!autoCopyEnabled) return;

  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) return;

  const text = sel.toString();
  // 空選択になったら状態をリセット（次に同じ文字列を選んでもコピーできる）
  if (!text) { lastCopiedText = ''; return; }
  if (text === lastCopiedText) return;

  const anchor = sel.anchorNode;
  const el = anchor && anchor.nodeType === Node.TEXT_NODE ? anchor.parentElement : anchor;
  if (isEditable(el)) return;

  lastCopiedText = text;
  const rect = sel.getRangeAt(0).getBoundingClientRect();
  copyToClipboard(text);
  showToast('コピー済み', rect);
}

// マウス選択：ドラッグ中は無視し、離した瞬間だけ確定処理
document.addEventListener('mouseup', () => {
  // mouseup直後にブラウザが選択を確定するので軽く遅延
  setTimeout(handleSelection, 0);
}, true);

// キーボード選択（Shift+矢印など）：マウスを使っていないときだけ反応
let mouseDown = false;
document.addEventListener('mousedown', () => { mouseDown = true; }, true);
document.addEventListener('mouseup',   () => { mouseDown = false; }, true);

let keyboardSelTimer = null;
document.addEventListener('selectionchange', () => {
  if (mouseDown) return; // ドラッグ中の中間状態は無視
  clearTimeout(keyboardSelTimer);
  keyboardSelTimer = setTimeout(handleSelection, 300);
});
