"""Parse the QLever TSV files into compact intermediates in WORK: items.json (one record per building) and
styles.json (one record per style with its parents)."""
from collections import defaultdict, Counter
from common import *

# styles per item
pairs = tsv("arch_pairs.tsv")
item_styles = defaultdict(list)
for r in pairs:
    if r["item"] and r["style"] and r["style"] not in item_styles[r["item"]]:
        item_styles[r["item"]].append(r["style"])
print("pairs", len(pairs), "items", len(item_styles), "styles", len({s for v in item_styles.values() for s in v}))

# coordinates: first point per item (some items carry several)
coords, ncoord = {}, Counter()
for r in tsv("arch_coords.tsv"):
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", r["coord"], re.I)
    if not m:
        continue
    ncoord[r["item"]] += 1
    if r["item"] not in coords:
        lon, lat = float(m.group(1)), float(m.group(2))
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            coords[r["item"]] = (round(lon, 5), round(lat, 5))
multi = sum(1 for v in ncoord.values() if v > 1)

# labels, sitelinks, countries
lab, sl, ctry = {}, {}, defaultdict(list)
for r in tsv("arch_labels.tsv"):
    i = r["item"]
    if r["label"] and i not in lab:
        lab[i] = r["label"]
    try:
        sl[i] = max(sl.get(i, 0), int(r["sitelinks"] or 0))
    except ValueError:
        pass
    if r["country"] and r["country"] not in ctry[i]:
        ctry[i].append(r["country"])
cmap = {r["c"]: (r["label"], r["iso"]) for r in tsv("arch_countries.tsv")}

# inception
inc, bad_inc = {}, 0
for r in tsv("arch_inception.tsv"):
    y = year_of(r["inception"])
    if y is None:
        bad_inc += 1
        continue
    inc[r["item"]] = (y, r["inception"])

# types
tl = {r["type"]: r["label"] for r in tsv("arch_typelabels.tsv")}
tcount = {r["type"]: int(r["n"] or 0) for r in tsv("arch_typelabels.tsv")}
types = defaultdict(list)
for r in tsv("arch_types.tsv"):
    if r["type"] and r["type"] not in types[r["item"]]:
        types[r["item"]].append(r["type"])

items = []
for i, sts in item_styles.items():
    if i not in coords:
        continue
    y = inc.get(i)
    ts = sorted(types.get(i, []), key=lambda t: -tcount.get(t, 0))
    items.append({"q": i, "n": lab.get(i, ""), "sl": sl.get(i, 0), "lon": coords[i][0], "lat": coords[i][1],
                  "c": ctry.get(i, []), "y": y[0] if y else None, "d": y[1] if y else "", "s": sts,
                  "t": [t for t in ts if tl.get(t)][:3]})
print("items with coords", len(items), "multi-coord items", multi, "inception", sum(1 for x in items if x["y"] is not None), "unparsed inception", bad_inc)

# styles
st = {}
for r in tsv("arch_styles.tsv"):
    s = r["style"]
    if not s.startswith("Q"):
        continue
    d = st.setdefault(s, {"q": s, "label": "", "parents": [], "partof": [], "period": [], "inception": "", "start": "", "end": "", "origin": [], "sitelinks": 0})
    if r["label"] and not d["label"]:
        d["label"] = r["label"]
    for k, kk in (("parent", "parents"), ("partof", "partof"), ("period", "period"), ("origin", "origin")):
        if r[k] and r[k] not in d[kk]:
            d[kk].append(r[k])
    for k in ("inception", "start", "end"):
        if r[k] and not d[k]:
            d[k] = r[k]
    try:
        d["sitelinks"] = max(d["sitelinks"], int(r["sitelinks"] or 0))
    except ValueError:
        pass
print("style rows", len(st))
jsave(items, f"{WORK}/items.json")
jsave({"styles": st, "typelabels": tl, "countries": cmap, "multi_coord": multi, "pairs": len(pairs)}, f"{WORK}/styles.json")
