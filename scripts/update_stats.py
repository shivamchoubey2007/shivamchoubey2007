"""Refresh the live numbers on id-dashboard.svg (dark + light) from the GitHub API.
Runs inside GitHub Actions with the built-in GITHUB_TOKEN. Standard library only."""
import datetime, json, os, pathlib, sys, urllib.parse, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from theme import to_light

ROOT = pathlib.Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER", "shivamchoubey2007")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
CACHE = ROOT / "stats.json"
DEFAULTS = {"repos": 15, "commits": None, "prs": None, "langs": 5,
            "bars": [["CSS", 2], ["TypeScript", 1], ["HTML", 1], ["JavaScript", 1], ["Jupyter Notebook", 1]]}

def api(path, **params):
    url = "https://api.github.com" + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def collect(old):
    data = dict(old)
    try:
        data["repos"] = api(f"/users/{USER}")["public_repos"]
    except Exception as e: print("repos failed:", e)
    try:
        repos = api(f"/users/{USER}/repos", per_page=100, type="owner")
        counts = {}
        for r in repos:
            if not r.get("fork") and r.get("language"):
                counts[r["language"]] = counts.get(r["language"], 0) + 1
        top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        if top:
            data["bars"] = [list(t) for t in top]; data["langs"] = len(counts)
    except Exception as e: print("languages failed:", e)
    try:
        data["commits"] = api("/search/commits", q=f"author:{USER}")["total_count"]
    except Exception as e: print("commits failed:", e)
    try:
        data["prs"] = api("/search/issues", q=f"author:{USER} type:pr is:merged")["total_count"]
    except Exception as e: print("prs failed:", e)
    return data

def show(v): return "\u2014" if v is None else f"{v:,}"

def bars_markup(bars, top=168):
    if not bars: return ""
    maxv = max(v for _, v in bars); out = []
    for i, (lang, v) in enumerate(bars):
        y = top + 66 + i * 31; w = max(14, round(v / maxv * 230))
        lang = {"Jupyter Notebook": "Jupyter"}.get(lang, lang).replace("&", "&amp;")[:14]
        out.append(f'<text x="358" y="{y+15}" class="mo" font-size="11" fill="#cbd5e1">{lang}</text>'
                   f'<rect x="470" y="{y}" width="{w}" height="20" rx="6" fill="#22d3ee" fill-opacity=".85">'
                   f'<animate attributeName="width" values="0;{w}" dur="1.1s" begin="{i*.12:.2f}s" fill="freeze"/></rect>'
                   f'<text x="{470+w+10}" y="{y+15}" class="mo" font-size="11" fill="#e2e8f0">{v}</text>')
    return "".join(out)

def fill(template, d, stamp):
    return (template.replace("{{REPOS}}", show(d["repos"])).replace("{{COMMITS}}", show(d["commits"]))
            .replace("{{PRS}}", show(d["prs"])).replace("{{LANGS}}", show(d["langs"]))
            .replace("{{LANG_BARS}}", bars_markup(d["bars"])).replace("{{UPDATED}}", stamp))

def main():
    old = DEFAULTS | (json.loads(CACHE.read_text()) if CACHE.exists() else {})
    d = collect(old) if "--offline" not in sys.argv else old
    CACHE.write_text(json.dumps(d, indent=2))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y")
    svg = fill((ROOT / "templates" / "id-dashboard.template.svg").read_text(), d, stamp)
    (ROOT / "id-dashboard.svg").write_text(svg)
    (ROOT / "id-dashboard-light.svg").write_text(to_light(svg))
    print("updated:", {k: d[k] for k in ("repos", "commits", "prs", "langs")})

if __name__ == "__main__":
    main()
