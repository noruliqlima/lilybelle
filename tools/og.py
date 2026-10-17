#!/usr/bin/env python3
"""Lukis gambar preview (Open Graph 1200x630) yang feminin untuk kedai & setiap beg."""
import io, math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1200, 630
FD = os.environ.get('LB_FONTS', os.path.join(os.path.dirname(__file__), 'fonts'))
ROSE, PLUM, INK, LILAC = (194, 65, 122), (123, 85, 211), (52, 33, 72), (205, 182, 247)

def font(name, size, wght=None):
    for p in [os.path.join(FD, name), '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        try:
            f = ImageFont.truetype(p, size)
            if wght:
                try: f.set_variation_by_axes([wght])
                except Exception: pass
            return f
        except Exception:
            continue
    return ImageFont.load_default()

def latar():
    im = Image.new('RGB', (W, H))
    px = im.load()
    a, b = (255, 232, 241), (236, 224, 252)
    for y in range(H):
        for x in range(0, W, 4):
            t = (x / W * .65 + y / H * .35)
            c = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
            for k in range(4):
                if x + k < W: px[x + k, y] = c
    blob = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(blob)
    for (cx, cy, r, col) in [(1050, 90, 230, (255, 184, 210, 170)), (180, 600, 260, (205, 182, 247, 150)), (720, 640, 200, (255, 205, 225, 140))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    blob = blob.filter(ImageFilter.GaussianBlur(70))
    im = Image.alpha_composite(im.convert('RGBA'), blob)
    return im

def bintang(d, cx, cy, r, col):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * .28
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col)

def hati(d, cx, cy, s, col):
    d.ellipse([cx - s, cy - s * .6, cx, cy + s * .4], fill=col)
    d.ellipse([cx, cy - s * .6, cx + s, cy + s * .4], fill=col)
    d.polygon([(cx - s * .97, cy - s * .02), (cx + s * .97, cy - s * .02), (cx, cy + s * 1.05)], fill=col)

def hiasan(im, bintangs, hatis):
    d = ImageDraw.Draw(im)
    for x, y, r in bintangs: bintang(d, x, y, r, (255, 255, 255, 235))
    for x, y, r in hatis: hati(d, x, y, r, (*ROSE, 160))

def bulat(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(im, (0, 0), m); return out

def bayang(card, blur=18, off=(0, 14), alpha=70):
    w, h = card.size; pad = blur * 3
    s = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    s.paste(Image.new('RGBA', (w, h), (80, 30, 90, alpha)), (pad + off[0], pad + off[1]), card.split()[-1])
    s = s.filter(ImageFilter.GaussianBlur(blur)); s.alpha_composite(card, (pad, pad)); return s

def polaroid(foto, size=250, sudut=0):
    f = ImageOps.fit(foto.convert('RGB'), (size, size), Image.LANCZOS)
    c = Image.new('RGBA', (size + 24, size + 64), (255, 255, 255, 255))
    c.paste(bulat(f, 10), (12, 12), bulat(f, 10))
    c = bulat(c, 16)
    d = ImageDraw.Draw(c); hati(d, (size + 24) // 2, size + 40, 9, (*ROSE, 255))
    return bayang(c).rotate(sudut, resample=Image.BICUBIC, expand=True)

def pil(d, xy, teks, f, bg, fg, padx=22, pady=12):
    x, y = xy; bb = d.textbbox((0, 0), teks, font=f); w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.rounded_rectangle([x, y, x + w + padx * 2, y + h + pady * 2], (h + pady * 2) // 2, fill=bg)
    d.text((x + padx - bb[0], y + pady - bb[1]), teks, font=f, fill=fg); return x + w + padx * 2

def logo(d, x, y):
    d.rounded_rectangle([x, y, x + 46, y + 46], 13, fill=PLUM)
    fi = font('PlayfairDisplay-Italic.ttf', 30, 700); d.text((x + 15, y + 3), 'L', font=fi, fill='white')
    d.text((x + 58, y + 4), 'Lilybelle', font=font('PlayfairDisplay.ttf', 30, 800), fill=INK)

def kedai(fotos, n, dari):
    im = latar()
    hiasan(im, [(175, 32, 12), (365, 64, 9), (515, 175, 13), (432, 500, 11), (525, 578, 8), (760, 52, 12), (1150, 82, 14), (1125, 525, 12), (575, 590, 9)],
           [(238, 58, 8), (603, 128, 9), (342, 494, 10), (630, 515, 8)])
    d = ImageDraw.Draw(im)
    logo(d, 64, 60)
    d.text((64, 140), 'STOK BARU SETIAP MINGGU', font=font('PlusJakartaSans.ttf', 19, 800), fill=ROSE, spacing=4)
    d.text((58, 168), 'Beg Idaman', font=font('GreatVibes-Regular.ttf', 108), fill=ROSE)
    d.text((64, 300), 'untuk wanita moden', font=font('PlayfairDisplay-Italic.ttf', 44, 600), fill=INK)
    fj = font('PlusJakartaSans.ttf', 24, 700); x = 64
    if n: x = pil(d, (x, 380), f'{n} beg tersedia', fj, (255, 255, 255, 235), PLUM) + 12
    if dari: pil(d, (x, 380), f'dari RM{dari}', fj, (255, 255, 255, 235), ROSE)
    cta = font('PlusJakartaSans.ttf', 26, 800)
    bx = pil(d, (64, 462), 'Lihat koleksi  →', cta, PLUM, 'white', 30, 16)
    hati(d, bx + 30, 494, 12, (*ROSE, 255))
    pos = [(640, 70, -9), (840, 150, 6), (700, 300, 4)]
    for foto, (x, y, a) in zip(fotos[:3], pos):
        im.alpha_composite(polaroid(foto, 230, a), (x, y))
    return im.convert('RGB')

def produk(foto, brand, details, harga, asal, qty, status):
    im = latar(); d = ImageDraw.Draw(im)
    card = ImageOps.fit(foto.convert('RGB'), (520, 520), Image.LANCZOS)
    c = Image.new('RGBA', (548, 548), (255, 255, 255, 255)); c.paste(bulat(card, 22), (14, 14), bulat(card, 22)); c = bulat(c, 30)
    im.alpha_composite(bayang(c, 22, (0, 16), 80).rotate(-3, resample=Image.BICUBIC, expand=True), (-10, -12))
    hiasan(im, [(875, 42, 12), (1018, 192, 9), (1150, 110, 13), (1036, 316, 9), (1000, 510, 10), (1010, 585, 8)], [(1120, 40, 10), (1100, 420, 9)])
    d = ImageDraw.Draw(im)
    logo(d, 650, 52)
    fb = font('PlayfairDisplay.ttf', 58, 800)
    t = brand
    while d.textlength(t, font=fb) > 500 and len(t) > 4: t = t[:-2]
    d.text((650, 140), t if t == brand else t + '…', font=fb, fill=INK)
    fdt = font('PlusJakartaSans.ttf', 25, 600); words, line, lines = details.title().split(), '', []
    for w in words:
        if d.textlength((line + ' ' + w).strip(), font=fdt) > 500: lines.append(line); line = w
        else: line = (line + ' ' + w).strip()
    if line: lines.append(line)
    for i, l in enumerate(lines[:2]): d.text((652, 222 + i * 36), l + ('…' if i == 1 and len(lines) > 2 else ''), font=fdt, fill=(104, 86, 128))
    fp = font('PlayfairDisplay.ttf', 64, 800)
    d.rounded_rectangle([650, 318, 650 + d.textlength(harga, font=fp) + 56, 410], 46, fill=PLUM)
    bb = d.textbbox((0, 0), harga, font=fp); d.text((678 - bb[0], 364 - (bb[1] + bb[3]) // 2), harga, font=fp, fill='white')
    if asal: d.text((650, 420), asal, font=font('PlusJakartaSans.ttf', 24, 600), fill=(150, 130, 170))
    fj = font('PlusJakartaSans.ttf', 26, 800)
    pil(d, (650, 466), status if status != 'AVAILABLE' else (f'Tinggal {qty} unit' if qty > 1 else 'Tinggal 1 unit sahaja'),
        fj, (255, 255, 255, 240), ROSE, 24, 14)
    d.text((652, 548), 'Tekan untuk lihat & tempah  →', font=font('PlusJakartaSans.ttf', 22, 700), fill=PLUM)
    return im.convert('RGB')

def simpan(im, path):
    im.save(path, 'JPEG', quality=86, optimize=True, progressive=True)
