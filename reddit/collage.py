"""r/dataisbeautiful collage for architecture-styles: 2400 x 3000 px, light background.
Numbers from data/results.json and the same buildings (WORK/items_f.json)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from collections import Counter, defaultdict
from matplotlib.patches import Patch
from figstyle import *

R = jload(f"{DATA}/results.json")
items = load_items()
PAPER = "#F7F4EE"; LANDC = "#E4DED1"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=PAPER)
fig.text(.045, .975, "Styles in stone", fontproperties=DISP, fontsize=60, color=FG, va="top")
fig.text(.045, .912, "The most common architectural style in each part of Europe, century by century.\n"
         f"Each square is one degree; {R['dates']['time_n']:,} dated buildings from Wikidata, styles grouped into {R['families']['n_fam']} families.",
         fontproperties=SERP, fontsize=16, color=FG, va="top", linespacing=1.45)

CEN = [1100, 1300, 1500, 1700, 1800, 1900]
cells = {c: defaultdict(Counter) for c in CEN}
for x in items:
    if x["cent"] in cells and x["f"] != "other":
        cells[x["cent"]][(int(np.floor(x["lon"])), int(np.floor(x["lat"])))][x["f"]] += 1
used = Counter()
for j, c in enumerate(CEN):
    ax = fig.add_axes([.012 + (j % 3) * .327, .585 - (j // 3) * .27, .32, .27])
    draw_land(ax, EUR, fc=LANDC, ec=PAPER, lw=.3)
    for (gx, gy), cnt in cells[c].items():
        if not (EUROPE[0] <= gx < EUROPE[2] and EUROPE[1] <= gy < EUROPE[3]):
            continue
        k, v = cnt.most_common(1)[0]; tot = sum(cnt.values()); used[k] += 1
        xs, ys = LAEA.transform([gx, gx + 1, gx + 1, gx], [gy, gy, gy + 1, gy + 1])
        ax.add_patch(MPoly(np.column_stack([xs, ys]), closed=True, fc=FC[k], ec="none", alpha=min(1, .35 + .65 * np.log10(tot + 1) / 1.8), zorder=3))
    frame(ax, (2.45e6, 6.55e6, 1.35e6, 5.45e6))
    lead = R["time"]["dom"][str(c)]
    sh = next(t for t in R["time"]["timeline"] if t["c"] == c)
    pct = rnd(100 * sh["counts"][lead] / sh["n"])
    ax.text(.035, .965, f"{c}s", transform=ax.transAxes, fontproperties=DISP, fontsize=26, color=FG, va="top")
    ax.text(.035, .845, f"{FN[lead]}\n{pct}% of {sh['n']:,}", transform=ax.transAxes, family=MONO, fontsize=10.5, color=FC[lead] if lead != "modern" else FG, va="top", linespacing=1.4)

# legend with full names, on plain paper
prop = SERP.copy(); prop.set_size(12.5)
keys = [k for k in FKEYS if used[k] >= 3]
fig.legend(handles=[Patch(fc=FC[k], ec="none", label=FN[k]) for k in keys], loc="upper left", bbox_to_anchor=(.04, .318), ncol=4, frameon=False,
           prop=prop, handlelength=1.1, columnspacing=1.4, labelspacing=.55)

# big numbers
g = R["revivals"]["gothic"]
nums = [(f"{rnd(R['time']['s1300_gothic'])}%", FC["gothic"], "of dated buildings\nfrom the 1300s are\nGothic"),
        (f"{rnd(R['time']['s1800_revival'])}%", FC["baroque"], "of those from the\n1800s are revivals of\nolder styles"),
        (f"{g['n']:,}", FC["renaissance"], f"Gothic Revival buildings\nin {g['n_countries']} countries, {g['usa']:,}\nin the United States"),
        (f"{R['coverage']['africa_pct']:.1f}%", "#5A6170", f"of all {R['coverage']['n']:,}\nare in Africa: a map\nof who keeps records")]
for i, (big, col, small) in enumerate(nums):
    x = .045 + i * .235
    fig.text(x, .188, big, fontproperties=DISP, fontsize=42, color=col, va="top")
    fig.text(x, .138, small, family=MONO, fontsize=11, color=FG, va="top", linespacing=1.35)

fig.text(.045, .018, f"Source: Wikidata (CC0) via QLever, retrieved in {RETRIEVED}: items with an architectural style (P149), coordinates and inception (P571).\n"
         "Natural Earth outlines. Round-century dates read as mid-century; buildings dated before their style began left out.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib  ·  maps.tristanhotham.com/architecture-styles", family=MONO, fontsize=9.5, color=MUT, linespacing=1.55, va="bottom")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles_in_stone.png")
fig.savefig(out, facecolor=PAPER, dpi=200)
print("ok", out)
