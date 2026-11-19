import re, sys, pathlib, urllib.parse, collections
site = pathlib.Path(sys.argv[1])
pages = sorted(site.glob("*.html"))
names = {p.name for p in pages}
for p in pages:
    h = p.read_text(encoding="utf-8")
    text = re.sub(r"<style\b.*?</style>|<script\b.*?</script>", " ", h, flags=re.S | re.I)
    textonly = re.sub(r"<[^>]+>", " ", text)
    brand_text = re.findall(r".{0,30}(?:KAMS|Kam['’]s|\bKams\b|kamslighting).{0,30}", textonly, re.I)
    brand_attr = re.findall(r'(?:alt|title|content|placeholder|aria-label)=["\'][^"\']*(?:kams|kam[\'’]s)[^"\']*["\']', h, re.I)
    remote = re.findall(r'(?:src|poster|srcset|href)=["\'](https?://[^"\']+)', h)
    remote_res = [u for u in remote if not re.search(r'<a\b', '')]
    # resource refs (not <a>)
    res_refs = re.findall(r'<(?!a\b)[a-z]+\b[^>]*?\b(?:src|poster|href)=["\']([^"\'#]+)["\']', h, re.I)
    res_refs += re.findall(r'url\(\s*["\']?([^)"\']+)', h)
    missing, remote_r = set(), set()
    for r in res_refs:
        if r.startswith("data:") or r.startswith("mailto:") or r.startswith("tel:"): continue
        if r.startswith(("http://", "https://", "//")): remote_r.add(r); continue
        f = site / urllib.parse.unquote(r.split("?")[0])
        if not f.exists(): missing.add(r)
    a_hrefs = collections.Counter(re.findall(r'<a\b[^>]*\bhref=["\']([^"\']*)["\']', h, re.I))
    bad_links = {k: v for k, v in a_hrefs.items() if k and not k.startswith(("#", "mailto:", "tel:", "javascript:")) and k.split("?")[0].split("#")[0] not in names}
    print(f"== {p.name}")
    print(f"  brand text: {len(brand_text)} {brand_text[:5]}")
    print(f"  brand attrs: {len(brand_attr)} {brand_attr[:3]}")
    print(f"  remote resources: {len(remote_r)} {sorted(remote_r)[:5]}")
    print(f"  missing local files: {len(missing)} {sorted(missing)[:8]}")
    print(f"  <a> targets: {dict(a_hrefs.most_common(12))}")
    print(f"  bad <a> links: {bad_links}")
