# Cool Spots Graz — POI Dataset

A unified, ready-to-use point-of-interest dataset of places in Graz where people can cool down on hot summer days: drinking fountains, public libraries, churches, parks and green spaces, public swimming pools, water playgrounds, spray mist cooling installations, and cultural buildings — including a flag for the City of Graz's official **"Coole Räume"** (cool-rooms) program.

## Motivation

During Graz's increasingly frequent heatwaves, the City of Graz runs a public "Orte der Abkühlung / Coole Räume" campaign that points residents to 10 inner-city churches and 3 climate-controlled library branches as official cooling spots. However, this list is not published as structured open data, and it ignores other relevant, freely available cooling infrastructure such as the city's 172 public drinking fountains and 88 parks and green spaces. This dataset conflates multiple open data sources into **one** table with a consistent schema and a `coole_raeume` flag, so it can be used directly to build a "where can I cool down in Graz" map, app, or accessibility analysis.

## Files

| File | Description |
|---|---|
| `graz_cool_spots.csv` | Tabular version of the dataset (291 records, 12 columns) |
| `graz_cool_spots.geojson` | Same data as a GeoJSON FeatureCollection (point geometries, EPSG:4326 / WGS84) |
| `graz_cool_spots_map.html` / `index.html` | Interactive demo map (Leaflet/folium) — open in any browser |
| `merge_graz.py` | Python script that builds the dataset from the raw source files |
| `build_map_graz.py` | Python script that builds the interactive map from the dataset |
| `raw_source_data_graz/` | Raw downloads from each source, for traceability |

## Schema

| Column | Description |
|---|---|
| `id` | Unique record ID, prefixed by source type (`fountain_*`, `library_*`, `church_*`, `park_*`, `pool_*`, `waterplay_*`, `spray_*`, `cultural_*`) plus the original source object ID |
| `name` | Name of the location |
| `category` | One of `Trinkbrunnen`, `Bibliothek`, `Kirche`, `Park/Gruenraum`, `Schwimmbad`, `Wasserspielplatz`, `Spruehnebel-Lanze`, `Kulturgebäude` |
| `subcategory` | Finer-grained type: for parks one of `park`, `water_park`, `nature_reserve`, `recreation_ground`, `village_green` (from OSM `leisure`/`landuse` tags) |
| `address` | Street and house number, where available |
| `plz` | Postal code, where available |
| `lat`, `lon` | WGS84 coordinates (EPSG:4326) |
| `coole_raeume` | `yes` / `no` — whether this location is part of the City of Graz's official "Coole Räume" cooling-spot campaign (10 churches + 3 libraries = 13 total) |
| `source` | Name of the original open-data dataset |
| `license` | License of the original source (`CC BY 4.0` or `ODbL 1.0`) |
| `opening_hours` | Opening hours where available; empty for fountains and parks which are always accessible |

## Record counts

- **172** drinking fountains ("Öffentliche Brunnen", all `Trinkbrunnen`)
- **88** parks and green spaces (from OpenStreetMap, filtered to `park`, `water_park`, `nature_reserve`, `recreation_ground`, `village_green`; `garden` and `sports_centre` excluded as not generally accessible cooling spots)
- **10** churches — all 10 flagged as official "Coole Räume"
- **8** public libraries (Stadtbibliothek Graz branches — 3 flagged as "Coole Räume")
- **6** public swimming pools (Schwimmbäder, operated by Grazer Freizeitbetriebe)
- **3** water playgrounds (Wasserspielplätze)
- **2** spray mist cooling installations (Sprühnebel-Lanzen, test locations as of June 2026)
- **2** cultural buildings (Kulturgebäude): Kunsthaus Graz (foyer) and Graz Museum (Stadtoase courtyard), recommended in the Hitzeaktionsplan but not formally part of the "Coole Räume" campaign

**Total: 291 records — 13 of which are official "Coole Räume" (10 churches + 3 libraries).**

## Data sources

1. **Öffentliche Brunnen (public fountains)** — Stadt Graz Open Government Data. License: **CC BY 4.0**.  
   https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/19

2. **Bibliotheken (libraries)** — Stadt Graz Open Government Data. License: **CC BY 4.0**.  
   https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/23

3. **Kirchen und anerkannte Religionsgemeinschaften (churches)** — Stadt Graz Open Government Data. License: **CC BY 4.0**.  
   https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/31

4. **Parks and green spaces** — OpenStreetMap, queried via the Overpass API for `leisure`/`landuse` tags within Graz's city boundary. License: **ODbL 1.0**, © OpenStreetMap contributors.

