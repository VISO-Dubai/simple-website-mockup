"""Remove remaining Kams traces behind the pages: favicon, black logo, odd CSS file, class names, video file names."""
import sys, pathlib, re, os
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding="utf-8")
site = pathlib.Path(sys.argv[1]); A = site / "assets" / "simple"

# 1. favicon: red square with a white "S", same style as the old red "K"
im = Image.new("RGBA", (256, 256), (225, 30, 37, 255))
d = ImageDraw.Draw(im)
font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 230)
box = d.textbbox((0, 0), "S", font=font)
w, h = box[2] - box[0], box[3] - box[1]
d.text(((256 - w) / 2 - box[0], (256 - h) / 2 - box[1]), "S", font=font, fill="white")
im.save(A / "favicon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
im.resize((128, 128)).save(pathlib.Path(__file__).parent / "fav_new.png")
print("favicon replaced")

# 2. black logo (login/register popup): Simple wordmark, new file name
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="260" height="80" viewBox="0 0 260 80">'
       '<text x="0" y="50" font-family="Manrope,Arial,sans-serif" font-size="52" font-weight="300" textLength="214" lengthAdjust="spacingAndGlyphs" fill="#111">simple</text>'
       '<circle cx="232" cy="45" r="6" fill="#111"/>'
       '<text x="2" y="74" font-family="Manrope,Arial,sans-serif" font-size="13" textLength="210" lengthAdjust="spacing" fill="#111">LIGHTING</text></svg>')
old = A / "img" / "kams-logo-black.be04d1d9.svg"
(A / "img" / "simple-logo-black.svg").write_text(svg, encoding="utf-8")
if old.exists(): old.unlink()

# 3. css: logo path, class names, and the bogus non-critical.css (was an HTML page)
(A / "css" / "non-critical.css").write_text("/* intentionally empty */\n", encoding="utf-8")
for css in (A / "css").glob("*.css"):
    t = css.read_text(encoding="utf-8", errors="ignore"); t0 = t
    t = t.replace("kams-logo-black.be04d1d9.svg", "simple-logo-black.svg")
    t = re.sub(r"\bkams-", "simple-", t)
    if t != t0: css.write_text(t, encoding="utf-8"); print("css fixed:", css.name)

# 4. video files whose names contain the brand
vdir = A / "prod-api" / "profile" / "upload" / "2025" / "06" / "10"
renames = {
    "KAMS company video~1_20250610174915A191.mp4": "company-video_20250610174915A191.mp4",
    "重点欢乐港湾连接道前海景观照明KAMS案例-无水印~1_20250610172350A175.mp4": "qianhai-landscape-lighting-case_20250610172350A175.mp4",
    "金曼斯布加迪展厅灯光改造【英文版B】--2分钟20191205_20250610174604A190.mp4": "bugatti-showroom-lighting_20250610174604A190.mp4",
}
for o, n in renames.items():
    if (vdir / o).exists(): os.replace(vdir / o, vdir / n)
for p in site.glob("*.html"):
    t = p.read_text(encoding="utf-8"); t0 = t
    for o, n in renames.items(): t = t.replace(o, n)
    t = re.sub(r"\bkams-", "simple-", t)
    if t != t0: p.write_text(t, encoding="utf-8"); print("page fixed:", p.name)
