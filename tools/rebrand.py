"""Turn rendered kamslighting.com page snapshots into a static 'Simple' rebrand mockup.

Usage: python -I rebrand.py <raw_dir> <out_dir>
"""
import re, sys, pathlib, base64

raw, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
ORIGIN = "https://kamslighting.com"
PAGES = ["home", "products", "product", "projects", "downloads", "news", "videos", "about", "contact"]
ROUTES = [  # (regex on path, local file)
    (r"^/(en/?)?$", "index.html"),
    (r"^(/en)?/products/detail", "product.html"),
    (r"^(/en)?/products", "products.html"),
    (r"^(/en)?/project", "projects.html"),
    (r"^(/en)?/downloads", "downloads.html"),
    (r"^(/en)?/news", "news.html"),
    (r"^(/en)?/videos", "videos.html"),
    (r"^(/en)?/about-us", "about.html"),
    (r"^(/en)?/contact", "contact.html"),
]
M6_VIDEO = ORIGIN + "/media/M6.210bebba.mp4"

def logo_svg(color):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="260" height="80" viewBox="0 0 260 80">'
           f'<text x="0" y="50" font-family="Manrope,Arial,sans-serif" font-size="52" font-weight="300" '
           f'textLength="214" lengthAdjust="spacingAndGlyphs" fill="{color}">simple</text>'
           f'<circle cx="232" cy="45" r="6" fill="{color}"/>'
           f'<text x="2" y="74" font-family="Manrope,Arial,sans-serif" font-size="13" '
           f'textLength="210" lengthAdjust="spacing" fill="{color}">LIGHTING</text></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

LOGO_WHITE, LOGO_GREY = logo_svg("#ffffff"), logo_svg("#8a8a8a")

BRAND = [  # order matters
    (r"KAMS LED", "SIMPLE LED"), (r"KAMS LIGHTING", "SIMPLE LIGHTING"), (r"KAMSLIGHTING", "SIMPLELIGHTING"),
    (r"Kam['’]s Lighting Co\s*\(H\.K\)\.?\s*,?\s*Limited", "Simple Lighting Co. (H.K.) Limited"),
    (r"KAM['’]S", "SIMPLE"), (r"Kam['’]s", "Simple"), (r"kam['’]s", "Simple"),
    (r"\bKAMS\b", "SIMPLE"), (r"\bKams\b", "Simple"), (r"\bkams\b", "Simple"),
]
def rebrand_text(s):
    for pat, rep in BRAND:
        s = re.sub(pat, rep, s)
    return s

def local_href(url):
    path = re.sub(r"^https?://(www\.)?kamslighting\.com", "", url)
    if path.startswith(("http", "mailto:", "tel:", "#", "javascript:", "data:")):
        return None
    p = path.split("?")[0].split("#")[0]
    for rx, f in ROUTES:
        if re.match(rx, p):
            return f
    return None

TEXT_ATTRS = {"alt", "title", "content", "placeholder", "aria-label"}

