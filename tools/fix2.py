import re, sys, pathlib, urllib.request
site = pathlib.Path(sys.argv[1])
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36"}
ICON_RX = re.compile(r'url\(&quot;(/(?:icons|prod-api)/[^&]+?\.ico)&quot;\)')
for p in sorted(site.glob("*.html")):
    h = p.read_text(encoding="utf-8")
    n0 = h.count("kamsled")
    h = h.replace('href="https://www.kamsled.com"', 'href="#"')
    h = h.replace("kamsled", "simpleled").replace("data-kams-seo", "data-simple-seo")
    def icon(m):
        path = m.group(1)
        dest = site / "assets" / "simple" / path.lstrip("/")
        if not dest.exists():
            try:
                with urllib.request.urlopen(urllib.request.Request("https://kamslighting.com" + path, headers=UA), timeout=60) as r:
                    data = r.read()
                dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
            except Exception as e:
                print("  FAILED", path, e); return m.group(0)
        return f'url(&quot;assets/simple/{path.lstrip("/")}&quot;)'
    h, n1 = ICON_RX.subn(icon, h)
    p.write_text(h, encoding="utf-8")
    print(f"{p.name}: kamsled replaced {n0}, icons localized {n1}")
