"""Build site/model-<slug>.html for every captured model (rebrand + localize + the same fixes/scripts as model.html),
then point every model card on the series page (and its filter views) at its own page."""
import sys, pathlib, re, json, shutil, subprocess, os, html as H
sys.stdout.reconfigure(encoding="utf-8")
scr = pathlib.Path(__file__).parent
root = pathlib.Path(sys.argv[1]); raw, site = root / "raw", root / "site"
slugs = json.load(open(raw / "model_slugs.json", encoding="utf-8"))
tmp_raw, tmp_site = scr / "ms_raw", scr / "ms_site"
for d in (tmp_raw, tmp_site):
    shutil.rmtree(d, ignore_errors=True); d.mkdir()
stems = []
for t, s in slugs.items():
    f = raw / "models" / s
    if f.exists():
        shutil.copy(f, tmp_raw / s); stems.append(s[:-5])
print("captured models:", len(stems), "of", len(slugs))

# 1. rebrand
src = (scr / "rebrand.py").read_text(encoding="utf-8")
src = src.replace('PAGES = ["home", "products", "product", "projects", "downloads", "news", "videos", "about", "contact"]', "PAGES = " + json.dumps(stems))
src = src.replace('    (r"^(/en)?/products/detail", "product.html"),', '    (r"^(/en)?/products/productDetails", "model.html"),\n    (r"^(/en)?/products/detail", "product.html"),')
src = src.replace('print(f"{name}: {len(html):,} bytes, brand mentions left in text: {left}")', 'pass')
sys.argv = ["rebrand.py", str(tmp_raw), str(tmp_site)]
exec(compile(src, "rebrand.py", "exec"), {"__name__": "__main__"})

# 2. localize all at once, merge assets
env = dict(os.environ, PYTHONIOENCODING="utf-8")
r = subprocess.run([sys.executable, "-I", str(scr / "localize.py"), str(tmp_site)], env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
target = site / "assets" / "simple"
for host_dir in (tmp_site / "assets").iterdir():
    for f in host_dir.rglob("*"):
        if f.is_file():
            dest = target / f.relative_to(host_dir) if host_dir.name == "kamslighting.com" else target / "_ext" / host_dir.name / f.relative_to(host_dir)
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, dest)

# 3. shared pieces taken from the finished model.html
ref = (site / "model.html").read_text(encoding="utf-8")
head_extra = re.search(r'<style id="card-links">.*?</style>\s*<script id="card-links-js">.*?</script>', ref, re.S).group(0)
gallery = re.search(r'<script id="gallery-js">.*?</script>', ref, re.S).group(0)
buttons = ref[ref.find('<script id="model-buttons-js">'):ref.find("</body>", ref.find('<script id="model-buttons-js">'))]

for stem in stems:
    h = (tmp_site / f"{stem}.html").read_text(encoding="utf-8")
    h = h.replace("assets/kamslighting.com/", "assets/simple/")
    h = re.sub(r'assets/(?!simple/)([a-z0-9.-]+\.[a-z]+)/', r'assets/simple/_ext/\1/', h)
    h = h.replace('href="https://www.kamsled.com"', 'href="#"').replace("kamsled", "simpleled").replace("data-kams-seo", "data-simple-seo")
    h = re.sub(r"KAMS ?LED", "SIMPLE LED", h)
    h = re.sub(r'href="https?://[^"]*(kamslighting|youtube|tiktok|facebook|weixin|whatsapp|wa\.me)[^"]*"', 'href="#"', h)
    h = re.sub(r"\bkams-", "simple-", h)
    h = h.replace("</head>", head_extra + gallery + "</head>", 1)
    h = h.replace("</body>", buttons + "</body>", 1)
    (site / f"{stem}.html").write_text(h, encoding="utf-8")

# 4. link cards on the series page (base list + filter templates) to their own model pages
p = site / "product.html"; h = p.read_text(encoding="utf-8")
def relink(m):
    title = H.unescape(m.group(3)).strip()
    s = slugs.get(title)
    if not s or not (site / s).exists(): return m.group(0)
    return m.group(1) + s + m.group(2) + m.group(3)
h, n = re.subn(r'(<a data-v-0d37e628="" href=")model\.html(" rel="noopener noreferrer"><img[^>]*></a><p data-v-0d37e628="" class="title">)([^<]*)', relink, h)
p.write_text(h, encoding="utf-8")
print("series-page cards relinked:", n)
