"""Give every style a family and a revival flag (code/families.py), then every building a primary family.
Writes data/style_families.csv (the published mapping table) and WORK/stylefam.json."""
import csv
from collections import Counter, deque
from common import *
from families import FAMILIES, FKEYS, HAND, keyword_family

S = jload(f"{WORK}/styles.json"); ST = S["styles"]
items = jload(f"{WORK}/items.json")
use = Counter(s for it in items for s in it["s"])
lab = lambda q: (ST.get(q) or {}).get("label", "")

# every style used by 20 or more buildings must have a hand decision
missing = [(q, use[q], lab(q)) for q in use if use[q] >= 20 and q not in HAND]
assert not missing, missing[:20]

direct = {}
for q in set(use) | set(ST):
    if q in HAND:
        direct[q] = (HAND[q][0], HAND[q][1], "hand")
    else:
        k = keyword_family(lab(q))
        if k:
            direct[q] = (k[0], k[1], "keyword")


def via_ancestor(q):
    """Nearest ancestor (breadth first over P279 and P361) with a direct family."""
    seen, dq = {q}, deque([(q, 0)])
    while dq:
        x, d = dq.popleft()
        if x != q and x in direct:
            return direct[x][0], direct[x][1], x, d
        for p in (ST.get(x, {}).get("parents", []) + ST.get(x, {}).get("partof", [])):
            if p not in seen and d < 6:
                seen.add(p); dq.append((p, d + 1))
    return None


fam = {}
for q in use:
    if q in direct:
        f, r, how = direct[q]; via = ""
    else:
        a = via_ancestor(q)
        if a:
            f, r, via, _ = a; how = "ancestor"
        else:
            f, r, how, via = "other", False, "none", ""
    fam[q] = {"f": f, "r": r, "how": how, "via": via}

rows = []
for q in sorted(use, key=lambda q: (-use[q], q)):
    d = fam[q]; s = ST.get(q, {})
    rows.append({"style_qid": q, "style_label": dash(lab(q) or HAND.get(q, ("", "", ""))[2]), "buildings": use[q], "family": d["f"],
                 "family_name": dict((k, n) for k, n, *_ in FAMILIES)[d["f"]], "revival": int(d["r"]), "method": d["how"],
                 "via_ancestor": d["via"], "via_label": dash(lab(d["via"])) if d["via"] else "",
                 "parents": "|".join(s.get("parents", [])), "part_of": "|".join(s.get("partof", []))})
with open(f"{DATA}/style_families.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

how = Counter(fam[q]["how"] for q in use)
howp = Counter()
for it in items:
    for s in it["s"]:
        howp[fam[s]["how"]] += 1
print("styles by method", dict(how), "pairs by method", dict(howp))
print("families by styles", Counter(fam[q]["f"] for q in use).most_common())
jsave({"fam": fam, "use": dict(use), "how_styles": dict(how), "how_pairs": dict(howp)}, f"{WORK}/stylefam.json")
