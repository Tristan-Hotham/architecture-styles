# Styles in stone

The world's architectural styles on a map, century by century. Every building and structure in Wikidata with an architectural style and coordinates (180,451 items, 1,314 style labels), grouped into 25 style families with a hand-checked mapping table, and mapped through time.

Interactive page: https://maps.tristanhotham.com/architecture-styles/
Paper: https://doi.org/{{DOI}}
Blog post: https://blog.tristanhotham.com/2026/10/31/architecture-styles/

## Headline results

- The textbook sequence emerges from the data: Romanesque is 63% of dated buildings from the 1100s, Gothic 72% of the 1300s, Renaissance 43% of the 1500s, Baroque and Rococo 51% of the 1700s; Neoclassical leads the 1800s, Modernist (only 17%) the 1900s and postmodern and contemporary styles the 2000s.
- Revivals: 36,445 buildings (20%) are in a revival style, 42% of everything dated to the 1800s. Gothic Revival has 10,776 buildings in 97 countries (40% outside Europe); the first tenth of precisely dated ones were begun by 1832 in Britain, 1848 in Canada, 1849 in Australia, 1854 in the United States and 1864 in New Zealand. 96% of 5,518 Greek Revival buildings are in the United States.
- Capitals: Neoclassical, the largest family (26,140 buildings), is the most common family in 6 of 53 national capitals with at least 40 buildings within 15 km: Helsinki, Washington, Tbilisi, Paris, London, Havana. Helsinki has the highest share (32.5%).
- Dates: 86,148 buildings (48%) have an inception date; 21% of those fall on a round century (e.g. 2,374 dated 2000 against 51 dated 1999), read here as century-precision dates.
- Coverage: the United States (22.3%) and Spain (20.7%) hold 43% of all buildings; Europe 67.9%, Africa 0.4%; China has 381 buildings with a style. This is a map of what Wikidata records, not of the world's buildings.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, `data/points.json` and `data/names.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/buildings.csv.gz` | All 180,451 buildings: Wikidata ID, English label, point, country, continent, inception year, whether it is a round century, the year used, whether the date is earlier than the style, family, revival flag, primary style, all styles, kind and sitelinks (gzipped CSV). |
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
- Families: every style used by 20 or more buildings decided by hand (478 styles, 99.0% of style statements); the rest by words in the label (417) or the nearest classified ancestor in Wikidata's P279/P361 hierarchy (61); 358 rare styles and general labels are 'Other or general'. Revival styles keep the family of the style they revive and carry a flag. A building with several styles takes its most specific (least used) style.
- Dates: years ending in 00 are read as the middle of the century they end (Wikidata stores '20th century' as 2000). Buildings dated more than 25 years before their style began (3,166) are left out of the time views. The sensitivity of the century shares to this reading is reported in the paper (up to 20.2 points).
- Caveats: very uneven coverage by country, driven by which heritage lists are in Wikidata; loose and overlapping style labels; founding dates of uncertain precision; sitelinks measure documentation, not importance.

## How to rerun

Needs Python 3 with shapely, pyproj, matplotlib, numpy and fontTools, xelatex (TeX Gyre Pagella, Inter) and pdftotext. Raw inputs (Wikidata via QLever, retrieved in 2026) are read in place from `/home/claude/newdata/raw/arch/` and Natural Earth from `/home/claude/newdata/raw/geo/` (set in `code/common.py`, or with `ARCH_RAW` and `ARCH_GEO`). Intermediate files go to `/dev/shm/arch/work` (set `ARCHTMP` to change). Fonts are read from `/home/claude/ref/fonts` (`ARCH_FONTS`).

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

Hotham, T. (2026) Styles in stone: the world's architectural styles in Wikidata, mapped through time. Zenodo. https://doi.org/{{DOI}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
