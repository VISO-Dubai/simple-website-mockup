"""Products page: make the category buttons (Recessed Downlight, Wall Washer, ...) filter the series list like the live site."""
import sys, pathlib, re, json, urllib.request, html as H
site = pathlib.Path(sys.argv[1]); A = site / "assets" / "simple"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36"}
CATS = {"RECESSED CEILING LIGHT":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,23,24,100],"RECESSED DOWNLIGHT":[14,15,16,17,18,19,20,21,22,25,26,28],"WALL WASHER":[75,76,77,78,80],"SURFACE DOWNLIGHT":[27,29,30,31,32,33,34,35,36,38,"Surface Downlights","Outdoor Ceiling Light",99,101],"PENDANT":[39,40,41,42,43,44,45,46,47,"Suspended spotlights"],"LINEAR LIGHT":[68,69,70,71,73,"Outdoor Linear Lights",96,97,98],"GRILLE LIGHT":[48,49,50,51,52,53,56,"Grille spotlights"],"WALL LIGHT":["Outdoor Wall Lights",92,93,94,95],"INGROUND LIGHT":[85,86,87,"Underground Lights"],"TRACK LIGHT":[57,58,59,60,61,62,63,64,65,66,67,81,82,83],"SPOT LIGHT":[88,"Spike Lights",91],"MODULAR SERIES":[102,103]}
EXTRA = {
 "Surface Downlights": ("/prod-api/profile/upload/2024/10/07/CeilingSurface_20241007161017A018.png", ["Cutout Size:NO","Power:"]),
 "Outdoor Ceiling Light": ("/prod-api/profile/upload/2025/05/09/KAS-AL02-A-Black_20250509153540A029.png", ["Cutout Size:","Power:"]),
 "Suspended spotlights": ("/prod-api/profile/upload/2024/08/14/Ceiling-Suspended_20240814084746A024.png", ["Cutout Size:NO","Power:"]),
 "Outdoor Linear Lights": ("/prod-api/profile/upload/2025/07/07/LL07_20250707162752A004.png", ["Cutout Size:","Power:"]),
 "Grille spotlights": ("/prod-api/profile/upload/2024/08/14/Grille_20240814084822A025.png", ["Cutout Size:Grille spotlights","Power:Grille spotlights"]),
 "Outdoor Wall Lights": ("/prod-api/profile/upload/2024/08/14/wall_20240814085700A033.png", ["Cutout Size:NO","Power:"]),
 "Underground Lights": ("/prod-api/profile/upload/2024/08/14/Ground_20240814085301A031.png", ["Cutout Size:NO","Power:"]),
 "Spike Lights": ("/prod-api/profile/upload/2024/08/14/Garden-spot-light_20240814085351A032.png", ["Cutout Size:NO","Power:"]),
}
p = site / "products.html"; h = p.read_text(encoding="utf-8")
titles = [H.unescape(t).strip() for t in re.findall(r'class="item-title"><h2[^>]*>([^<]*)</h2>', h)]
print("local series cards:", len(titles))

cards = []
for title, (src, ps) in EXTRA.items():
    rel = src.lstrip("/"); dest = A / rel
    if not dest.exists():
        with urllib.request.urlopen(urllib.request.Request("https://kamslighting.com" + src, headers=UA), timeout=60) as r: data = r.read()
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
    body = "".join(f'<p data-v-1b4db708="">{H.escape(x)}</p>' for x in ps)
    cards.append(f'<div data-v-1b4db708="" class="item" data-extra="{H.escape(title)}"><div data-v-1b4db708="" class="item-img"><a data-v-1b4db708="" href="product.html" rel="noopener noreferrer">'
                 f'<img src="assets/simple/{rel}" data-v-1b4db708="" alt="" class="hoverImg"></a></div><div data-v-1b4db708="" class="item-text"><div data-v-1b4db708="" class="item-title">'
                 f'<h2 data-v-1b4db708="">{H.escape(title)}</h2></div><div data-v-1b4db708="">{body}</div></div></div>')

h = re.sub(r'<template id="cat-extras">.*?</template>', "", h, flags=re.S)
h = re.sub(r'<script id="category-js">.*?</script>', "", h, flags=re.S)
script = """<template id="cat-extras">""" + "".join(cards) + """</template>
<script id="category-js">
/* Products page: category buttons filter the series cards (lists taken from the live site) */
(function () {
  var CATS = """ + json.dumps(CATS) + """;
  var btns = [].slice.call(document.querySelectorAll('.series-category-item'));
  var first = document.querySelector('.item');
  if (!btns.length || !first) return;
  var box = first.parentElement;
  var items = [].slice.call(box.querySelectorAll(':scope > .item'));
  var extras = {};
  [].forEach.call(document.getElementById('cat-extras').content.children, function (c) { extras[c.getAttribute('data-extra')] = c; });
  btns.forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      btns.forEach(function (x) { x.classList.toggle('active', x === b); x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      var list = CATS[b.textContent.trim()];
      var nodes = list ? list.map(function (k) { return typeof k === 'number' ? items[k] : extras[k]; }).filter(Boolean) : items;
      items.forEach(function (it) { if (it.parentElement) it.remove(); });
      box.querySelectorAll(':scope > .item[data-extra]').forEach(function (it) { it.remove(); });
      var anchor = box.firstChild;
      nodes.forEach(function (n) { box.insertBefore(n, null); });
    });
  });
})();
</script>"""
h = h.replace("</body>", script + "</body>", 1)
p.write_text(h, encoding="utf-8")
print("products.html updated")
