import re, sys, pathlib
site = pathlib.Path(sys.argv[1])
p = site / "videos.html"
h = p.read_text(encoding="utf-8")
HERO = '<video data-v-38145048="" muted="muted" loop="loop" playsinline="" preload="none"'
srcs = iter(["assets/simple/media/CL36.9d779f2b.mp4", "assets/simple/media/CL38.7ef56bc9.mp4"])
def hero(m):
    rest = m.group(1)
    if "src=" not in rest:
        rest = f' src="{next(srcs)}"' + rest
    return '<video data-v-38145048="" muted="muted" loop="loop" playsinline="" preload="auto" autoplay' + rest + '>'
h, n = re.subn(re.escape(HERO) + r'([^>]*)>', hero, h)
print("hero videos fixed:", n)
script = """<script id="video-hero-js">
/* rotate the Videos banner (three looping clips) and keep the visible one playing */
document.addEventListener('DOMContentLoaded', function () {
  var box = document.querySelector('.banner .el-carousel__container');
  if (!box) return;
  var items = [].slice.call(box.querySelectorAll(':scope > .el-carousel__item'));
  var dots = [].slice.call(document.querySelectorAll('.banner .el-carousel__indicator'));
  items.forEach(function (it, n) {
    it.style.transform = 'none'; it.style.transition = 'opacity .9s ease';
    it.style.opacity = n === 0 ? '1' : '0'; it.style.zIndex = n === 0 ? '2' : '1';
  });
  var i = 0;
  function play(k) { var v = items[k].querySelector('video'); if (v) { var r = v.play(); if (r && r.catch) r.catch(function () {}); } }
  play(0);
  if (items.length < 2) return;
  function show(k) {
    items[i].style.opacity = '0'; items[i].style.zIndex = '1'; if (dots[i]) dots[i].classList.remove('is-active');
    i = k; items[i].style.opacity = '1'; items[i].style.zIndex = '2'; if (dots[i]) dots[i].classList.add('is-active');
    play(i);
  }
  dots.forEach(function (d, k) { d.addEventListener('click', function (e) { e.stopPropagation(); show(k); }); });
  setInterval(function () { show((i + 1) % items.length); }, 8000);
});
</script>"""
if 'id="video-hero-js"' not in h:
    h = h.replace("</head>", script + "</head>", 1)
p.write_text(h, encoding="utf-8")

for name, title in [("contact.html", "Contact Us - SIMPLE LED"), ("downloads.html", "Downloads - SIMPLE LED")]:
    q = site / name
    t = q.read_text(encoding="utf-8")
    t, k = re.subn(r"<title>[^<]*</title>", f"<title>{title}</title>", t, count=1)
    q.write_text(t, encoding="utf-8")
    print(name, "title set" if k else "no title tag")
