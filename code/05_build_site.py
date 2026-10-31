"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; results, page data, world outlines and city names are embedded; data/points.json and
data/names.json are loaded by the page. Facts stated in words are checked here. {{DOI}} and https://blog.tristanhotham.com/2026/10/31/architecture-styles/ stay as
placeholders for the publisher. The full-screen snippet (code/fullscreen_snippet.html) is pasted before </body>."""
import json, re
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
KEEP = {"DOI", "BLOG_URL", "DOI_URL"}


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{rnd(v):,}"
    if f == "pc": return f"{rnd(v)}%"
    if f == "f1": return f"{float(v):.1f}"
    raise ValueError(f)


def fill(tpl):
    return re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(m.group(1)), m.group(3)), tpl)


# ---- facts stated in words (page, and reused by the blog, paper and collage) ----
def check():
    t = R["time"]["dom"]
    assert t["1100"] == "romanesque" and t["1200"] == "gothic" and t["1300"] == "gothic" and t["1400"] == "gothic" and t["1500"] == "renaissance"
    assert t["1600"] == "baroque" and t["1700"] == "baroque" and t["1800"] == "neoclassical" and t["1900"] == "modern" and t["2000"] == "postmodern"
    tl = {x["c"]: x for x in R["time"]["timeline"]}
    c19 = sorted(tl[1900]["counts"].items(), key=lambda kv: -kv[1])
    assert [k for k, _ in c19[:4]] == ["modern", "historicist", "deco", "nouveau"], c19[:5]
    assert all(tl[c]["n"] < 1000 for c in range(800, 1100, 100)) and tl[1100]["n"] >= 1000
    assert R["dates"]["y2000"] > 20 * R["dates"]["y1999"] and R["dates"]["y2000"] > 20 * R["dates"]["y2001"]
    assert 18 <= R["dates"]["round100_pct"] <= 22   # 'about a fifth'
    g = R["revivals"]["gothic"]
    assert g["usa"] > g["deu"] > g["gbr"] and g["usa"] > g["pol"] and g["can"] > g["fra"]
    assert R["families"]["rank"][0] == "neoclassical" and max(R["families"]["by"], key=R["families"]["by"].get) == "neoclassical"
    assert R["revivals"]["greek"]["top"][0]["iso"] == "USA" and R["revivals"]["colonialrev"]["top"][0]["iso"] == "USA" and R["revivals"]["colonialrev"]["top"][1]["iso"] == "BRA"
    assert [x["iso"] for x in R["revivals"]["moorish"]["top"][:2]] == ["ESP", "USA"]
    assert R["capitals"]["neo_dom"] == ["Helsinki", "Washington, D.C.", "Tbilisi", "Paris", "London", "Havana"], R["capitals"]["neo_dom"]
    assert R["capitals"]["top"][0]["name"] == "Helsinki" and R["capitals"]["top"][4]["name"].startswith("Washington")
    assert [x["name"] for x in R["best"]["overall"][:3]] == ["Taj Mahal", "Statue of Liberty", "Hagia Sophia"] and R["best"]["overall"][1]["f"] == "neoclassical"
    cv = R["coverage"]
    assert [x["iso"] for x in cv["top"][:5]] == ["USA", "ESP", "DEU", "ITA", "SVK"]
    assert cv["per_million_top"][0]["iso"] == "SVK"
    gt = {r["iso"]: r for r in g["table"]}
    assert min(gt, key=lambda k: gt[k]["p10"]) == "RUS" and gt["RUS"]["p10"] < 1790
    assert gt["GBR"]["p10"] < gt["CAN"]["p10"] <= gt["AUS"]["p10"] < gt["USA"]["p10"] < gt["NZL"]["p10"] and gt["USA"]["median"] > gt["GBR"]["median"] + 20
    assert R["regions"]["irn"]["f"] == "persian" and R["regions"]["jpn"]["f"] == "japanese"


check()


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl)
    left = set(re.findall(r"\{\{([^}]+)\}\}", html))
    assert left <= KEEP, left
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    Rp = {k: R[k] for k in ("families", "time", "revivals", "capitals", "best", "coverage", "dates", "meta")}
    html = html.replace("/*RESULTS*/", J(Rp)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{k: c[k] for k in ("name", "lat", "lon", "pop", "iso", "cap")} for c in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
