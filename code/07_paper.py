"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/Hotham_Styles_in_Stone.pdf and .tex (figures f_*.png sit beside them)."""
import re, subprocess
from common import *
from families import FAMILIES

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Styles_in_Stone"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
KEEP = {"DOI"}
t = R["time"]["dom"]
assert all(t[str(c)] == "romanesque" for c in (800, 900, 1000, 1100)) and all(t[str(c)] == "japanese" for c in (300, 400, 500, 600, 700))
assert [c["name"] for c in R["capitals"]["top"][1:5]] == ["Dublin", "Minsk", "Santiago", "Washington, D.C."]
assert R["regions"]["bel"]["f"] == "deco" and R["regions"]["esp"]["f"] == "vernacular"
assert [r["k"] for r in sorted(R["families"]["list"], key=lambda r: -r["n"])[:5]] == ["neoclassical", "gothic", "vernacular", "historicist", "baroque"]


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{rnd(v):,}"
    if f == "pc": return f"{rnd(v)}\\%"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


cv, fa = R["coverage"], R["families"]
TS = ("\\begin{table}[tbp]\\centering\\small\\caption{Sources, what was kept and licences.}\\label{tab:sources}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.0cm}>{\\raggedright\\arraybackslash}p{7.2cm}r>{\\raggedright\\arraybackslash}p{2.2cm}}\\toprule Source & Kept & Records & Licence\\\\\\midrule\n"
      f"Wikidata & Items with an architectural style (P149) and coordinates & {cv['n']:,} & CC0\\\\\n"
      f"Wikidata & Style statements on those items & {fa['n_pairs']:,} & CC0\\\\\n"
      f"Wikidata & Styles in use, with parents and part-of links & {fa['n_styles']:,} & CC0\\\\\n"
      f"Wikidata & Items with an inception date & {R['dates']['n']:,} & CC0\\\\\n"
      f"Natural Earth & Countries (1:50m) and populated places & 240 / 2,517 & Public domain\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
FD = {k: d for k, n, c, d in FAMILIES}
rows = ""
for r in R["families"]["list"]:
    med = "" if r["median"] is None else (f"{-r['median']} BCE" if r["median"] < 0 else str(r["median"]))
    rows += f"{tex(r['name'])} & {tex(FD[r['k']])} & {r['n']:,} & {r['rev']:,} & {r['styles']} & {med}\\\\\n"
TF = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The style families: buildings, revival buildings, number of Wikidata styles and median year of dated buildings (round-century years read as mid-century; dates earlier than the style left out).}\\label{tab:fam}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.2cm}>{\\raggedright\\arraybackslash}p{6.4cm}rrrr}\\toprule Family & Includes & Buildings & Revival & Styles & Median\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for r in sorted(R["revivals"]["gothic"]["table"], key=lambda r: r["p10"]):
    rows += f"{tex(r['name'].replace('United States of America', 'United States'))} & {tex(r['cont'])} & {r['n']:,} & {r['p10']} & {r['median']}\\\\\n"
TG = ("\\begin{table}[tbp]\\centering\\small\\caption{Gothic Revival buildings dated to a year from 1740 on, by country (at least 15): year by which the first tenth were begun, and median year.}\\label{tab:gr}"
      "\\begin{tabular}{llrrr}\\toprule Country & Continent & Buildings & First tenth & Median\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(m.group(1)), m.group(3) or "raw"), t)
t = t.replace("{{TABLE_SOURCES}}", TS).replace("{{TABLE_FAMILIES}}", TF).replace("{{TABLE_GR}}", TG)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP
assert "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
