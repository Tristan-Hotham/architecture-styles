"""Shared paths and helpers for the architecture-styles project.

Raw inputs (read in place, never modified):
  /home/claude/newdata/raw/arch/arch_pairs.tsv       item, P149 architectural style (every item with coordinates)
  /home/claude/newdata/raw/arch/arch_coords.tsv      item, P625 coordinates as WKT Point(lon lat)
  /home/claude/newdata/raw/arch/arch_labels.tsv      item, English label, sitelinks, P17 country (may repeat)
  /home/claude/newdata/raw/arch/arch_inception.tsv   item, earliest P571 inception
  /home/claude/newdata/raw/arch/arch_types.tsv       item, P31 instance of
  /home/claude/newdata/raw/arch/arch_typelabels.tsv  type, English label, count
  /home/claude/newdata/raw/arch/arch_styles.tsv      style, label, P279 parent, P361 part of, P2348 period, dates, origin, sitelinks
  /home/claude/newdata/raw/arch/arch_countries.tsv   country item, English label, ISO 3166-1 alpha-3
  /home/claude/newdata/raw/geo/ne_50m_admin_0_countries.geojson, ne_10m_populated_places_simple.geojson (Natural Earth)
All Wikidata files were retrieved through QLever in 2026 (CC0).
"""
import json, gzip, math, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("ARCH_RAW", "/home/claude/newdata/raw/arch")
GEO = os.environ.get("ARCH_GEO", "/home/claude/newdata/raw/geo")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("ARCHTMP", "/dev/shm/arch"), "work")   # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "architecture-styles"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "{{DOI}}"            # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/architecture-styles/"      # filled in by the publisher
RETRIEVED = "2026"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
WD = "http://www.wikidata.org/entity/"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text taken from Wikidata (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def val(v):
    """Plain value from a QLever TSV cell: entity IRI to QID, literal to text, blank node to ''."""
    v = v.strip()
    if v.startswith("<" + WD):
        return v[len(WD) + 1:-1]
    if v.startswith("<http://www.wikidata.org/.well-known/genid/"):
        return ""
    if v.startswith("<") and v.endswith(">"):
        return v[1:-1]
    m = re.match(r'^"(.*)"(@[\w-]+|\^\^<[^>]+>)?$', v, re.S)
    if m:
        return m.group(1).replace('\\"', '"').replace("\\\\", "\\").replace("\\t", " ").replace("\\n", " ")
    return v


def tsv(name):
    """Read a QLever TSV from RAW as a list of dicts with plain values."""
    out = []
    with open(os.path.join(RAW, name), encoding="utf-8") as f:
        head = [h.lstrip("?") for h in f.readline().rstrip("\n").split("\t")]
        for ln in f:
            parts = ln.rstrip("\n").split("\t")
            parts += [""] * (len(head) - len(parts))
            out.append({h: val(x) for h, x in zip(head, parts)})
    return out


def year_of(v):
    """Year from an xsd:dateTime string (BCE years are negative). None if unparseable."""
    m = re.match(r"^(-?)(\d{1,6})-\d\d-\d\dT", v or "")
    if not m:
        return None
    y = int(m.group(2))
    return -y if m.group(1) else y


def century_label(c):
    """c is the first year of a century bin, e.g. 1700 -> '1700s', -500 -> '500s BCE'."""
    return f"{c}s" if c >= 0 else f"{-c}s BCE"


def rnd(v):
    """Round half up (so 32.5 shows as 33 everywhere, as in the page's JavaScript)."""
    return int(math.floor(float(v) + 0.5))
