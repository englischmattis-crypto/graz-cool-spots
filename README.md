# Cool Spots Graz — POI Dataset

A unified, ready-to-use point-of-interest dataset of places in Graz where
people can cool down on hot summer days: drinking fountains, public
libraries, churches (cool, shaded interiors), and parks/green spaces —
including a flag for the City of Graz's official **"Coole Räume"**
(cool-rooms) program.

## Motivation

During Graz's increasingly frequent heatwaves, the City of Graz runs a
public "Orte der Abkühlung" / "Coole Räume" campaign that points residents to
10 inner-city churches and 3 climate-controlled library branches as official
cooling spots. However, this campaign list is not published as structured
open data, and it ignores other relevant, freely available cooling
infrastructure such as the city's ~180 public drinking fountains and ~90
parks and green spaces. This dataset conflates four open data sources into
**one** table with a consistent schema and a "Coole Räume" flag, so it can be
used directly to build a "where can I cool down in Graz" map, app, or
accessibility analysis.

## Files

| File | Description |
|---|---|
| `graz_cool_spots.csv` | Tabular version of the dataset (402 records, 11 columns) |
| `graz_cool_spots.geojson` | Same data as a GeoJSON FeatureCollection (point geometries, EPSG:4326 / WGS84) |
| `graz_cool_spots_map.html` | Interactive demo map (Leaflet/folium) — open in any browser |
| `merge_graz.py` | Python script that builds the dataset from the raw source files |
| `build_map_graz.py` | Python script that builds the interactive map from the dataset |

## Schema

| Column | Description |
|---|---|
| `id` | Unique record ID, prefixed by source type (`fountain_*`, `library_*`, `church_*`, `park_*`) plus the original source object ID |
| `name` | Name of the location |
| `category` | One of `Trinkbrunnen`, `Bibliothek`, `Kirche`, `Park/Gruenraum` |
| `subcategory` | Finer-grained type: for fountains always `Trinkbrunnen`; for parks one of `park`, `water_park`, `nature_reserve`, `recreation_ground`, `village_green` (from OSM `leisure`/`landuse` tags) |
| `address` | Street and house number, where available (fountains, libraries, churches) |
| `plz` | Postal code, where available (libraries, churches) |
| `lat`, `lon` | WGS84 coordinates (EPSG:4326) |
| `coole_raeume` | `yes` / `no` — whether this location is part of the City of Graz's official "Coole Räume" cooling-spot program (10 churches + 3 libraries) |
| `source` | Name of the original open-data dataset |
| `license` | License of the original source (`CC BY 4.0` or `ODbL 1.0`) |

## Record counts

- 183 drinking fountains ("Öffentliche Brunnen", all `Trinkbrunnen`)
- 35 public libraries (3 flagged as "Coole Räume")
- 93 churches and recognised religious communities (10 flagged as "Coole Räume")
- 91 parks and green spaces (from OpenStreetMap, filtered to `park`,
  `water_park`, `nature_reserve`, `recreation_ground`, `village_green`;
  `garden` and `sports_centre` excluded as not generally publicly accessible
  cool-down spots)

**Total: 402 records — 13 of which are official "Coole Räume".**

## Data sources

1. **Öffentliche Brunnen (public fountains)** — Stadt Graz Open Government
   Data, layer 19 of the OGD WFS MapServer. License: **CC BY 4.0**.
   https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/19
2. **Bibliotheken (libraries)** — Stadt Graz Open Government Data, layer 23.
   License: **CC BY 4.0**.
   https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/23
3. **Kirchen und anerkannte Religionsgemeinschaften (churches)** — Stadt Graz
   Open Government Data, layer 31. License: **CC BY 4.0**.
   https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/31
4. **Parks and green spaces** — OpenStreetMap, queried via the Overpass API
   for `leisure`/`landuse` tags within Graz's city boundary. License:
   **ODbL 1.0**, © OpenStreetMap contributors.

The "Coole Räume" flag was derived by cross-referencing the official list of
10 churches and 3 libraries published by the City of Graz:
https://www.graz.net/orte-der-abkuehlung-33368/ (article dated 5 June 2025).

All data was retrieved on **2026-06-12**.

## Collection / processing method

1. Each Stadt Graz OGD layer (fountains, libraries, churches) was queried via
   the ArcGIS REST `query` endpoint (`f=json`, `outFields=*`,
   `resultRecordCount=1000`).
2. Park/green-space data was queried from OpenStreetMap via the Overpass API
   for the Graz city area, filtered to named `leisure`/`landuse` features of
   type park, garden, water_park, nature_reserve, recreation_ground,
   village_green, or sports_centre, then restricted to the five types listed
   above.
3. The 10 official "Coole Räume" churches and 3 libraries were identified by
   matching the names/addresses on https://www.graz.net/orte-der-abkuehlung-33368/
   against the OGD church and library layers (by `OBJEKT_ID`).
4. `merge_graz.py` reads the four raw source files, maps each source's fields
   onto the common schema above, and writes `graz_cool_spots.csv` and
   `graz_cool_spots.geojson`.
5. `build_map_graz.py` reads the CSV and builds an interactive Leaflet map
   (`graz_cool_spots_map.html`) with one toggleable layer per category, plus
   a dedicated layer highlighting the official "Coole Räume" locations in
   red.

## Use case

**"It's 35°C in Graz — where can I cool down, and which spots are part of the
city's official cooling program?"**

Open `graz_cool_spots_map.html`, use the layer control to show/hide drinking
fountains, libraries, churches, and parks/green spaces, and click any marker
for its name, address, and source. The dedicated "Coole Räume" layer
highlights the 10 churches and 3 libraries that are part of the City of
Graz's official cooling-spot program, letting users compare the limited
official program against the much larger set of freely available cooling
infrastructure (fountains and parks) nearby. The same data (CSV/GeoJSON) can
be loaded into GIS software (e.g. QGIS) for accessibility analyses — e.g.
identifying neighbourhoods that are far from any official "Coole Raum" but
close to a fountain or park.

## License

This dataset combines sources under **CC BY 4.0** (Stadt Graz OGD: fountains,
libraries, churches) and **ODbL 1.0** (OpenStreetMap: parks/green spaces). In
line with ODbL's share-alike requirement for derivative databases, this
combined dataset is released under the **Open Database License (ODbL) v1.0**.

Attribution:
- Fountains, libraries, churches: © Stadt Graz – data.graz.gv.at, licensed
  under CC BY 4.0.
- Parks/green spaces: © OpenStreetMap contributors, licensed under ODbL 1.0,
  https://www.openstreetmap.org/copyright

## Update strategy

The Stadt Graz OGD layers and OpenStreetMap are both updated on an ongoing
basis. To refresh this dataset, re-run `merge_graz.py` after re-downloading
the four raw source files from the endpoints listed above, and re-check the
"Coole Räume" list at https://www.graz.net/orte-der-abkuehlung-33368/ for
changes.
