"""Geography: a light world outline file for the page and figures (Natural Earth 1:50m), a country and continent for
every building (Wikidata P17 first, else point in polygon), and place names for map labels and search
(Natural Earth populated places)."""
from collections import Counter
from shapely.geometry import shape, mapping, Point
from shapely.strtree import STRtree
from common import *

W = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
iso_of = lambda p: p["ISO_A3_EH"] if p["ISO_A3_EH"] not in ("-99", None) else p["ADM0_A3"]
feats, geoms, meta = [], [], {}
for f in W["features"]:
    p = f["properties"]; iso = iso_of(p)
    g = shape(f["geometry"])
    geoms.append((iso, g))
    gs = g.simplify(0.06, preserve_topology=True)
    if gs.is_empty:
        continue
    def rnd(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            return [round(c[0], 2), round(c[1], 2)]
        return [rnd(x) for x in c]
    gm = mapping(gs)
    feats.append({"type": "Feature", "properties": {"iso": iso}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
    if iso in meta and (meta[iso]["pop"] or 0) >= (p["POP_EST"] or 0):
        continue
    meta[iso] = {"name": p["NAME_EN"] or p["NAME"], "cont": p["CONTINENT"], "sub": p["SUBREGION"], "pop": p["POP_EST"], "lx": p["LABEL_X"], "ly": p["LABEL_Y"]}
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")

S = jload(f"{WORK}/styles.json"); C = S["countries"]
items = jload(f"{WORK}/items.json")
tree = STRtree([g for _, g in geoms])
how = Counter()
for it in items:
    iso = None
    for q in it["c"]:
        if q in C and C[q][1] and C[q][1] in meta:
            iso = C[q][1]; break
    if iso:
        how["P17"] += 1
    else:
        pt = Point(it["lon"], it["lat"])
        hit = [geoms[i][0] for i in tree.query(pt) if geoms[i][1].covers(pt)]
        if not hit:
            hit = [geoms[i][0] for i in tree.query(pt.buffer(0.05)) if geoms[i][1].distance(pt) < 0.05]
        if hit:
            iso = hit[0]; how["point"] += 1
        else:
            how["none"] += 1
    it["iso"] = iso
    it["cont"] = meta[iso]["cont"] if iso else None
print("country from", dict(how))
jsave(items, f"{WORK}/items.json")

# place names: cities for labels, plus capitals
P = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")
cities = []
for f in P["features"]:
    p = f["properties"]
    pop = p.get("pop_max") or 0
    cap = p.get("adm0cap") == 1 or p.get("featurecla", "").startswith("Admin-0 capital")
    if pop >= 150000 or cap:
        cities.append({"name": re.sub(r"\s+", " ", p["name"]), "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(pop),
                       "iso": p.get("adm0_a3"), "adm1": p.get("adm1name") or "", "cap": 1 if cap else 0})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{DATA}/cities.json")
jsave(meta, f"{WORK}/countries.json")
print("cities", len(cities), "countries", len(meta))
