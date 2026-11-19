"""Add working type filters (Fixed, Adjustable, ...) to site/product.html using rendered filter views in raw/filters."""
import re, sys, pathlib, urllib.request, urllib.parse
root = pathlib.Path(sys.argv[1])
site, fdir = root / "site", root / "raw" / "filters"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36"}

def content_block(h):
    """inner HTML of the first <div ... class="content"> inside .product-loading-region"""
    i = h.find('class="product-loading-region"')
    j = h.find('class="content"', i)
    start = h.find(">", j) + 1
    depth, pos = 1, start
    for m in re.compile(r"<(/?)div\b[^>]*>").finditer(h, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return h[start:m.start()], start, m.start()
    raise ValueError("no content block")

def local_img(src):
    if not src.startswith("/"):
        return src
    rel = urllib.parse.unquote(src).lstrip("/")
    dest = site / "assets" / "simple" / rel
    if not dest.exists():
        url = "https://kamslighting.com" + urllib.parse.quote(urllib.parse.unquote(src), safe="/")
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            data = r.read()
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
    return "assets/simple/" + rel

def clean(block):
    block = re.sub(r'src="(/[^"]+)"', lambda m: f'src="{local_img(m.group(1))}"', block)
    block = re.sub(r'href="/en/products/productDetails[^"]*"', 'href="model.html"', block)
    block = re.sub(r"KAMS ?LED|KAMS|Kams|Kam['’]s", lambda m: "SIMPLE LED" if "LED" in m.group(0) else "Simple", block)
    return block

templates = []
for name in ["Fixed", "Adjustable", "Trim", "Trimless", "Round", "Square", "Wallwasher"]:
    h = (fdir / f"{name}.html").read_text(encoding="utf-8", errors="replace")
    block, _, _ = content_block(h)
    block = clean(block)
    n = block.count('class="title"')
    titles = re.findall(r'class="title">([^<]*)', block)[:2]
    print(f"{name}: {n} cards, first {titles}")
    templates.append(f'<template data-filter="{name}">{block}</template>')

p = site / "product.html"
h = p.read_text(encoding="utf-8")
h = re.sub(r'<div id="filter-templates".*?</div><!--/filter-templates-->', "", h, flags=re.S)
h = re.sub(r'<script id="filter-js">.*?</script>', "", h, flags=re.S)
h = h.replace("</body>", '<div id="filter-templates" hidden>' + "".join(templates) + "</div><!--/filter-templates-->" + """
<script id="filter-js">
/* series page: the type buttons (All, Fixed, Adjustable, ...) swap in the matching models */
(function () {
  var box = document.querySelector('.product-loading-region .content');
  var bar = document.querySelector('.type-buttons');
  if (!box || !bar) return;
  var all = box.innerHTML;
  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('.type-buttons > *'); if (!btn) return;
    var name = (btn.querySelector('.type-name') || btn).textContent.trim();
    [].forEach.call(bar.children, function (b) { b.classList.toggle('active', b === btn); });
    var tpl = document.querySelector('#filter-templates template[data-filter="' + name + '"]');
    box.innerHTML = tpl ? tpl.innerHTML : all;
  });
})();
</script></body>""", 1)
p.write_text(h, encoding="utf-8")
print("product.html updated")
