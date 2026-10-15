#!/usr/bin/env python3
"""Jana halaman kongsi setiap beg (p/KOD.html + p/KOD.jpg) supaya WhatsApp,
Facebook dan Telegram tunjuk gambar, nama dan harga beg bila link dikongsi."""
import html, io, json, os, re, sys, urllib.request

API = os.environ['LB_API']
SITE = 'https://noruliqlima.github.io/lilybelle/'
OUT = sys.argv[1] if len(sys.argv) > 1 else '_site'
UA = {'User-Agent': 'Mozilla/5.0 (Lilybelle page builder)'}

def get(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()

data = json.loads(get(API + '?a=list'))
if not data.get('ok'):
    sys.exit('API gagal: ' + str(data)[:200])
os.makedirs(os.path.join(OUT, 'p'), exist_ok=True)
rm = lambda n: ('%.2f' % n).rstrip('0').rstrip('.')
e = lambda s: html.escape(str(s), quote=True)
n = 0
for x in data['items']:
    kod = x['kod']
    if not re.fullmatch(r'[A-Z]{2}-\d{3,}', kod):
        continue
    img = ''
    if x.get('gambar'):
        try:
            b = get(re.sub(r'=w\d+$', '=w800', x['gambar'][0]))
            # Kecilkan ke 600x600 JPEG (<150KB) supaya WhatsApp pasti tunjuk gambar
            from PIL import Image, ImageOps
            im = ImageOps.exif_transpose(Image.open(io.BytesIO(b))).convert('RGB')
            im = ImageOps.fit(im, (600, 600), Image.LANCZOS)
            im.save(os.path.join(OUT, 'p', kod + '.jpg'), 'JPEG', quality=80, optimize=True, progressive=True)
            img = SITE + 'p/' + kod + '.jpg'
        except Exception as ex:
            print('gambar gagal', kod, ex)
    harga = 'RM' + rm(x['harga'])
    asal = x.get('hargaAsal') or 0
    jual = harga + (' (asal RM%s)' % rm(asal) if asal > x['harga'] else '')
    status = 'Masih ada · 1 unit sahaja' if x['status'] == 'AVAILABLE' else 'Sedang ditempah'
    title = '%s · %s' % (x['brand'], harga)
    desc = '%s. %s. %s — tempah di Lilybelle.' % (x['details'].title(), jual, status)
    url = SITE + 'p/' + kod + '.html'
    dest = SITE + '#' + kod
    page = f'''<!doctype html>
<html lang="ms"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Lilybelle</title>
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="Lilybelle">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
{f'<meta property="og:image" content="{e(img)}"><meta property="og:image:width" content="600"><meta property="og:image:height" content="600">' if img else ''}
<meta property="product:price:amount" content="{rm(x['harga'])}"><meta property="product:price:currency" content="MYR">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{e(url)}">
<meta http-equiv="refresh" content="0;url={e(dest)}">
<style>body{{font-family:system-ui,sans-serif;background:#EBE3F8;color:#2A2140;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#7B55D3;font-weight:700}}</style>
</head><body><p>Membuka <a href="{e(dest)}">{e(title)}</a>…</p>
<script>location.replace({json.dumps(dest)})</script></body></html>
'''
    with open(os.path.join(OUT, 'p', kod + '.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    n += 1
print('Halaman produk dijana:', n)
