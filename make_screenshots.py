"""SelectEase Chrome Web Store スクリーンショット生成"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 800
OUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT, exist_ok=True)

BG      = (15, 23, 42)
CARD    = (30, 41, 59)
BORDER  = (51, 65, 85)
ACCENT  = (56, 189, 248)
GREEN   = (74, 222, 128)
WHITE   = (226, 232, 240)
MUTED   = (100, 116, 139)

EMOJI_FONT_PATH = "/System/Library/Fonts/Apple Color Emoji.ttc"
JP_FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
JP_FONT      = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

def get_font(size, bold=False):
    path = JP_FONT_BOLD if bold else JP_FONT
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def get_emoji_font(size):
    try:
        return ImageFont.truetype(EMOJI_FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

def rrect(draw, xy, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

def browser_chrome(img, draw, url="https://example.com"):
    draw.rectangle([0, 0, W, 36], fill=(40, 40, 45))
    draw.rectangle([0, 36, 220, 70], fill=(28, 28, 32))
    draw.rectangle([220, 36, W, 70], fill=(50, 50, 55))
    draw.text((16, 48), "example.com", font=get_font(13), fill=(180,180,180), anchor="lm")
    for i, c in enumerate([(255,95,87),(255,189,46),(40,202,65)]):
        draw.ellipse([12+i*20,12,24+i*20,24], fill=c)
    rrect(draw, [240, 40, W-100, 66], 6, fill=(60,60,65))
    draw.text((260, 53), url, font=get_font(13), fill=(200,200,200), anchor="lm")

def draw_emoji(img, x, y, emoji, size=28, anchor="lm"):
    """絵文字をRGBA合成で描画"""
    f = get_emoji_font(size)
    tmp = Image.new("RGBA", (size*3, size*2), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    td.text((size//2, size//2), emoji, font=f, embedded_color=True, anchor=anchor)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(tmp, dest=(x - size//2, y - size//2))
    return img_rgba.convert("RGB")

def popup_panel(img, draw, px, py, pw=240, ph=90, on=True):
    rrect(draw, [px, py, px+pw, py+ph], 12, fill=CARD, outline=BORDER, width=1)
    draw.text((px+16, py+16), "SelectEase", font=get_font(14, bold=True), fill=WHITE)
    draw.text((px+16, py+44), "自動コピー", font=get_font(13), fill=WHITE)
    tx = px + pw - 58
    ty = py + 40
    rrect(draw, [tx, ty, tx+38, ty+22], 11, fill=(ACCENT if on else BORDER))
    cx = tx + (22 if on else 6)
    draw.ellipse([cx, ty+3, cx+16, ty+19], fill=(255,255,255))


# ════════════════════════════════
# 画像1: なぞるだけで自動コピー
# ════════════════════════════════
img1 = Image.new("RGB", (W, H), BG)
draw1 = ImageDraw.Draw(img1)
browser_chrome(img1, draw1)

draw1.text((80, 100), "SelectEase", font=get_font(28, bold=True), fill=ACCENT)
draw1.text((80, 142), "なぞるだけで自動コピー。Ctrl+C は不要。", font=get_font(18), fill=WHITE)

lines = [
    "Chrome拡張機能「SelectEase」は、テキストをマウスでなぞるだけで",
    "クリップボードに自動コピーする拡張機能です。",
    "",
    "コピーしたい文字列を選択すると、その場で「コピー済み」と表示され、",
    "すぐに別の場所に貼り付けることができます。",
    "",
    "Ctrl+C を押す手間が完全になくなります。",
]
ay = 200
for line in lines:
    draw1.text((80, ay), line, font=get_font(15), fill=WHITE)
    ay += 26

# 選択ハイライト
hl = Image.new("RGBA", (W, H), (0,0,0,0))
ImageDraw.Draw(hl).rectangle([80, 200, 560, 224], fill=(255, 213, 79, 90))
img1 = Image.alpha_composite(img1.convert("RGBA"), hl).convert("RGB")
draw1 = ImageDraw.Draw(img1)

# トースト
tf = get_font(13)
toast_text = "コピー済み"
tw = 100; th = 28
t_img = Image.new("RGBA", (tw, th), (0,0,0,0))
ImageDraw.Draw(t_img, "RGBA").rounded_rectangle([0,0,tw,th], radius=6, fill=(20,20,20,210))
ImageDraw.Draw(t_img).text((tw//2, th//2), toast_text, font=tf, fill=(255,255,255), anchor="mm")
img1.paste(t_img, (565, 172), t_img)

# カーソル
draw1.polygon([(556,210),(570,222),(563,222),(566,230),(562,231),(559,223),(553,228)],
              fill=(255,255,255), outline=(0,0,0))

# ポップアップ
popup_panel(img1, draw1, W-290, 120)

# キャプション
rrect(draw1, [60, H-100, W-60, H-30], 10, fill=CARD, outline=BORDER, width=1)
draw1.text((W//2, H-65), "テキストをなぞるだけで自動コピー。Ctrl+C は不要です。",
           font=get_font(16), fill=WHITE, anchor="mm")

img1.save(os.path.join(OUT, "01_auto_copy.png"))
print("01_auto_copy.png 完了")


# ════════════════════════════════
# 画像2: オン/オフ切り替え
# ════════════════════════════════
img2 = Image.new("RGB", (W, H), BG)
draw2 = ImageDraw.Draw(img2)
browser_chrome(img2, draw2)

# タイトル（⚡絵文字 + テキスト）
draw2.text((W//2, 140), "必要な時だけオフにできる", font=get_font(26, bold=True), fill=ACCENT, anchor="mm")
img2 = draw_emoji(img2, W//2 - 210, 140, "⚡", size=30)
draw2 = ImageDraw.Draw(img2)
draw2.text((W//2, 185), "拡張機能アイコンをクリックして自動コピーをオン/オフ切り替え",
           font=get_font(16), fill=MUTED, anchor="mm")

cx = W // 2
pp_y = 240
card_w = 280

# ON カード
rrect(draw2, [cx-card_w-20, pp_y, cx-20, pp_y+200], 16, fill=CARD, outline=BORDER, width=1)
draw2.text((cx-card_w-4, pp_y+18), "SelectEase", font=get_font(15, bold=True), fill=WHITE)
draw2.text((cx-card_w-4, pp_y+52), "自動コピー", font=get_font(14), fill=WHITE)
rrect(draw2, [cx-76, pp_y+48, cx-38, pp_y+70], 11, fill=ACCENT)
draw2.ellipse([cx-54, pp_y+51, cx-40, pp_y+67], fill=(255,255,255))
draw2.text((cx-card_w-4, pp_y+100), "選択と同時にコピーされます", font=get_font(13), fill=GREEN)
draw2.text((cx-card_w-4, pp_y+126), "Ctrl+C 不要", font=get_font(13), fill=MUTED)
draw2.text((cx-card_w-4, pp_y+158), "ON", font=get_font(14, bold=True), fill=ACCENT)
draw2.text((cx-card_w//2-20, pp_y-30), "オン", font=get_font(14, bold=True), fill=ACCENT, anchor="mm")

# OFF カード
rrect(draw2, [cx+20, pp_y, cx+card_w+20, pp_y+200], 16, fill=CARD, outline=BORDER, width=1)
draw2.text((cx+36, pp_y+18), "SelectEase", font=get_font(15, bold=True), fill=WHITE)
draw2.text((cx+36, pp_y+52), "自動コピー", font=get_font(14), fill=WHITE)
rrect(draw2, [cx+card_w-38, pp_y+48, cx+card_w, pp_y+70], 11, fill=BORDER)
draw2.ellipse([cx+card_w-36, pp_y+51, cx+card_w-20, pp_y+67], fill=(255,255,255))
draw2.text((cx+36, pp_y+100), "通常のブラウザ動作", font=get_font(13), fill=MUTED)
draw2.text((cx+36, pp_y+126), "Ctrl+C で手動コピー", font=get_font(13), fill=MUTED)
draw2.text((cx+36, pp_y+158), "OFF", font=get_font(14, bold=True), fill=MUTED)
draw2.text((cx+card_w//2+20, pp_y-30), "オフ", font=get_font(14, bold=True), fill=MUTED, anchor="mm")

rrect(draw2, [60, H-100, W-60, H-30], 10, fill=CARD, outline=BORDER, width=1)
draw2.text((W//2, H-65), "拡張機能アイコンから自動コピーのオン/オフをいつでも切り替え可能",
           font=get_font(16), fill=WHITE, anchor="mm")

img2.save(os.path.join(OUT, "02_toggle.png"))
print("02_toggle.png 完了")


# ════════════════════════════════
# 画像3: 活用シーン
# ════════════════════════════════
img3 = Image.new("RGB", (W, H), BG)
draw3 = ImageDraw.Draw(img3)
browser_chrome(img3, draw3)

draw3.text((W//2, 125), "こんな場面で活躍", font=get_font(26, bold=True), fill=ACCENT, anchor="mm")

use_cases = [
    ("📋", "調べ物・リサーチ",    "気になる文章をなぞるだけでメモアプリに貼れる"),
    ("📝", "議事録・要約作成",    "会議中のページから素早く引用・貼り付け"),
    ("💬", "AI・チャットへの引用","ChatGPT などに文章を貼る手間がゼロ"),
    ("🔍", "翻訳・検索",         "選択→翻訳ツールへの貼り付けがワンアクション"),
]

cw, ch = 270, 170
margin_x = 30
margin_y = 20
start_x = (W - (cw * 2 + margin_x)) // 2
start_y = 160

for i, (emoji, title, desc) in enumerate(use_cases):
    col = i % 2
    row = i // 2
    bx = start_x + col * (cw + margin_x)
    by = start_y + row * (ch + margin_y)
    rrect(draw3, [bx, by, bx+cw, by+ch], 14, fill=CARD, outline=BORDER, width=1)
    # 絵文字
    img3 = draw_emoji(img3, bx + cw//2, by + 36, emoji, size=32)
    draw3 = ImageDraw.Draw(img3)
    draw3.text((bx + cw//2, by + 74), title, font=get_font(14, bold=True), fill=WHITE, anchor="mm")
    draw3.text((bx + cw//2, by + 104), desc, font=get_font(12), fill=MUTED, anchor="mm")

# チェックポイント行
pts_y = start_y + 2*(ch + margin_y) + 16
points = [
    ("✅", "  編集欄（検索バー・入力フォーム）では自動コピーしません"),
    ("✅", "  ドラッグ選択の時だけコピー。クリックは無視します"),
    ("✅", "  すべてのページで動作（http / https）"),
]
for j, (em, txt) in enumerate(points):
    py = pts_y + j * 34
    img3 = draw_emoji(img3, W//2 - 240, py + 8, em, size=22)
    draw3 = ImageDraw.Draw(img3)
    draw3.text((W//2 - 220, py + 8), txt, font=get_font(14), fill=GREEN, anchor="lm")

rrect(draw3, [60, H-100, W-60, H-30], 10, fill=CARD, outline=BORDER, width=1)
draw3.text((W//2, H-65), "コピペ作業が多い人に。なぞるだけでどこにでも貼れます。",
           font=get_font(16), fill=WHITE, anchor="mm")

img3.save(os.path.join(OUT, "03_use_cases.png"))
print("03_use_cases.png 完了")
print("\n全スクリーンショット生成完了")
