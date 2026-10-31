"""All analysis: primary family per building, coverage, families, time, revivals, capitals, best-documented buildings.
Writes data/results.json (every number quoted anywhere), data/buildings.csv.gz, data/family_century.csv,
data/revival_countries.csv and the page data (data/site.json, data/points.json, data/names.json)."""
import csv, math, statistics as stt
from collections import Counter, defaultdict
from common import *
from families import FAMILIES, FKEYS

items = jload(f"{WORK}/items.json"); SF = jload(f"{WORK}/stylefam.json"); fam, use = SF["fam"], SF["use"]
S = jload(f"{WORK}/styles.json"); ST, TL = S["styles"], S["typelabels"]
CM = jload(f"{WORK}/countries.json")
FN = {k: n for k, n, *_ in FAMILIES}
cname = lambda iso: (CM.get(iso) or {}).get("name", iso or "")
N = len(items)
R = {"meta": {"retrieved": RETRIEVED, "page": PAGE, "repo": REPO, "doi": DOI, "slug": SLUG}}

# earliest plausible year for each family (and revival); a building whose inception is more than 25 years earlier
# than its style began most likely carries the founding date of an older building on the site, so it is left out of
# the time views (but kept everywhere else)
START = {("gothic", True): 1740, ("romanesque", True): 1820, ("renaissance", True): 1820, ("baroque", True): 1840,
         ("neoclassical", False): 1600, ("neoclassical", True): 1780, ("historicist", False): 1780, ("historicist", True): 1780,
         ("colonial", True): 1870, ("crafts", False): 1850, ("nouveau", False): 1880, ("deco", False): 1910, ("modern", False): 1880,
         ("brutalist", False): 1945, ("postmodern", False): 1960, ("byzantine", True): 1820, ("islamic", True): 1800,
         ("mughal", True): 1850, ("precolumbian", True): 1900, ("ottoman", False): 1300, ("mughal", False): 1190,
         ("baroque", False): 1560, ("renaissance", False): 1400, ("gothic", False): 1120, ("colonial", False): 1490}
MARGIN = 25


def prim(it):
    c = [(use[s], s) for s in it["s"] if fam[s]["f"] != "other"]
    if not c:
        s = min((use[s], s) for s in it["s"])[1]
        return "other", False, s
    s = min(c)[1]
    return fam[s]["f"], fam[s]["r"], s


