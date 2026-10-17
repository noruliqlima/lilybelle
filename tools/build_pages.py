#!/usr/bin/env python3
"""Jana halaman kongsi setiap beg (p/KOD.html + p/KOD.jpg) supaya WhatsApp,
Facebook dan Telegram tunjuk gambar, nama dan harga beg bila link dikongsi."""
import html, io, json, os, re, sys, time, urllib.request

API = os.environ['LB_API']
SITE = 'https://lilybelle.vercel.app/'
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

# Fon untuk gambar preview feminin (dimuat turun dari Google Fonts di GitHub)
FD = os.path.join(OUT, '..', '_fonts')
os.makedirs(FD, exist_ok=True)
for nama, path in [('PlayfairDisplay.ttf', 'ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf'),
                   ('PlayfairDisplay-Italic.ttf', 'ofl/playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf'),
                   ('GreatVibes-Regular.ttf', 'ofl/greatvibes/GreatVibes-Regular.ttf'),
                   ('PlusJakartaSans.ttf', 'ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf')]:
    try:
        if not os.path.exists(os.path.join(FD, nama)):
            open(os.path.join(FD, nama), 'wb').write(get('https://raw.githubusercontent.com/google/fonts/main/' + path))
    except Exception as ex:
        print('fon gagal', nama, ex)
os.environ['LB_FONTS'] = FD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import og
except Exception as ex:
    og = None; print('og.py gagal dimuat', ex)
from PIL import Image, ImageOps
foto_cache = {}
def foto(x, w=800):
    k = x['kod']
    if k not in foto_cache:
        foto_cache[k] = ImageOps.exif_transpose(Image.open(io.BytesIO(get(re.sub(r'=w\d+$', '=w%d' % w, x['gambar'][0]))))).convert('RGB')
    return foto_cache[k]
stamp = time.strftime('%Y%m%d%H%M')
n = 0
for x in data['items']:
    kod = x['kod']
    if not re.fullmatch(r'[A-Z]{2}-\d{3,}', kod):
        continue
    img, iw, ih = '', 600, 600
    harga = 'RM' + rm(x['harga'])
    asal = x.get('hargaAsal') or 0
    qty = int(x.get('qty') or 1)
    if x.get('gambar'):
        try:
            if og:   # kad preview feminin 1200x630: gambar + nama + harga + baki stok
                og.simpan(og.produk(foto(x), x['brand'], x['details'], harga, ('Harga asal RM%s' % rm(asal)) if asal > x['harga'] else '',
                                    qty, 'AVAILABLE' if x['status'] == 'AVAILABLE' else 'Sedang ditempah'), os.path.join(OUT, 'p', kod + '.jpg'))
                iw, ih = 1200, 630
            else:
                ImageOps.fit(foto(x), (600, 600), Image.LANCZOS).save(os.path.join(OUT, 'p', kod + '.jpg'), 'JPEG', quality=80, optimize=True, progressive=True)
            img = SITE + 'p/' + kod + '.jpg?v=' + stamp
        except Exception as ex:
            print('gambar gagal', kod, ex)
    jual = harga + (' (asal RM%s)' % rm(asal) if asal > x['harga'] else '')
    status = ('Tinggal %d unit' % qty if qty > 1 else 'Tinggal 1 unit sahaja') if x['status'] == 'AVAILABLE' else 'Sedang ditempah'
    title = '👜 %s · %s 🎀' % (x['brand'], harga)
    desc = '✨ %s · %s · %s. Tekan untuk lihat & tempah di Lilybelle 💕' % (x['details'].title(), jual, status)
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
{f'<meta property="og:image" content="{e(img)}"><meta property="og:image:width" content="{iw}"><meta property="og:image:height" content="{ih}">' if img else ''}
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

# Gambar & teks preview kedai — dijana semula setiap 30 minit dengan beg terbaru
try:
    ada = [x for x in data['items'] if x['status'] == 'AVAILABLE' and x.get('gambar')]
    pilih = ([x for x in ada if x.get('kategori') == 'HANDBAG'] or ada)[-3:][::-1]
    dari = int(min(x['harga'] for x in ada)) if ada else 0
    K = data.get('kongsi') or {}
    isi = lambda t: t.replace('{bil}', str(len(ada))).replace('{dari}', str(dari))
    poster = None
    if K.get('poster'):   # poster sendiri dari admin
        try:
            poster = ImageOps.fit(ImageOps.exif_transpose(Image.open(io.BytesIO(get(K['poster'])))).convert('RGB'), (1200, 630), Image.LANCZOS)
        except Exception as ex:
            print('poster gagal', ex)
    if poster is not None:
        poster.save(os.path.join(OUT, 'og.jpg'), 'JPEG', quality=86, optimize=True, progressive=True)
    elif og and pilih:
        og.simpan(og.kedai([foto(x, 600) for x in pilih], len(ada), dari), os.path.join(OUT, 'og.jpg'))
    ip = os.path.join(OUT, 'index.html')
    s = open(ip, encoding='utf-8').read()
    t = isi(K['tajuk']) if K.get('tajuk') else 'Lilybelle 🎀 Beg Idaman untuk Wanita Moden'
    dsc = isi(K['ayat']) if K.get('ayat') else '✨ %d beg tersedia%s · Stok baru setiap minggu. Tekan untuk lihat koleksi & tempah terus 💕' % (len(ada), (' dari RM%d' % dari) if dari else '')
    s = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % e(t), s)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % e(dsc), s)
    s = re.sub(r'(<meta property="og:image" content=")[^"]*(">)', r'\g<1>%sog.jpg?v=%s\g<2>' % (SITE, stamp), s)
    open(ip, 'w', encoding='utf-8').write(s)
    print('Preview kedai dikemas kini:', len(ada), 'beg')
except Exception as ex:
    print('preview kedai gagal', ex)
