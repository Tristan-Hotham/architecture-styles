"""House style for static figures: fonts (static instances cut from the variable Fraunces in /home/claude/ref/fonts,
written to WORK), the stone palette, family colours, and Natural Earth outlines in Equal Earth (world) and
LAEA Europe (EPSG:3035) projections."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from common import *
from families import FAMILIES, FKEYS

FONTS = os.environ.get("ARCH_FONTS", "/home/claude/ref/fonts")
FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#646A72", "axes.labelcolor": "#1F2329",
                     "xtick.color": "#646A72", "ytick.color": "#646A72"})
BG, FG, MUT, LAND, RULE, COOL, HOT = "#F6F3EC", "#1F2329", "#646A72", "#E6E0D2", "#DED7C9", "#283B7A", "#A3214A"
FC = {k: c for k, n, c, d in FAMILIES}
FN = {k: n for k, n, c, d in FAMILIES}
EE = Transformer.from_crs(4326, 8857, always_xy=True)
LAEA = Transformer.from_crs(4326, 3035, always_xy=True)
W = jload(f"{DATA}/world.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


def shapes(tr, clip=None):
    out = []
    for f in W["features"]:
        for ring in rings(f["geometry"]):
            if clip is not None:
                lo, la = ring[:, 0], ring[:, 1]
                if lo.max() < clip[0] or lo.min() > clip[2] or la.max() < clip[1] or la.min() > clip[3]:
                    continue
            x, y = tr.transform(np.clip(ring[:, 0], -179.9, 179.9), ring[:, 1])
            out.append((f["properties"]["iso"], np.column_stack([x, y])))
    return out


WORLD_EE = shapes(EE)
EUROPE = (-25, 33, 50, 72)
EUR = shapes(LAEA, clip=EUROPE)
WORLD_EXT = (-12.0e6, 15.6e6, -6.0e6, 8.5e6)
EUR_EXT = (2.45e6, 6.55e6, 1.35e6, 5.45e6)


def draw_land(ax, shp, fc=LAND, ec="#FFFFFF", lw=.3, z=1):
    for iso, p in shp:
        ax.add_patch(MPoly(p, closed=True, fc=fc, ec=ec, lw=lw, zorder=z))


def frame(ax, ext):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.axis("off")


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)


def load_items():
    """Buildings with family, revival flag, year read for the time views (None if undated or earlier than its style)."""
    it = jload(f"{WORK}/items_f.json")
    return it


def draw_order(items):
    from collections import Counter
    c = Counter(x["f"] for x in items)
    return sorted(FKEYS, key=lambda k: -c[k])
