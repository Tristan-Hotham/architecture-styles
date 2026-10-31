"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
{{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/architecture-styles/ stay as placeholders for the publisher."""
import re, zipfile, json as _json
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release")
NAME = "Hotham_Styles_in_Stone"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}


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


# facts stated in words in the blog (alt text included); the page build checks the rest
import importlib.util
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
cp = [(c["name"], rnd(c["neo_pct"])) for c in R["capitals"]["top"][:12]]
assert cp == [("Helsinki", 33), ("Dublin", 30), ("Minsk", 28), ("Santiago", 28), ("Washington, D.C.", 28), ("Moscow", 27), ("Tbilisi", 27),
              ("København", 27), ("Warsaw", 24), ("Vilnius", 23), ("Paris", 20), ("London", 20)], cp
assert [(c["iso"], c["pct"]) for c in R["coverage"]["top"][:8]] == [("USA", 22.3), ("ESP", 20.7), ("DEU", 6.0), ("ITA", 6.0), ("SVK", 5.8), ("CZE", 4.6), ("POL", 4.1), ("FRA", 3.9)]
assert [c["iso"] for c in R["coverage"]["top"][8:12]] == ["BEL", "RUS", "GBR", "NLD"]
assert [(c["name"], c["pct"]) for c in R["coverage"]["continents"]] == [("Europe", 67.9), ("North America", 24.0), ("Asia", 5.6), ("South America", 1.7), ("Oceania", 0.5), ("Africa", 0.4)]
assert R["coverage"]["n"] == 180451 and 45 <= R["dates"]["pct"] < 50
assert R["families"]["by"]["neoclassical"] == max(R["families"]["by"].values())

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Styles in stone: the world's architectural styles on a map, century by century",
        "slug": SLUG,
        "excerpt": f"{R['coverage']['n']:,} buildings with an architectural style in Wikidata, sorted into {R['families']['n_fam']} families and mapped through time. Romanesque gives way to Gothic, Baroque and the revivals, Gothic Revival sails to Toronto and Melbourne, and the gaps show who keeps the records.",
        "seo_description": "A world map of architectural styles through time: 180,451 buildings from Wikidata, from Romanesque and Gothic to Art Deco and Brutalist.",
        "tags": ["architecture", "architectural styles", "Gothic Revival", "history", "maps", "data visualisation", "Wikidata"],
        "header_alt": f"Title card reading 'Styles in stone' in black and slate blue on pale stone, beside a world map dotted with {R['coverage']['n']:,} buildings coloured by architectural style, dense across Europe and the eastern United States, with Persian blue in Iran and Japanese purple in Japan."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)


def link(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    os.link(src, dst)


link(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__" or fn in ("points.json", "names.json"):   # page-only files, rebuilt by the code
                continue
            z.write(os.path.join(ROOT, d, fn), f"{SLUG}/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\emph{", "").replace("}", "").replace("\\&", "&")
zmeta = {"title": "Styles in Stone: The World's Architectural Styles in Wikidata, Mapped Through Time",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: {PAGE}. Data and code: {REPO}. Blog post: {{https://blog.tristanhotham.com/2026/10/31/architecture-styles/}}.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["architecture", "architectural styles", "Gothic Revival", "Neoclassical architecture", "historical geography", "Wikidata", "open data", "maps"],
         "license": "cc-by-4.0",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
print("blog words", words, "; zenodo files", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
