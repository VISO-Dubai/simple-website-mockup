"""Render every CL38E model detail page with headless Edge (4 in parallel) into raw/models/<slug>.html"""
import json, re, sys, os, pathlib, subprocess, concurrent.futures as cf
sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(sys.argv[1]); raw = root / "raw"
out = raw / "models"; out.mkdir(exist_ok=True)
models = json.load(open(raw / "models.json", encoding="utf-8"))
edge = os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
if not os.path.exists(edge): edge = os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")

def slug(t): return "model-" + re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_") + ".html"

def dump(item):
    i, (title, href) = item
    dest = out / slug(title)
    if dest.exists() and title in dest.read_text(encoding="utf-8", errors="ignore"):
        return title, "cached"
    prof = os.path.join(os.environ["TEMP"], f"edge-dump-prof{i % 4}")
    for attempt in range(2):
        r = subprocess.run([edge, "--headless=new", f"--user-data-dir={prof}", "--virtual-time-budget=20000",
                            "--window-size=1536,900", "--dump-dom", "https://kamslighting.com" + href],
                           capture_output=True, timeout=180)
        h = r.stdout.decode("utf-8", errors="replace")
        if title.split("/")[0] in h and "table-right" in h:
            dest.write_text(h, encoding="utf-8"); return title, "ok"
    return title, "FAILED"

with cf.ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
    for n, (t, s) in enumerate(ex.map(dump, enumerate(models.items())), 1):
        print(f"{n}/{len(models)} {s} {t}", flush=True)
json.dump({t: slug(t) for t in models}, open(raw / "model_slugs.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("done")
