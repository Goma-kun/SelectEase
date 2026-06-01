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
  // コピー前のフォーカス要素を退避（コピー後に戻すため）
  const prevFocus = document.activeElement;

  (document.body || document.documentElement).appendChild(ta);
  ta.focus();
  ta.select();
  let ok = false;
  try { ok = document.execCommand('copy'); } catch (e) {}
  ta.remove();

  // 選択範囲を復元
  sel.removeAllRanges();
  savedRanges.forEach(r => sel.addRange(r));

  // 元のフォーカスを戻す
  if (prevFocus && typeof prevFocus.focus === 'function') {
    try { prevFocus.focus(); } catch (e) {}
  }

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
  const tag = el.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
  if (el.isContentEditable) return true;
  // 祖先にcontenteditableがあるかも確認
  if (el.closest && el.closest('[contenteditable=""],[contenteditable="true"]')) return true;
  return false;
}

// ---- 選択確定時にコピーを実行 ----
let lastCopiedText = '';

function handleSelection() {
  if (!autoCopyEnabled) return;

  // 入力欄など編集可能要素にフォーカスがある場合は一切介入しない
  // （検索欄の文字を選んで上書きしたいケースを邪魔しないため）
  if (isEditable(document.activeElement)) return;

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

// 「なぞった時だけ」コピーする：
// マウスを押した位置と離した位置の距離で、ドラッグ選択かどうかを判定する。
// ダブルクリックや単純クリックは距離がほぼ0なのでコピーしない。
const DRAG_THRESHOLD = 6; // px。これ以上動いたらドラッグとみなす
let downX = 0, downY = 0;

document.addEventListener('mousedown', (e) => {
  downX = e.clientX;
  downY = e.clientY;
}, true);

document.addEventListener('mouseup', (e) => {
  const moved = Math.hypot(e.clientX - downX, e.clientY - downY);
  if (moved < DRAG_THRESHOLD) return; // なぞっていない（クリック/ダブルクリック）→ 何もしない
  // mouseup直後にブラウザが選択を確定するので軽く遅延
  setTimeout(handleSelection, 0);
}, true);
