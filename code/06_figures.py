"""Static figures: header.png (1200 x 630), blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png).
All numbers come from data/results.json or the same buildings used to make it."""
from collections import Counter, defaultdict
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgb
from figstyle import *

R = jload(f"{DATA}/results.json")
items = load_items()
BL = os.path.join(ROOT, "release", "blog"); PP = os.path.join(ROOT, "release", "paper")
for d in (BL, PP):
    os.makedirs(d, exist_ok=True)
ORDER = draw_order(items)
lon = np.array([x["lon"] for x in items]); lat = np.array([x["lat"] for x in items])
EX, EY = EE.transform(lon, lat)
FAMA = np.array([x["f"] for x in items])
fmt = lambda v: f"{round(v):,}"


def both(fig, name):
    fig.savefig(f"{BL}/b_{name}.png", dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(f"{PP}/f_{name}.png", dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


def world_dots(ax, s=.55, alpha=.85, ext=WORLD_EXT):
    draw_land(ax, WORLD_EE, fc=LAND, ec=BG, lw=.25)
    for k in ORDER:
        m = FAMA == k
        if m.any():
            ax.scatter(EX[m], EY[m], s=s, c=FC[k], lw=0, alpha=alpha, rasterized=True, zorder=3)
    frame(ax, ext)


def fam_legend(fig, keys, x, y, ncol, size=10.5, counts=None, spacing=1.2):
    prop = SERP.copy(); prop.set_size(size)
    h = [Patch(fc=FC[k], ec="none", label=FN[k] + (f"  {fmt(counts[k])}" if counts else "")) for k in keys]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(x, y), ncol=ncol, frameon=False, prop=prop, handlelength=1.0,
               columnspacing=spacing, labelspacing=.45, handletextpad=.5)


# ---------------- header ----------------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([.33, .04, .68, .92]); world_dots(ax, s=.35, ext=(-11.5e6, 15.2e6, -5.6e6, 8.4e6))
fig.text(.04, .84, "Styles", fontproperties=DISP, fontsize=64, color=FG, va="top")
fig.text(.04, .69, "in stone", fontproperties=DISP, fontsize=64, color=COOL, va="top")
fig.text(.04, .50, f"{fmt(R['coverage']['n'])} buildings with an\narchitectural style in Wikidata,\nin {R['families']['n_fam']} families, mapped\ncentury by century.",
         fontproperties=SERP, fontsize=16.5, color=FG, va="top", linespacing=1.5)
for i, k in enumerate(["romanesque", "gothic", "baroque", "neoclassical", "modern", "nouveau"]):
    xx, yy = .04 + (i % 3) * .125, .19 - (i // 3) * .045
    fig.add_artist(Line2D([xx + .005], [yy], marker="o", ms=7, color=FC[k], transform=fig.transFigure))
    fig.text(xx + .015, yy, {"neoclassical": "neoclassical", "modern": "modernist", "nouveau": "art nouveau"}.get(k, k), family=MONO, fontsize=11, color=FC[k] if k != "modern" else FG, va="center")
fig.text(.04, .035, "maps.tristanhotham.com/architecture-styles", family=MONO, fontsize=12, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
plt.close(fig)

# ---------------- world map ----------------
fc = Counter(FAMA)
fig = plt.figure(figsize=(12, 7.6), facecolor=BG)
ax = fig.add_axes([0, .2, 1, .8]); world_dots(ax, s=.5)
fam_legend(fig, [k for k in FKEYS if fc[k]], .03, .2, 5, size=10)
both(fig, "world_map")

# ---------------- Europe by century: dominant family per 1 degree square ----------------
CEN = [1100, 1300, 1500, 1700, 1800, 1900]
cells = {c: defaultdict(Counter) for c in CEN}
for x in items:
    if x["cent"] in cells and x["f"] != "other":
        cells[x["cent"]][(int(np.floor(x["lon"])), int(np.floor(x["lat"])))][x["f"]] += 1
used = Counter()
fig = plt.figure(figsize=(12, 9.6), facecolor=BG)
for j, c in enumerate(CEN):
    ax = fig.add_axes([.005 + (j % 3) * .333, .53 - (j // 3) * .4, .325, .4])
    draw_land(ax, EUR, fc=LAND, ec=BG, lw=.3)
    for (gx, gy), cnt in cells[c].items():
        if not (EUROPE[0] <= gx < EUROPE[2] and EUROPE[1] <= gy < EUROPE[3]):
            continue
        k, v = cnt.most_common(1)[0]; tot = sum(cnt.values()); used[k] += 1
        xs, ys = LAEA.transform([gx, gx + 1, gx + 1, gx], [gy, gy, gy + 1, gy + 1])
        ax.add_patch(MPoly(np.column_stack([xs, ys]), closed=True, fc=FC[k], ec="none", alpha=min(1, .35 + .65 * np.log10(tot + 1) / 1.8), zorder=3))
    frame(ax, EUR_EXT)
    n = sum(sum(v.values()) for v in cells[c].values())
    ax.text(.03, .97, f"{c}s", transform=ax.transAxes, fontproperties=DISP, fontsize=22, color=FG, va="top")
    ax.text(.03, .86, f"{fmt(n)} buildings", transform=ax.transAxes, family=MONO, fontsize=10, color=MUT, va="top")
fam_legend(fig, [k for k in FKEYS if used[k] >= 3], .03, .125, 5, size=10)
both(fig, "europe_centuries")

# ---------------- centuries stacked ----------------
TL = [t for t in R["time"]["timeline"] if t["c"] >= 800]
fig, ax = plt.subplots(figsize=(11, 6.2), facecolor=BG); ax.set_facecolor(BG)
x = np.arange(len(TL)); bottom = np.zeros(len(TL)); seen = set()
for k in FKEYS:
    v = np.array([100 * t["counts"].get(k, 0) / t["n"] for t in TL])
    if v.max() > 0:
        ax.bar(x, v, bottom=bottom, color=FC[k], width=.86, label=FN[k]); bottom += v
        if v.max() >= 4: seen.add(k)
ax.set_xticks(x, [f"{t['c']}s\n{fmt(t['n'])}" for t in TL], fontsize=9.5)
ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.set_ylim(0, 100); ax.set_xlim(-.6, len(TL) - .4)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.tick_params(length=0)
prop = SERP.copy(); prop.set_size(10)
ax.legend(handles=[Patch(fc=FC[k], label=FN[k]) for k in FKEYS if k in seen], loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False, prop=prop, handlelength=1, labelspacing=.4)
fig.subplots_adjust(left=.06, right=.76, bottom=.14, top=.97)
both(fig, "centuries")

# ---------------- Gothic Revival: map coloured by year ----------------
gr = [x for x in items if x["f"] == "gothic" and x["r"]]
dated = [x for x in gr if x["y"] is not None and x["y"] % 100 and x["ye"] >= 1740]
und = [x for x in gr if x not in dated]
fig = plt.figure(figsize=(12, 6.9), facecolor=BG)
ax = fig.add_axes([0, .17, 1, .83]); draw_land(ax, WORLD_EE, fc=LAND, ec=BG, lw=.25)
ux, uy = EE.transform([x["lon"] for x in und], [x["lat"] for x in und])
ax.scatter(ux, uy, s=1.2, c="#B9B1A3", lw=0, rasterized=True, zorder=2)
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
cmap = LinearSegmentedColormap.from_list("rev", ["#E2B007", "#D9733B", "#A3214A", "#5B2A86", "#283B7A"])
ds = sorted(dated, key=lambda x: -x["ye"])
dx, dy = EE.transform([x["lon"] for x in ds], [x["lat"] for x in ds])
sc = ax.scatter(dx, dy, s=3.2, c=[min(1930, max(1790, x["ye"])) for x in ds], cmap=cmap, vmin=1790, vmax=1930, lw=0, rasterized=True, zorder=3)
frame(ax, (-12.0e6, 15.6e6, -5.4e6, 8.3e6))
cax = fig.add_axes([.05, .07, .3, .025]); cb = fig.colorbar(sc, cax=cax, orientation="horizontal"); cb.outline.set_visible(False)
cb.set_ticks([1800, 1840, 1880, 1920]); cax.tick_params(labelsize=10, length=0)
fig.text(.05, .115, "Year a Gothic Revival building was begun", family=MONO, fontsize=10.5, color=FG)
fig.add_artist(Line2D([.405], [.083], marker="o", ms=5, color="#B9B1A3", transform=fig.transFigure))
fig.text(.415, .083, "dated only to a century, or undated", family=MONO, fontsize=10, color="#8F877A", va="center")
both(fig, "gothic_revival")

# ---------------- capitals ----------------
cp = R["capitals"]["top"][:12][::-1]
fig, ax = plt.subplots(figsize=(10, 5.8), facecolor=BG); ax.set_facecolor(BG)
ax.barh(range(len(cp)), [c["neo_pct"] for c in cp], color=FC["neoclassical"], height=.68)
for i, c in enumerate(cp):
    ax.text(c["neo_pct"] + .5, i, f"{rnd(c['neo_pct'])}%  ({c['neo']} of {c['n']:,})", va="center", fontsize=10.5, color=FG)
ax.set_yticks(range(len(cp)), [c["name"].replace("København", "Copenhagen") for c in cp], fontsize=11)
ax.set_xlim(0, 45); ax.set_xticks([])
for s in ("top", "right", "bottom", "left"): ax.spines[s].set_visible(False)
ax.tick_params(length=0)
fig.subplots_adjust(left=.2, right=.97, top=.97, bottom=.04)
both(fig, "capitals")

# ---------------- coverage ----------------
top = R["coverage"]["top"][:12][::-1]; cont = R["coverage"]["continents"][::-1]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6), facecolor=BG, gridspec_kw={"width_ratios": [1.25, 1]})
for a in (a1, a2):
    a.set_facecolor(BG)
    for s in ("top", "right", "bottom", "left"): a.spines[s].set_visible(False)
    a.tick_params(length=0); a.set_xticks([])
nm = lambda s: s.replace("United States of America", "United States").replace("Czech Republic", "Czechia")
a1.barh(range(len(top)), [c["pct"] for c in top], color="#5A6170", height=.7)
for i, c in enumerate(top):
    a1.text(c["pct"] + .3, i, f"{c['pct']:.1f}%", va="center", fontsize=10.5)
a1.set_yticks(range(len(top)), [nm(c["name"]) for c in top], fontsize=11); a1.set_xlim(0, 27)
a1.set_title("By country (top 12)", loc="left", fontproperties=SERB, fontsize=13)
a2.barh(range(len(cont)), [c["pct"] for c in cont], color="#8C8170", height=.6)
for i, c in enumerate(cont):
    a2.text(c["pct"] + 1, i, f"{c['pct']:.1f}%  ({c['n']:,})", va="center", fontsize=10.5)
a2.set_yticks(range(len(cont)), [c["name"] for c in cont], fontsize=11); a2.set_xlim(0, 100)
a2.set_title("By continent", loc="left", fontproperties=SERB, fontsize=13)
fig.subplots_adjust(left=.13, right=.98, wspace=.55, top=.92, bottom=.04)
both(fig, "coverage")

# ---------------- families (paper only) ----------------
fl = sorted(R["families"]["list"], key=lambda r: r["n"])
fig, ax = plt.subplots(figsize=(10, 8), facecolor=BG); ax.set_facecolor(BG)
for i, r in enumerate(fl):
    ax.barh(i, r["n"] - r["rev"], color=FC[r["k"]], height=.72)
    if r["rev"]:
        ax.barh(i, r["rev"], left=r["n"] - r["rev"], color=FC[r["k"]], alpha=.45, height=.72, hatch="////", edgecolor=BG, lw=0)
    ax.text(r["n"] + 250, i, f"{r['n']:,}", va="center", fontsize=10)
ax.set_yticks(range(len(fl)), [r["name"] for r in fl], fontsize=10.5)
ax.set_xlim(0, 30500); ax.set_xticks([])
for s in ("top", "right", "bottom", "left"): ax.spines[s].set_visible(False)
ax.tick_params(length=0)
fig.subplots_adjust(left=.27, right=.97, top=.98, bottom=.03)
fig.savefig(f"{PP}/f_families.png", dpi=200, facecolor=BG); plt.close(fig)
print("figures done")