future = 0
for it in items:
    it["f"], it["r"], it["ps"] = prim(it)
    it["fams"] = sorted({fam[s]["f"] for s in it["s"]} - ({"other"} if it["f"] != "other" else set()), key=FKEYS.index)
    if it["y"] is not None and it["y"] > 2026:
        it["y"] = None; future += 1
    # a year ending in 00 is very often a century-precision date, which Wikidata stores as the century's last year
    # ('20th century' is 2000), so it is read as the middle of the century that ends that year
    it["ye"] = None if it["y"] is None else (it["y"] - 50 if it["y"] % 100 == 0 else it["y"])
    st = START.get((it["f"], it["r"]))
    it["anach"] = bool(it["ye"] is not None and st is not None and it["ye"] < st - MARGIN)
    it["cent"] = None if it["ye"] is None or it["anach"] else (it["ye"] // 100) * 100

dated = [it for it in items if it["y"] is not None]
nd = len(dated)

# ---------------- coverage ----------------
ic = Counter(it["iso"] for it in items)
cc = Counter(it["cont"] for it in items)
top_c = [{"iso": k, "name": cname(k), "n": v, "pct": round(100 * v / N, 1)} for k, v in ic.most_common(20)]
conts = [{"name": k, "n": v, "pct": round(100 * v / N, 1)} for k, v in cc.most_common() if k in ("Europe", "North America", "Asia", "South America", "Africa", "Oceania")]
ESPT = Counter(TL.get(it["t"][0], "") for it in items if it["iso"] == "ESP" and it["t"])
SVK_lab = sum(1 for it in items if it["iso"] == "SVK" and it["n"]) / max(1, ic["SVK"])
first_type = Counter(TL.get(it["t"][0], "") for it in items if it["t"])
pop = {k: v["pop"] for k, v in CM.items()}
per_m = sorted([(k, v / pop[k] * 1e6) for k, v in ic.items() if k in pop and pop[k] > 2e6], key=lambda x: -x[1])
R["coverage"] = {
    "n": N, "n_countries": len([k for k in ic if k]), "top": top_c, "continents": conts,
    "europe_pct": round(100 * cc["Europe"] / N, 1), "namerica_pct": round(100 * cc["North America"] / N, 1),
    "asia_pct": round(100 * cc["Asia"] / N, 1), "africa_pct": round(100 * cc["Africa"] / N, 1), "africa_n": cc["Africa"],
    "samerica_pct": round(100 * cc["South America"] / N, 1), "oceania_pct": round(100 * cc["Oceania"] / N, 1),
    "usa_esp_pct": round(100 * (ic["USA"] + ic["ESP"]) / N, 1), "top5_pct": round(100 * sum(v for _, v in ic.most_common(5)) / N, 1),
    "deu_fra_gbr_pct": round(100 * (ic["DEU"] + ic["FRA"] + ic["GBR"]) / N, 1),
    "chn_n": ic["CHN"], "ind_n": ic["IND"], "nga_n": ic["NGA"], "egy_n": ic["EGY"], "jpn_n": ic["JPN"], "irn_n": ic["IRN"], "bra_n": ic["BRA"], "mex_n": ic["MEX"],
    "esp_masia": ESPT["masia"], "esp_silo": ESPT["silo"], "svk_label_pct": round(100 * SVK_lab), "per_million_top": [{"iso": k, "name": cname(k), "v": round(v)} for k, v in per_m[:8]],
    "dated_n": nd, "dated_pct": round(100 * nd / N, 1), "label_pct": round(100 * sum(1 for it in items if it["n"]) / N, 1),
    "no_label_n": sum(1 for it in items if not it["n"]),
    "sl0_n": sum(1 for it in items if it["sl"] == 0), "sl0_pct": round(100 * sum(1 for it in items if it["sl"] == 0) / N, 1),
    "church_n": first_type["church building"], "house_n": first_type["house"],
}

# ---------------- families ----------------
fc = Counter(it["f"] for it in items)
famrows = []
for k in FKEYS:
    xs = [it for it in items if it["f"] == k]
    ys = [it["ye"] for it in xs if it["ye"] is not None and not it["anach"]]
    famrows.append({"k": k, "name": FN[k], "n": len(xs), "pct": round(100 * len(xs) / N, 1), "rev": sum(1 for it in xs if it["r"]),
                    "dated": len(ys), "median": int(stt.median(ys)) if ys else None,
                    "styles": sum(1 for q in use if fam[q]["f"] == k),
                    "top_iso": [{"iso": i, "name": cname(i), "n": n} for i, n in Counter(it["iso"] for it in xs).most_common(3)]})
fr = {r["k"]: r for r in famrows}
rank = sorted([r for r in famrows if r["k"] != "other"], key=lambda r: -r["n"])
nrev = sum(1 for it in items if it["r"])
R["families"] = {"list": famrows, "by": {r["k"]: r["n"] for r in famrows}, "rank": [r["k"] for r in rank], "n_fam": len(FKEYS) - 1,
                 "n_styles": len(use), "n_pairs": sum(len(it["s"]) for it in items), "multi_fam": sum(1 for it in items if len(it["fams"]) > 1),
                 "revival_n": nrev, "revival_pct": round(100 * nrev / N, 1),
                 "how_styles": SF["how_styles"], "how_pairs": SF["how_pairs"],
                 "hand_pairs_pct": round(100 * SF["how_pairs"]["hand"] / sum(SF["how_pairs"].values()), 1),
                 "other_pct": fr["other"]["pct"], "non_euro_fams": sum(fr[k]["n"] for k in ("islamic", "persian", "ottoman", "mughal", "hindu", "chinese", "japanese", "seasian", "precolumbian")),
                 "top_styles": [{"q": q, "label": ST.get(q, {}).get("label", ""), "n": n, "f": fam[q]["f"]} for q, n in sorted(use.items(), key=lambda x: -x[1])[:12]]}
R["families"]["non_euro_pct"] = round(100 * R["families"]["non_euro_fams"] / N, 1)

# ---------------- dates ----------------
yrs = [it["y"] for it in dated]
R["dates"] = {"n": nd, "pct": round(100 * nd / N, 1), "round100_pct": round(100 * sum(1 for y in yrs if y % 100 == 0) / nd, 1),
              "round10_pct": round(100 * sum(1 for y in yrs if y % 10 == 0) / nd, 1), "bce": sum(1 for y in yrs if y < 0), "future_dropped": future,
              "anach_n": sum(1 for it in items if it["anach"]), "anach_pct_dated": round(100 * sum(1 for it in items if it["anach"]) / nd, 1),
              "time_n": sum(1 for it in items if it["cent"] is not None), "earliest": min(yrs),
              "y1900": Counter(yrs)[1900], "y1899": Counter(yrs)[1899], "y1901": Counter(yrs)[1901],
              "y1500": Counter(yrs)[1500], "y1501": Counter(yrs)[1501], "y1499": Counter(yrs)[1499], "y2000": Counter(yrs)[2000], "y1999": Counter(yrs)[1999], "y2001": Counter(yrs)[2001],
              "after1800_pct": round(100 * sum(1 for y in yrs if y >= 1800) / nd, 1), "after1900_pct": round(100 * sum(1 for y in yrs if y >= 1900) / nd, 1)}
ga = sum(1 for it in items if it["anach"] and it["f"] == "gothic" and it["r"])
R["dates"]["anach_gothic_rev"] = ga

# ---------------- time: family by century ----------------
CENTS = list(range(-500, 2001, 100))
def cbin(c):
    return max(-500, c)
fcent = defaultdict(Counter)
for it in items:
    if it["cent"] is not None:
        fcent[cbin(it["cent"])][it["f"]] += 1
# sensitivity: read round-century years as written instead (1800 in the 1800s)
fcent2 = defaultdict(Counter)
for it in items:
    if it["cent"] is not None:
        fcent2[cbin((it["y"] // 100) * 100)][it["f"]] += 1
timeline, maxdiff, domchg = [], 0, 0
for c in CENTS:
    tot = sum(fcent[c].values()); tot2 = sum(fcent2[c].values())
    dom = [k for k, _ in fcent[c].most_common() if k != "other"][:1]
    dom2 = [k for k, _ in fcent2[c].most_common() if k != "other"][:1]
    if tot >= 50 and dom != dom2:
        domchg += 1
    if tot >= 200 and tot2 >= 200:
        for k in FKEYS:
            maxdiff = max(maxdiff, abs(100 * fcent[c][k] / tot - 100 * fcent2[c][k] / tot2))
    timeline.append({"c": c, "label": century_label(c) if c > -500 else "before 400 BCE", "n": tot, "counts": {k: fcent[c][k] for k in FKEYS if fcent[c][k]},
                     "dom": dom[0] if dom else None})
with open(f"{DATA}/family_century.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["century_start", "century", "buildings"] + FKEYS)
    for t in timeline:
        w.writerow([t["c"], t["label"], t["n"]] + [t["counts"].get(k, 0) for k in FKEYS])
tl = {t["c"]: t for t in timeline}
share = lambda c, k: round(100 * tl[c]["counts"].get(k, 0) / tl[c]["n"], 1) if tl[c]["n"] else 0
R["time"] = {"timeline": timeline, "sens_maxdiff": round(maxdiff, 1), "sens_domchange": domchg,
             "peak": max(timeline, key=lambda t: t["n"])["c"], "n1800": tl[1800]["n"], "n1900": tl[1900]["n"],
             "dom": {str(t["c"]): t["dom"] for t in timeline},
             "s1100_romanesque": share(1100, "romanesque"), "s1300_gothic": share(1300, "gothic"), "s1500_renaissance": share(1500, "renaissance"),
             "s1700_baroque": share(1700, "baroque"), "s1800_neoclassical": share(1800, "neoclassical"),
             "s1900_modern": share(1900, "modern"), "s1900_deco": share(1900, "deco"), "s1900_nouveau": share(1900, "nouveau"),
             "s1800_gothic": share(1800, "gothic"), "s1800_revival": round(100 * sum(1 for it in items if it["cent"] == 1800 and it["r"]) / tl[1800]["n"], 1),
             "s1900_revival": round(100 * sum(1 for it in items if it["cent"] == 1900 and it["r"]) / tl[1900]["n"], 1),
             "s2000_postmodern": share(2000, "postmodern"), "s2000_modern": share(2000, "modern")}

# ---------------- revivals ----------------
def revival_table(sel, y0, minn=15):
    by = defaultdict(list)
    for it in items:
        if sel(it) and it["ye"] is not None and it["y"] % 100 and it["ye"] >= y0 and it["iso"]:   # precise years only
            by[it["iso"]].append(it["ye"])
    rows = []
    for iso, v in by.items():
        if len(v) >= minn:
            v = sorted(v)
            rows.append({"iso": iso, "name": cname(iso), "cont": CM.get(iso, {}).get("cont"), "n": len(v), "p10": v[len(v) // 10], "median": int(stt.median(v))})
    return sorted(rows, key=lambda r: (r["p10"], r["median"]))


isGR = lambda it: it["f"] == "gothic" and it["r"]
GR = [it for it in items if isGR(it)]
gr_tab = revival_table(isGR, 1740)
EMPIRE = ["GBR", "IRL", "CAN", "AUS", "NZL", "ZAF", "IND", "LKA", "JAM", "BRB", "MLT", "SGP", "MYS", "HKG", "BMU", "TTO", "GUY", "KEN", "NGA", "GHA", "PAK", "BGD", "MMR"]
grc = Counter(it["iso"] for it in GR)
gr_cont = Counter(it["cont"] for it in GR)
R["revivals"] = {
    "gothic": {"n": len(GR), "n_countries": len(grc), "usa": grc["USA"], "gbr": grc["GBR"], "deu": grc["DEU"], "pol": grc["POL"], "can": grc["CAN"],
               "empire_n": sum(grc[i] for i in EMPIRE), "empire_countries": sum(1 for i in EMPIRE if grc[i]),
               "empire_ex_gbr_n": sum(grc[i] for i in EMPIRE if i != "GBR"),
               "outside_europe": len(GR) - gr_cont["Europe"], "outside_europe_pct": round(100 * (len(GR) - gr_cont["Europe"]) / len(GR), 1),
               "table": gr_tab, "top": [{"iso": k, "name": cname(k), "n": v} for k, v in grc.most_common(10)]},
}
R["revivals"]["gothic"]["fra"] = grc["FRA"]; R["revivals"]["gothic"]["nld"] = grc["NLD"]
grt = {r["iso"]: r for r in gr_tab}
for iso in ("GBR", "USA", "CAN", "AUS", "NZL", "DEU", "FRA", "POL"):
    if iso in grt:
        R["revivals"]["gothic"][iso.lower() + "_med"] = grt[iso]["median"]; R["revivals"]["gothic"][iso.lower() + "_p10"] = grt[iso]["p10"]
# earliest decade per continent (5th percentile of revival-era dates)
for k, sel, y0 in (("gothic", isGR, 1740), ("greek", lambda it: any(s == "Q1513688" for s in it["s"]), 1780),
                   ("moorish", lambda it: it["f"] == "islamic" and it["r"], 1800), ("colonialrev", lambda it: it["f"] == "colonial" and it["r"], 1870)):
    cyr = defaultdict(list)
    for it in items:
        if sel(it) and it["ye"] is not None and it["y"] % 100 and it["ye"] >= y0:
            cyr[it["cont"]].append(it["ye"])
    R["revivals"].setdefault(k, {})
    R["revivals"][k]["n"] = sum(1 for it in items if sel(it))
    R["revivals"][k]["by_cont"] = {c: {"n": len(v), "median": int(stt.median(v))} for c, v in cyr.items() if c and len(v) >= 10}
    R["revivals"][k]["countries"] = len({it["iso"] for it in items if sel(it)})
    R["revivals"][k]["top"] = [{"iso": i, "name": cname(i), "n": n} for i, n in Counter(it["iso"] for it in items if sel(it)).most_common(6)]
R["revivals"]["greek"]["usa"] = sum(1 for it in items if it["iso"] == "USA" and any(s == "Q1513688" for s in it["s"]))
R["revivals"]["greek"]["usa_pct"] = round(100 * R["revivals"]["greek"]["usa"] / R["revivals"]["greek"]["n"])
R["revivals"]["colonialrev"]["usa_pct"] = round(100 * sum(1 for it in items if it["iso"] == "USA" and it["f"] == "colonial" and it["r"]) / R["revivals"]["colonialrev"]["n"])
rv_fam = Counter(it["f"] for it in items if it["r"])
R["revivals"]["by_family"] = {k: rv_fam[k] for k in FKEYS if rv_fam[k]}
R["revivals"]["by_family_pct"] = {k: round(100 * rv_fam[k] / fr[k]["n"], 1) for k in FKEYS if rv_fam[k]}
with open(f"{DATA}/revival_countries.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["revival", "iso", "country", "continent", "buildings_dated_from_1740", "p10_year", "median_year"])
    for r in gr_tab:
        w.writerow(["Gothic Revival", r["iso"], r["name"], r["cont"], r["n"], r["p10"], r["median"]])

# ---------------- capitals: neoclassical ----------------
cities = jload(f"{DATA}/cities.json")
caps = [c for c in cities if c["cap"]]
def km(a, b, c, d):
    p = math.pi / 180
    x = (c - a) * p * math.cos((b + d) / 2 * p); y = (d - b) * p
    return 6371 * math.hypot(x, y)
grid = defaultdict(list)
for it in items:
    grid[(int(it["lat"] // 1), int(it["lon"] // 1))].append(it)
caprows = []
for c in caps:
    near = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            for it in grid.get((int(c["lat"] // 1) + dy, int(c["lon"] // 1) + dx), []):
                if km(c["lon"], c["lat"], it["lon"], it["lat"]) <= 15:
                    near.append(it)
    if len(near) >= 40:
        nc = sum(1 for it in near if it["f"] == "neoclassical")
        fcn = Counter(it["f"] for it in near)
        caprows.append({"name": c["name"], "iso": c["iso"], "n": len(near), "neo": nc, "neo_pct": round(100 * nc / len(near), 1),
                        "dom": [k for k, _ in fcn.most_common() if k != "other"][0]})
caprows.sort(key=lambda r: -r["neo_pct"])
R["capitals"] = {"radius_km": 15, "min_n": 40, "n_caps": len(caprows), "top": caprows[:12],
                 "neo_dom": [r["name"] for r in caprows if r["dom"] == "neoclassical"], "n_neo_dom": sum(1 for r in caprows if r["dom"] == "neoclassical")}

# ---------------- best documented ----------------
SETTLE = re.compile(r"city|municipal|town|village|commune|settlement|district|human settlement|region|neighbo", re.I)
isbuilding = lambda it: not any(SETTLE.search(TL.get(t, "")) for t in it["t"])
best = {}
for k in FKEYS:
    xs = sorted([it for it in items if it["f"] == k and it["n"] and isbuilding(it)], key=lambda it: (-it["sl"], it["q"]))[:6]
    best[k] = [{"q": it["q"], "name": it["n"], "sl": it["sl"], "iso": it["iso"], "country": cname(it["iso"]), "y": it["y"], "style": ST.get(it["ps"], {}).get("label", "")} for it in xs]
allbest = sorted([it for it in items if isbuilding(it)], key=lambda it: -it["sl"])[:15]
R["best"] = {"by_family": best, "overall": [{"q": it["q"], "name": it["n"], "sl": it["sl"], "f": it["f"], "iso": it["iso"], "country": cname(it["iso"])} for it in allbest],
             "median_sl": stt.median([it["sl"] for it in items])}

# ---------------- regional dominants (for text and figures) ----------------
def dom_in(isos):
    c = Counter(it["f"] for it in items if it["iso"] in isos and it["f"] != "other")
    t = sum(c.values()); k = c.most_common(1)[0]
    return {"f": k[0], "pct": round(100 * k[1] / t, 1), "n": t}
R["regions"] = {iso.lower(): dom_in({iso}) for iso in ("USA", "ESP", "DEU", "ITA", "FRA", "GBR", "SVK", "CZE", "POL", "RUS", "IRN", "TUR", "JPN", "IND", "CHN", "BRA", "MEX", "AUS", "BEL", "NLD", "CAN")}
cd = defaultdict(Counter)
for it in items:
    if it["f"] != "other":
        cd[it["iso"]][it["f"]] += 1
cdom = {iso: c.most_common(1)[0][0] for iso, c in cd.items() if iso and sum(c.values()) >= 20}
R["regions"]["country_dom_counts"] = dict(Counter(cdom.values()).most_common())
R["regions"]["n_countries_20"] = len(cdom)
R["regions"]["neo_dom_countries"] = sorted(cname(i) for i, f in cdom.items() if f == "neoclassical")

# ---------------- headline cards ----------------
R["cards"] = {"gothic_all": fr["gothic"]["n"], "gothic_rev": sum(1 for it in items if it["f"] == "gothic" and it["r"]),
              "gothic_orig": sum(1 for it in items if it["f"] == "gothic" and not it["r"])}
R["cards"]["gothic_rev_pct"] = round(100 * R["cards"]["gothic_rev"] / R["cards"]["gothic_all"])

# ---------------- page data ----------------
fidx = {k: i for i, k in enumerate(FKEYS)}
styles_used = sorted(use, key=lambda q: -use[q]); sidx = {q: i for i, q in enumerate(styles_used)}
tused = Counter(it["t"][0] for it in items if it["t"]); tlist = [t for t, _ in tused.most_common()]; tidx = {t: i for i, t in enumerate(tlist)}
clist = sorted({it["iso"] for it in items if it["iso"]}); ciidx = {c: i for i, c in enumerate(clist)}
order = sorted(range(N), key=lambda i: items[i]["sl"])     # draw best-documented last (on top)
P = {k: [] for k in ("x", "y", "f", "r", "yr", "a", "sl", "q", "c", "s", "t")}
names = []; extra = {}
for j, i in enumerate(order):
    it = items[i]
    P["x"].append(round(it["lon"] * 1e4)); P["y"].append(round(it["lat"] * 1e4)); P["f"].append(fidx[it["f"]]); P["r"].append(1 if it["r"] else 0)
    P["yr"].append(it["y"] if it["y"] is not None else None); P["a"].append(1 if it["anach"] else 0); P["sl"].append(it["sl"])
    P["q"].append(int(it["q"][1:])); P["c"].append(ciidx.get(it["iso"], -1)); P["s"].append(sidx[it["ps"]]); P["t"].append(tidx[it["t"][0]] if it["t"] else -1)
    names.append(it["n"])
    other = [sidx[s] for s in it["s"] if s != it["ps"]]
    if other:
        extra[j] = other
jsave(P, f"{DATA}/points.json")
jsave({"names": names, "extra": extra}, f"{DATA}/names.json")
SITE = {"fams": [[k, n, c, d] for k, n, c, d in FAMILIES], "styles": [[dash(ST.get(q, {}).get("label", "")) or "(no English label)", fidx[fam[q]["f"]], 1 if fam[q]["r"] else 0, q] for q in styles_used],
        "types": [dash(TL.get(t, "")) for t in tlist], "countries": [[c, cname(c)] for c in clist],
        "clab": [[k, v["name"], round(v["lx"], 2), round(v["ly"], 2), v["pop"] or 0] for k, v in CM.items() if v.get("lx") is not None]}
jsave(SITE, f"{DATA}/site.json")

# buildings.csv.gz (all buildings, reusable; gzipped to stay under GitHub's file size limit)
import gzip
with gzip.open(f"{DATA}/buildings.csv.gz", "wt", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["qid", "label", "lon", "lat", "country_iso3", "continent", "inception_year", "round_century", "year_used", "date_before_style", "family", "revival", "primary_style_qid", "primary_style", "all_style_qids", "type", "sitelinks"])
    for it in sorted(items, key=lambda it: int(it["q"][1:])):
        w.writerow([it["q"], dash(it["n"]), it["lon"], it["lat"], it["iso"] or "", it["cont"] or "", "" if it["y"] is None else it["y"], "" if it["y"] is None else int(it["y"] % 100 == 0), "" if it["ye"] is None else it["ye"], int(it["anach"]), it["f"], int(it["r"]),
                    it["ps"], dash(ST.get(it["ps"], {}).get("label", "")), "|".join(it["s"]), dash(TL.get(it["t"][0], "")) if it["t"] else "", it["sl"]])
jsave(items, f"{WORK}/items_f.json")
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("coverage",)}, ensure_ascii=False)[:1500])
print("families", [(r["k"], r["n"], r["median"]) for r in famrows])
print("time sens", R["time"]["sens_maxdiff"], R["time"]["sens_domchange"], "dom", R["time"]["dom"])
print("gothic", {k: v for k, v in R["revivals"]["gothic"].items() if k not in ("table",)})
print("capitals", R["capitals"]["top"][:12], R["capitals"]["n_neo_dom"])
print("dates", R["dates"])