def fix_tag(tag):
    name_m = re.match(r"<\s*([a-zA-Z0-9-]+)", tag)
    name = name_m.group(1).lower() if name_m else ""
    def attr(m):
        k, q, v = m.group(1), m.group(2), m.group(3)
        kl = k.lower()
        if kl == "data-src":
            v = ORIGIN + v if v.startswith("/") and not v.startswith("//") else v
            return f'data-real={q}{v}{q}'
        if kl in TEXT_ATTRS:
            v = rebrand_text(v)
        elif kl in ("src", "srcset", "poster"):
            if "logo_white" in v or "logo-white" in v:
                v = LOGO_WHITE
            elif "logo-grey" in v or "logo_grey" in v or "/logo" in v:
                v = LOGO_GREY
            elif v.startswith("/") and not v.startswith("//"):
                v = ORIGIN + v
        elif kl == "href":
            if name == "a":
                loc = local_href(v)
                if loc:
                    v = loc
                elif v.startswith("/"):
                    v = ORIGIN + v
            elif v.startswith("/") and not v.startswith("//"):
                v = ORIGIN + v
        elif kl == "style":
            v = re.sub(r"url\((['\"]?)/(?!/)", lambda mm: f"url({mm.group(1)}{ORIGIN}/", v)
        return f'{k}={q}{v}{q}'
    tag = re.sub(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)=(["\'])(.*?)\2', attr, tag, flags=re.S)
    # lazy images: the real photo is in data-src, src holds a placeholder (with the old logo)
    m = re.search(r' data-real=(["\'])(.*?)\1', tag, flags=re.S)
    if m:
        real = m.group(2)
        tag = tag.replace(m.group(0), "")
        tag = re.sub(r' src=(["\']).*?\1', "", tag, flags=re.S)
        tag = re.sub(r' lazy=(["\']).*?\1', "", tag)
        tag = re.sub(r"^<(\w+)", lambda mm: f'<{mm.group(1)} src="{real}"', tag, count=1)
    return tag

def process(html):
    # drop scripts, third-party chat widget and analytics
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<noscript\b.*?</noscript>", "", html, flags=re.S | re.I)
    html = re.sub(r'<jdiv\b.*?</jdiv>', "", html, flags=re.S | re.I)
    html = re.sub(r'<link[^>]+jivosite[^>]*>', "", html, flags=re.I)
    html = re.sub(r'<div[^>]+id="jivo[^"]*".*?</div>', "", html, flags=re.S | re.I)
    # walk tags vs text
    parts = re.split(r"(<[^>]+>)", html)
    res, in_style = [], False
    for part in parts:
        if part.startswith("<"):
            low = part.lower()
            if low.startswith("<style"): in_style = True
            if low.startswith("</style"): in_style = False
            res.append(fix_tag(part))
        else:
            if in_style:
                part = re.sub(r"url\((['\"]?)/(?!/)", lambda mm: f"url({mm.group(1)}{ORIGIN}/", part)
                res.append(part)
            else:
                res.append(rebrand_text(part))
    html = "".join(res)
    # the M6 feature video gets its source from the app script; set it directly
    html = re.sub(r'(<div[^>]*class="project-videos[^"]*"[^>]*>\s*<video)((?:(?!src=)[^>])*)>',
                  lambda m: f'{m.group(1)} src="{M6_VIDEO}" autoplay{m.group(2).replace("preload=\"none\"", "preload=\"auto\"")}>', html)
    extra = """<style>
/* catalogue carousel: show the cards as a scrollable row instead of the app-driven slider */
.catalogo-list .el-carousel__container{display:flex;gap:2rem;overflow-x:auto;height:auto !important;padding-bottom:1rem}
.catalogo-list .el-carousel__item{position:relative !important;transform:none !important;flex:0 0 calc((100% - 4rem)/3);width:auto !important;display:block !important}
.catalogo-list .el-carousel__indicators{display:none}
/* static mockup helpers */
img[lazy], img.lazy, img[data-loaded] { opacity:1 !important; }
.animate__animated { opacity:1 !important; visibility:visible !important; }
</style>
<script>
/* minimal hero slider so the banner rotates without the original app */
document.addEventListener('DOMContentLoaded',function(){
  var w=document.querySelector('.swiper-wrapper'); if(!w) return;
  var slides=w.children; if(slides.length<2) return; var i=0;
  w.style.transition='transform .8s ease';
  setInterval(function(){ i=(i+1)%slides.length; var x=slides[i].offsetLeft; w.style.transform='translate3d(-'+x+'px,0,0)'; },5000);
});
</script>"""
    html = html.replace("</head>", extra + "</head>", 1)
    return html

out.mkdir(parents=True, exist_ok=True)
for p in PAGES:
    src = raw / f"{p}.html"
    if not src.exists():
        print("missing", p); continue
    html = src.read_text(encoding="utf-8", errors="replace")
    i = html.find("<html")
    html = "<!DOCTYPE html>\n" + (html[i:] if i >= 0 else html)
    html = process(html)
    name = "index.html" if p == "home" else f"{p}.html"
    (out / name).write_text(html, encoding="utf-8")
    left = len(re.findall(r"KAMS|Kam['’]s|\bKams\b", re.sub(r"<[^>]+>", " ", html)))
    print(f"{name}: {len(html):,} bytes, brand mentions left in text: {left}")
