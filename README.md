# Cool Spots Graz: POI Dataset

A unified point-of-interest dataset of urban cooling spots in Graz, Austria: drinking fountains, parks, churches, libraries, swimming pools, water playgrounds, spray mist installations, and cultural buildings, including a `coole_raeume` flag for the City of Graz's official "Coole Räume" program.

**291 records · 8 categories · 12 attributes · 15 official "Coole Räume"**

For full documentation: schema, data sources, collection method, use cases, and license details. See [`about.html`](about.html) or the [published dataset page](https://englischmattis-crypto.github.io/graz-cool-spots/about.html).

## Files

| File | Description |
|---|---|
| `graz_cool_spots.csv` | Tabular dataset (291 records, 12 columns) |
| `graz_cool_spots.geojson` | Same data as GeoJSON (EPSG:4326 / WGS84) |
| `index.html` | Interactive Leaflet map, open in any browser |
| `about.html` | Full dataset documentation |
| `merge_graz.py` | Python script to rebuild the dataset from raw sources |
| `build_map_graz.py` | Python script to rebuild the interactive map |
| `raw_source_data_graz/` | Raw source downloads, for traceability |

## Quick start

```bash
# Rebuild dataset from raw sources
python merge_graz.py

# Rebuild map
python build_map_graz.py
# then open graz_cool_spots_map.html in a browser
```

## License

Released under **ODbL 1.0** (share-alike, attribution required). Sources: Stadt Graz OGD (CC BY 4.0), OpenStreetMap (ODbL 1.0), Hitzeaktionsplan der Stadt Graz (CC BY 4.0). See `LICENSE.md` for full attribution requirements.

## AI assistance disclosure

Dataset content, source selection, schema design, Coole Räume flag methodology, and all analytical decisions were carried out by the author. AI assistance (Claude, Anthropic) was used for the build scripts, interactive map code, and website documentation. No data was generated or inferred by AI; all records originate from the open sources listed in `about.html`.
