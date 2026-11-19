"""Download every remote asset the mockup pages use and point the pages at local copies.

Usage: python -I localize.py <site_dir>
Assets go to <site_dir>/assets/<host>/<path>. External page links (<a href>) are left alone.
"""
import re, sys, pathlib, urllib.request, urllib.parse, concurrent.futures as cf, hashlib

site = pathlib.Path(sys.argv[1])
assets = site / "assets"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"}
SKIP_HOSTS = ("jivosite", "googletagmanager", "baidu", "google-analytics", "youtube.com", "facebook", "linkedin", "instagram", "twitter")

def local_path(url):
    u = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(u.path).lstrip("/") or "index"
    if u.query:  # keep distinct query variants apart (e.g. Google Fonts css2?family=...)
        stem = hashlib.md5(u.query.encode()).hexdigest()[:10]
        path = path + "_" + stem + (".css" if "fonts.googleapis" in u.netloc else "")
    path = re.sub(r'[<>:"|?*]', "_", path)
    return assets / u.netloc / path

cache = {}
def fetch(url):
    if url in cache:
        return cache[url]
    dest = local_path(url)
    ok = dest.exists() and dest.stat().st_size > 0
    if not ok:
        try:
            safe_url = urllib.parse.quote(url, safe=":/?&=%#~+,;@!$'()*[]")
            req = urllib.request.Request(safe_url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            ok = True
        except Exception as e:
            print("  FAILED", url, "-", e)
    cache[url] = dest if ok else None
    return cache[url]

def rel(dest, from_dir):
    return pathlib.Path(__import__("os").path.relpath(dest, from_dir)).as_posix()

def skip(url):
    return any(h in url for h in SKIP_HOSTS)

# ---- 1. collect asset URLs from pages
pages = sorted(site.glob("*.html"))
ATTR_RX = re.compile(r'\b(src|poster)=(["\'])(https?://[^"\']+)\2')
SRCSET_RX = re.compile(r'\bsrcset=(["\'])([^"\']+)\1')
LINK_RX = re.compile(r'<link\b[^>]*>', re.I)
URLFN_RX = re.compile(r'url\(\s*([\'"]?)(https?://[^)\'"]+)\1\s*\)')

wanted = set()
for p in pages:
    h = p.read_text(encoding="utf-8")
    wanted |= {m.group(3) for m in ATTR_RX.finditer(h)}
    for m in SRCSET_RX.finditer(h):
        wanted |= {part.strip().split(" ")[0] for part in m.group(2).split(",") if part.strip().startswith("http")}
    for tag in LINK_RX.findall(h):
        if re.search(r'rel=["\'](stylesheet|icon|shortcut icon|apple-touch-icon|preload)["\']', tag, re.I):
            m = re.search(r'href=["\'](https?://[^"\']+)["\']', tag)
            if m: wanted.add(m.group(1))
    wanted |= {m.group(2) for m in URLFN_RX.finditer(h)}
wanted = {u for u in wanted if not skip(u)}
print(f"{len(wanted)} assets referenced by the pages; downloading…")
with cf.ThreadPoolExecutor(12) as ex:
    list(ex.map(fetch, wanted))

# ---- 2. CSS files: download what they reference (fonts, icons, backgrounds) and rewrite
CSS_URL_RX = re.compile(r'url\(\s*([\'"]?)([^)\'"]+)\1\s*\)')
IMPORT_RX = re.compile(r'@import\s+([\'"])([^\'"]+)\1')
def localize_css(css_url, depth=0):
    dest = cache.get(css_url)
    if not dest or depth > 3:
        return
    text = dest.read_text(encoding="utf-8", errors="replace")
    refs = {}
    for m in list(CSS_URL_RX.finditer(text)) + list(IMPORT_RX.finditer(text)):
        ref = m.group(2).strip()
        if ref.startswith(("data:", "#")) or not ref:
            continue
        absu = urllib.parse.urljoin(css_url, ref)
        if absu.startswith("http") and not skip(absu):
            refs[ref] = absu
    with cf.ThreadPoolExecutor(12) as ex:
        list(ex.map(fetch, set(refs.values())))
    def sub(m):
        ref = m.group(2).strip(); absu = refs.get(ref)
        d = cache.get(absu) if absu else None
        if not d: return m.group(0)
        r = rel(d, dest.parent)
        return f'url("{r}")' if m.re is CSS_URL_RX else f'@import "{r}"'
    text = CSS_URL_RX.sub(sub, text); text = IMPORT_RX.sub(sub, text)
    dest.write_text(text, encoding="utf-8")
    for absu in refs.values():
        if absu.split("?")[0].endswith(".css") or "fonts.googleapis.com/css" in absu:
            localize_css(absu, depth + 1)

for u in list(wanted):
    if u.split("?")[0].endswith(".css") or "fonts.googleapis.com/css" in u:
        localize_css(u)

# ---- 3. rewrite pages
def to_local(url):
    d = cache.get(url)
    return rel(d, site) if d else url

for p in pages:
    h = p.read_text(encoding="utf-8")
    h = ATTR_RX.sub(lambda m: f'{m.group(1)}={m.group(2)}{to_local(m.group(3))}{m.group(2)}', h)
    h = SRCSET_RX.sub(lambda m: f'srcset={m.group(1)}' + ", ".join(
        " ".join([to_local(x.strip().split(" ")[0])] + x.strip().split(" ")[1:]) for x in m.group(2).split(",") if x.strip()) + m.group(1), h)
    def link_fix(tag):
        t = tag.group(0)
        if re.search(r'rel=["\'](stylesheet|icon|shortcut icon|apple-touch-icon|preload)["\']', t, re.I):
            t = re.sub(r'href=(["\'])(https?://[^"\']+)\1', lambda m: f'href={m.group(1)}{to_local(m.group(2))}{m.group(1)}', t)
        return t
    h = LINK_RX.sub(link_fix, h)
    h = URLFN_RX.sub(lambda m: f'url({m.group(1)}{to_local(m.group(2))}{m.group(1)})', h)
    p.write_text(h, encoding="utf-8")
    remaining = len(re.findall(r'(?:src|poster)=["\']https?://', h))
    print(f"{p.name}: remote src left = {remaining}")

failed = [u for u, d in cache.items() if d is None]
size = sum(f.stat().st_size for f in assets.rglob("*") if f.is_file())
print(f"downloaded {len(cache) - len(failed)} files, {size/1e6:.1f} MB; failed {len(failed)}")