5. **Schwimmbäder (public swimming pools)** — Grazer Freizeitbetriebe GmbH / Stadt Graz OGD. License: **CC BY 4.0**.  
   https://www.freizeitbetriebe.graz.at

6. **Wasserspielplätze (water playgrounds)** — Stadt Graz / Freizeitinfo.at / Mamilade. License: **CC BY 4.0**.

7. **Sprühnebel-Lanzen (spray mist cooling)** — Stadt Graz / Holding Graz. License: **CC BY 4.0**.

8. **Kulturgebäude (cultural buildings)** — Hitzeaktionsplan der Stadt Graz, Version 1.0 (June 2025), Chapter 5. License: **CC BY 4.0**.  
   https://www.sicherheit.graz.at/cms/beitrag/10395815/12275502/Der_Hitzeaktionsplan_der_Stadt_Graz.html

The "Coole Räume" flag was derived by cross-referencing the official list from the Hitzeaktionsplan der Stadt Graz (Version 1.0, June 2025, Chapter 5 — Orte der Abkühlung) against the OGD church and library layers, matched by object ID.

All data was retrieved on **2026-06-12**.

## Collection / processing method

1. Each Stadt Graz OGD layer (fountains, libraries, churches) was queried via the ArcGIS REST `query` endpoint (`f=json`, `outFields=*`, `resultRecordCount=1000`).
2. Park/green-space data was queried from OpenStreetMap via the Overpass API for the Graz city area, filtered to named `leisure`/`landuse` features of type `park`, `water_park`, `nature_reserve`, `recreation_ground`, `village_green`.
3. Swimming pools were sourced from Grazer Freizeitbetriebe / Stadt Graz OGD.
4. Water playgrounds and spray mist installations were identified through Stadt Graz public sources.
5. Cultural buildings (Kunsthaus Graz, Graz Museum) were identified from Chapter 5 of the Hitzeaktionsplan.
6. The 13 official "Coole Räume" (10 churches + 3 libraries) were identified by matching the Hitzeaktionsplan's published list against the OGD layers by object ID.
7. `merge_graz.py` reads the source files, maps each source onto the common schema, and writes `graz_cool_spots.csv` and `graz_cool_spots.geojson`.
8. `build_map_graz.py` reads the CSV and builds an interactive Leaflet map with one toggleable layer per category, mobile-responsive layout, and a "locate me" button.

## Use case

**"It's 35°C in Graz — where can I cool down, and which spots are part of the city's official cooling program?"**

Open `graz_cool_spots_map.html`, use the layer control to show/hide cooling spot types, and tap any marker for its name, address, and source. Red markers indicate the 13 official "Coole Räume." The same data (CSV/GeoJSON) can be loaded into QGIS for accessibility analyses — e.g. identifying neighbourhoods far from any official "Coole Raum" but close to a fountain or park.

## License

This dataset combines sources under **CC BY 4.0** (all Stadt Graz OGD layers, Freizeitbetriebe, Holding Graz, Hitzeaktionsplan) and **ODbL 1.0** (OpenStreetMap parks/green spaces). In line with ODbL's share-alike requirement for derivative databases, the combined dataset is released under the **Open Database License (ODbL) v1.0**. See `LICENSE.md` for the full text and attribution requirements.

Attribution:
- Fountains, libraries, churches: © Stadt Graz — data.graz.gv.at, CC BY 4.0.
- Swimming pools: © Grazer Freizeitbetriebe GmbH / Stadt Graz OGD, CC BY 4.0.
- Water playgrounds, spray mist: © Stadt Graz / Holding Graz / Mamilade, CC BY 4.0.
- Cultural buildings: © Stadt Graz, derived from Hitzeaktionsplan Version 1.0, CC BY 4.0.
- Parks/green spaces: © OpenStreetMap contributors, ODbL 1.0, https://www.openstreetmap.org/copyright

## Update strategy

The Stadt Graz OGD layers and OpenStreetMap are updated on an ongoing basis. To refresh this dataset, re-run `merge_graz.py` after re-downloading the raw source files from the endpoints listed above, and re-check the "Coole Räume" list in the Hitzeaktionsplan der Stadt Graz (updated annually before summer) for any changes.

## AI assistance disclosure

The dataset content — source selection, schema design, Coole Räume flag methodology, record collection, and all analytical decisions — was carried out by the author. AI assistance (Claude, Anthropic) was used for the build scripts (`merge_graz.py`, `build_map_graz.py`), the interactive map code, and the website documentation (`about.html`). No data was generated or inferred by AI; all records originate from the open sources listed above.
