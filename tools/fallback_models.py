"""Models whose detail page is broken on the live site: build a page from a sibling model's layout,
replacing the code, photos and specs with that model's own card data (from the series page)."""
import sys, pathlib, re, json, html as H
sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(sys.argv[1]); raw, site = root / "raw", root / "site"
slugs = json.load(open(raw / "model_slugs.json", encoding="utf-8"))
missing = [t for t, s in slugs.items() if not (raw / "models" / s).exists()]
print("missing:", len(missing))
tpl_slug = slugs["K-CL38E-2510R-R2W"]
tpl = (site / tpl_slug).read_text(encoding="utf-8")

p = site / "product.html"; ph = p.read_text(encoding="utf-8")
cards = {}
for m in re.finditer(r'<a data-v-0d37e628="" href="[^"]*" rel="noopener noreferrer"><img[^>]*src="([^"]+)"[^>]*></a><p data-v-0d37e628="" class="title">([^<]*)</p>(.*?)</div>', ph, re.S):
    t = H.unescape(m.group(2)).strip()
    specs = [H.unescape(x).strip() for x in re.findall(r'<p data-v-0d37e628="">([^<]*)</p>', m.group(3))]
    cards.setdefault(t, (m.group(1), [s for s in specs if s]))

PATCH = """<script id="fallback-model-js">
/* this model's own data (its detail page is unavailable on the source site) */
document.addEventListener('DOMContentLoaded', function () {
  var D = %s;
  var old = %s;
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var n; while ((n = walker.nextNode())) { if (n.nodeValue.indexOf(old) >= 0) n.nodeValue = n.nodeValue.split(old).join(D.code); }
  document.title = D.code + ' - Product Details - SIMPLE LED';
  var main = document.querySelector('.product-select .select-left img'); if (main) { main.src = D.img; main.alt = D.code; }
  document.querySelectorAll('.my-carousel .prodect-item').forEach(function (it, i) { if (i === 0) { it.querySelector('img').src = D.img; } else { it.remove(); } });
  var cfg = document.querySelector('.select-right');
  if (cfg) [].forEach.call(cfg.querySelectorAll('.select-color, .select-ynmt, .product-download'), function (e) { e.style.display = 'none'; });
  var right = document.querySelector('.table-right');
  if (right) {
    var rows = D.specs.filter(function (s) { return s.split(':').slice(1).join(':').trim(); }).map(function (s) { var k = s.split(':'); return '<div class="item"><span class="title">' + k[0] + ':</span><span>' + k.slice(1).join(':').trim() + '</span></div>'; }).join('');
    right.querySelectorAll('.general, .el-table, .h1').forEach(function (e, i) { e.remove(); });
    var g = document.createElement('div'); g.className = 'general';
    g.innerHTML = '<p class="h1">Key specifications</p><div class="items">' + rows + '</div><p style="margin-top:1rem;color:#888;font-size:.9rem">Detailed specifications for this model are available on request: sales@simpleled.com</p>';
    right.insertBefore(g, right.firstChild);
  }
});
</script>"""
for t in missing:
    if t not in cards: print("no card data for", t); continue
    img, specs = cards[t]
    h = tpl.replace("</head>", PATCH % (json.dumps({"code": t, "img": img, "specs": specs}, ensure_ascii=False), json.dumps("K-CL38E-2510R-R2W")) + "</head>", 1)
    (site / slugs[t]).write_text(h, encoding="utf-8")
    print("built", slugs[t], specs[:2])

def relink(m):
    t = H.unescape(m.group(3)).strip(); s = slugs.get(t)
    return m.group(1) + s + m.group(2) + m.group(3) if s and (site / s).exists() else m.group(0)
ph, n = re.subn(r'(<a data-v-0d37e628="" href=")model\.html(" rel="noopener noreferrer"><img[^>]*></a><p data-v-0d37e628="" class="title">)([^<]*)', relink, ph)
p.write_text(ph, encoding="utf-8"); print("relinked", n, "; cards still on model.html:", ph.count('href="model.html"'))
