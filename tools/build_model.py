"""Build site/model.html from raw/model.html using the same rebrand + localize steps, plus the later fixes."""
import sys, pathlib, re, shutil, subprocess, os
scr = pathlib.Path(__file__).parent
root = pathlib.Path(sys.argv[1])
raw, site = root / "raw", root / "site"
tmp_raw, tmp_site = scr / "m_raw", scr / "m_site"
for d in (tmp_raw, tmp_site):
    shutil.rmtree(d, ignore_errors=True); d.mkdir()
shutil.copy(raw / "model.html", tmp_raw / "model.html")

# 1. rebrand (same script, PAGES = model only, model route first)
src = (scr / "rebrand.py").read_text(encoding="utf-8")
src = src.replace('PAGES = ["home", "products", "product", "projects", "downloads", "news", "videos", "about", "contact"]', 'PAGES = ["model"]')
src = src.replace('    (r"^(/en)?/products/detail", "product.html"),', '    (r"^(/en)?/products/productDetails", "model.html"),\n    (r"^(/en)?/products/detail", "product.html"),')
sys.argv = ["rebrand.py", str(tmp_raw), str(tmp_site)]
exec(compile(src, "rebrand.py", "exec"), {"__name__": "__main__"})

# 2. localize into tmp, then merge into site/assets/simple
env = dict(os.environ, PYTHONIOENCODING="utf-8")
subprocess.run([sys.executable, "-I", str(scr / "localize.py"), str(tmp_site)], check=True, env=env)
for host_dir in (tmp_site / "assets").iterdir():
    target = site / "assets" / "simple"
    for f in host_dir.rglob("*"):
        if f.is_file():
            dest = target / f.relative_to(host_dir) if host_dir.name == "kamslighting.com" else target / "_ext" / host_dir.name / f.relative_to(host_dir)
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, dest)
h = (tmp_site / "model.html").read_text(encoding="utf-8")
h = h.replace("assets/kamslighting.com/", "assets/simple/")
h = re.sub(r'assets/(?!simple/)([a-z0-9.-]+\.[a-z]+)/', r'assets/simple/_ext/\1/', h)

# 3. later fixes: email/domain, social + live-site links, icons, shared click script
h = h.replace('href="https://www.kamsled.com"', 'href="#"').replace("kamsled", "simpleled").replace("data-kams-seo", "data-simple-seo")
h = re.sub(r'href="https?://[^"]*(kamslighting|youtube|tiktok|facebook|weixin|whatsapp|wa\.me)[^"]*"', 'href="#"', h)
idx = (site / "product.html").read_text(encoding="utf-8")
m = re.search(r'<style id="card-links">.*?</style>\s*<script id="card-links-js">.*?</script>', idx, re.S)
if m and 'id="card-links"' not in h:
    h = h.replace("</head>", m.group(0) + "</head>", 1)
(site / "model.html").write_text(h, encoding="utf-8")
print("model.html written,", len(h), "bytes; remote src left:", len(re.findall(r'(?:src|poster)=["\']https?://', h)))
