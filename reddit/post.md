## Title

[OC] Styles in stone: the most common architectural style in each part of Europe, century by century. Gothic is 72% of dated buildings from the 1300s; by the 1800s, 42% are revivals of older styles

## Body

I took every building in Wikidata with an architectural style and coordinates (180,451 of them, using 1,314 different style labels), sorted the labels into 25 families by hand, and placed the 82,982 usable dated ones in centuries. The textbook sequence falls out on its own: Romanesque in the 1100s (63%), Gothic in the 1300s (72%), Renaissance in the 1500s, Baroque in the 1700s (51%), then a patchwork of revivals, Art Nouveau, Art Deco and modernism. Gothic Revival alone has 10,776 buildings in 97 countries, 3,426 of them in the US. Caveat: this maps what Wikidata records, not what was built: only 0.4% of the buildings are in Africa, and the US and Spain hold 43% between them. Round-century dates (Wikidata stores "20th century" as 2000) are read as mid-century. Interactive map with a time slider: https://maps.tristanhotham.com/architecture-styles/

## Source comment

Source: Wikidata (CC0), every item with an architectural style (P149), coordinates (P625) and inception (P571), via the QLever SPARQL engine; Natural Earth outlines (public domain). Style families come from a hand-checked mapping table published with the data (data/style_families.csv).

Tools: Python (shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/architecture-styles/
Paper: https://doi.org/10.5281/zenodo.23842989
Blog post: https://blog.tristanhotham.com/2026/10/31/architecture-styles/
Data and code: https://github.com/Tristan-Hotham/architecture-styles
