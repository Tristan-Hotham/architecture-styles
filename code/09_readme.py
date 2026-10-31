"""README.md and LICENSE, numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
cv, fa, dt, tm, rv, cp = R["coverage"], R["families"], R["dates"], R["time"], R["revivals"], R["capitals"]
g = rv["gothic"]
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
readme = f"""# Styles in stone

The world's architectural styles on a map, century by century. Every building and structure in Wikidata with an architectural style and coordinates ({cv['n']:,} items, {fa['n_styles']:,} style labels), grouped into {fa['n_fam']} style families with a hand-checked mapping table, and mapped through time.

Interactive page: {PAGE}
Paper: https://doi.org/{{{{DOI}}}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/architecture-styles/}}

## Headline results

- The textbook sequence emerges from the data: Romanesque is {rnd(tm['s1100_romanesque'])}% of dated buildings from the 1100s, Gothic {rnd(tm['s1300_gothic'])}% of the 1300s, Renaissance {rnd(tm['s1500_renaissance'])}% of the 1500s, Baroque and Rococo {rnd(tm['s1700_baroque'])}% of the 1700s; Neoclassical leads the 1800s, Modernist (only {rnd(tm['s1900_modern'])}%) the 1900s and postmodern and contemporary styles the 2000s.
- Revivals: {fa['revival_n']:,} buildings ({rnd(fa['revival_pct'])}%) are in a revival style, {rnd(tm['s1800_revival'])}% of everything dated to the 1800s. Gothic Revival has {g['n']:,} buildings in {g['n_countries']} countries ({rnd(g['outside_europe_pct'])}% outside Europe); the first tenth of precisely dated ones were begun by {g['gbr_p10']} in Britain, {g['can_p10']} in Canada, {g['aus_p10']} in Australia, {g['usa_p10']} in the United States and {g['nzl_p10']} in New Zealand. {rnd(rv['greek']['usa_pct'])}% of {rv['greek']['n']:,} Greek Revival buildings are in the United States.
- Capitals: Neoclassical, the largest family ({fa['by']['neoclassical']:,} buildings), is the most common family in {cp['n_neo_dom']} of {cp['n_caps']} national capitals with at least {cp['min_n']} buildings within {cp['radius_km']} km: {', '.join(c.replace('Washington, D.C.', 'Washington') for c in cp['neo_dom'])}. Helsinki has the highest share ({cp['top'][0]['neo_pct']:.1f}%).
- Dates: {dt['n']:,} buildings ({rnd(dt['pct'])}%) have an inception date; {rnd(dt['round100_pct'])}% of those fall on a round century (e.g. {dt['y2000']:,} dated 2000 against {dt['y1999']} dated 1999), read here as century-precision dates.
- Coverage: the United States ({cv['top'][0]['pct']}%) and Spain ({cv['top'][1]['pct']}%) hold {rnd(cv['usa_esp_pct'])}% of all buildings; Europe {cv['europe_pct']}%, Africa {cv['africa_pct']}%; China has {cv['chn_n']} buildings with a style. This is a map of what Wikidata records, not of the world's buildings.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, `data/points.json` and `data/names.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/buildings.csv.gz` | All {cv['n']:,} buildings: Wikidata ID, English label, point, country, continent, inception year, whether it is a round century, the year used, whether the date is earlier than the style, family, revival flag, primary style, all styles, kind and sitelinks ({size('buildings.csv.gz')}). |
| `data/style_families.csv` | The mapping table: every style in use with its number of buildings, family, revival flag, how it was assigned (hand, keyword, ancestor, none) and its Wikidata parents. |
| `data/family_century.csv` | Dated buildings by century and family. |
| `data/revival_countries.csv` | Gothic Revival by country: buildings dated to a year from 1740, year of the first tenth, median year. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/points.json`, `data/names.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data (columnar points, names, style and type labels), Natural Earth outlines and place names. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. `code/families.py` holds the hand-checked decisions. |
| `release/` | Paper PDF and LaTeX source with figures, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Buildings: every Wikidata item with an architectural style (P149) and coordinates (P625), with English label, sitelinks, country (P17, else the Natural Earth country under the point), earliest inception (P571) and classes (P31).
- Families: every style used by 20 or more buildings decided by hand ({fa['how_styles']['hand']} styles, {fa['hand_pairs_pct']}% of style statements); the rest by words in the label ({fa['how_styles']['keyword']}) or the nearest classified ancestor in Wikidata's P279/P361 hierarchy ({fa['how_styles']['ancestor']}); {fa['how_styles']['none']} rare styles and general labels are 'Other or general'. Revival styles keep the family of the style they revive and carry a flag. A building with several styles takes its most specific (least used) style.
- Dates: years ending in 00 are read as the middle of the century they end (Wikidata stores '20th century' as 2000). Buildings dated more than 25 years before their style began ({dt['anach_n']:,}) are left out of the time views. The sensitivity of the century shares to this reading is reported in the paper (up to {tm['sens_maxdiff']} points).
- Caveats: very uneven coverage by country, driven by which heritage lists are in Wikidata; loose and overlapping style labels; founding dates of uncertain precision; sitelinks measure documentation, not importance.

## How to rerun

Needs Python 3 with shapely, pyproj, matplotlib, numpy and fontTools, xelatex (TeX Gyre Pagella, Inter) and pdftotext. Raw inputs (Wikidata via QLever, retrieved in {RETRIEVED}) are read in place from `{RAW}/` and Natural Earth from `{GEO}/` (set in `code/common.py`, or with `ARCH_RAW` and `ARCH_GEO`). Intermediate files go to `/dev/shm/arch/work` (set `ARCHTMP` to change). Fonts are read from `/home/claude/ref/fonts` (`ARCH_FONTS`).

```
python3 code/01_parse.py        # parse the QLever TSV files
python3 code/02_styles.py       # style families and data/style_families.csv
python3 code/03_geo.py          # countries, world outlines, place names
python3 code/04_results.py      # all analysis, results.json and page data
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 code/09_readme.py       # README and LICENSE
python3 code/08_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
```

## Sources and licences

- Wikidata (https://www.wikidata.org/), via QLever (https://qlever.cs.uni-freiburg.de/wikidata). CC0.
- Natural Earth countries and populated places (https://www.naturalearthdata.com/). Public domain.
- Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) Styles in stone: the world's architectural styles in Wikidata, mapped through time. Zenodo. https://doi.org/{{{{DOI}}}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in readme.replace("```", "").replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog, the figures and the derived data files in
data/ are released under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/). The underlying Wikidata content
is CC0. Country outlines and place names are Natural Earth (public domain).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(readme.split()), "words")
