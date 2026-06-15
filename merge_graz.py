"""
merge_graz.py — Build the Cool Spots Graz dataset from raw source files.

Reads raw JSON downloads from the raw_source_data_graz/ folder (see README for
download instructions) and writes graz_cool_spots.csv and graz_cool_spots.geojson.

Dependencies: Python 3.8+ standard library only (json, csv, pathlib, collections).

Sources:
  Fountains  — Stadt Graz OGD ArcGIS REST layer 19
               https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/19
  Libraries  — Stadt Graz OGD ArcGIS REST layer 23
               https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/23
  Churches   — Stadt Graz OGD ArcGIS REST layer 31
               https://geodaten.graz.at/arcgis/rest/services/OGD/OGD_WFS/MapServer/31
  Parks      — OpenStreetMap via Overpass API (see raw_source_data_graz/README.txt)
  Pools, water playgrounds, spray mist, cultural buildings — hardcoded below
               (sources: Holding Graz, Freizeitinfo.at, Hitzeaktionsplan der Stadt Graz)

Coole Raeume flag: cross-referenced against Hitzeaktionsplan der Stadt Graz,
Version 1.0 (June 2025), Chapter 5 — Orte der Abkuehlung.
  https://www.sicherheit.graz.at/cms/beitrag/10395815/12275502/
"""

import json
import csv
from pathlib import Path
from collections import Counter

# ── Paths ─────────────────────────────────────────────────────────────────────
# All paths are relative to this script's location.
BASE   = Path(__file__).parent
RAW    = BASE / "raw_source_data_graz"   # raw downloaded JSON files
OUT    = BASE                             # output CSV and GeoJSON go here

# ── Schema ────────────────────────────────────────────────────────────────────
FIELDNAMES = [
    "id", "name", "category", "subcategory",
    "address", "plz", "lat", "lon",
    "coole_raeume", "source", "license", "opening_hours",
]

records = []

# ── 1. Fountains (Trinkbrunnen) ───────────────────────────────────────────────
# Source: Stadt Graz OGD layer 19, license CC BY 4.0
with open(RAW / "brunnen.json", encoding="utf-8") as f:
    data = json.load(f)
for feat in data["features"]:
    a = feat["attributes"]
    g = feat["geometry"]
    addr_parts = [a.get("STRASSENNAME") or ""]
    if a.get("HAUS_NR"):
        addr_parts.append(a["HAUS_NR"])
    address = " ".join(addr_parts).strip()
    records.append({
        "id":           f"fountain_{a['OBJEKT_ID']}",
        "name":         f"Trinkbrunnen {address}".strip(),
        "category":     "Trinkbrunnen",
        "subcategory":  a.get("BRUNNENART") or "Trinkbrunnen",
        "address":      address,
        "plz":          "",
        "lat":          g["y"],
        "lon":          g["x"],
        "coole_raeume": "no",
        "source":       "Stadt Graz OGD - Oeffentliche Brunnen",
        "license":      "CC BY 4.0",
        "opening_hours":"24/7 (when operational)",
    })

# ── 2. Libraries (Bibliotheken) ───────────────────────────────────────────────
# Source: Stadt Graz OGD layer 23, license CC BY 4.0
# Coole Raeume: Stadtbibliothek West-Eggenberg (18), Nord-Geidorf (19), Zanklhof (20)
COOLE_LIBRARIES = {18, 19, 20}
with open(RAW / "bibliotheken.json", encoding="utf-8") as f:
    data = json.load(f)
for feat in data["features"]:
    a = feat["attributes"]
    g = feat["geometry"]
    addr_parts = [a.get("STRASSENNAME") or ""]
    if a.get("HAUSNR"):
        addr_parts.append(a["HAUSNR"])
    address = " ".join(addr_parts).strip()
    records.append({
        "id":           f"library_{a['OBJEKT_ID']}",
        "name":         a.get("NAME") or "",
        "category":     "Bibliothek",
        "subcategory":  "Bibliothek",
        "address":      address,
        "plz":          a.get("PLZ") or "",
        "lat":          g["y"],
        "lon":          g["x"],
        "coole_raeume": "yes" if a["OBJEKT_ID"] in COOLE_LIBRARIES else "no",
        "source":       "Stadt Graz OGD - Bibliotheken",
        "license":      "CC BY 4.0",
        "opening_hours":"Mon-Fri: 10:00-18:00, Sat: 10:00-13:00",
    })

# ── 3. Churches (Kirchen) ─────────────────────────────────────────────────────
# Source: Stadt Graz OGD layer 31, license CC BY 4.0
# Coole Raeume: the 10 inner-city churches in the Hitzeaktionsplan (by OBJEKT_ID)
COOLE_CHURCHES = {1704, 1682, 1706, 1732, 1651, 1762, 1663, 1737, 1664, 1646}
# Address correction: OGD has Annenstraße 2 for Barmherzigenkirche (OBJEKT_ID 1732),
# but the official address is Annenstraße 4 (verified against Hitzeaktionsplan).
ADDRESS_OVERRIDES = {1732: "Annenstraße 4"}
with open(RAW / "kirchen.json", encoding="utf-8") as f:
    data = json.load(f)
for feat in data["features"]:
    a = feat["attributes"]
    g = feat["geometry"]
    oid = a["OBJEKT_ID"]
    address = ADDRESS_OVERRIDES.get(oid) or (a.get("ADRESSE") or "").strip()
    records.append({
        "id":           f"church_{oid}",
        "name":         a.get("NAME") or "",
        "category":     "Kirche",
        "subcategory":  "Kirche",
        "address":      address,
        "plz":          a.get("PLZ") or "",
        "lat":          g["y"],
        "lon":          g["x"],
        "coole_raeume": "yes" if oid in COOLE_CHURCHES else "no",
        "source":       "Stadt Graz OGD - Kirchen und anerkannte Religionsgemeinschaften",
        "license":      "CC BY 4.0",
        "opening_hours":"Daily masses (see graz-seckau.at for schedule)",
    })

# ── 4. Parks / green spaces (OpenStreetMap via Overpass) ─────────────────────
# Source: OSM Overpass API, license ODbL 1.0
EXCLUDE_TYPES = {"garden", "sports_centre"}
with open(RAW / "parks_raw.json", encoding="utf-8") as f:
    parks = json.load(f)
for p in parks:
    if p["type"] in EXCLUDE_TYPES:
        continue
    records.append({
        "id":           f"park_{p['id']}",
        "name":         p["name"],
        "category":     "Park/Gruenraum",
        "subcategory":  p["type"],
        "address":      "",
        "plz":          "",
        "lat":          p["lat"],
        "lon":          p["lon"],
        "coole_raeume": "no",
        "source":       "OpenStreetMap (via Overpass API)",
        "license":      "ODbL 1.0",
        "opening_hours":"24/7 (public access)",
    })

# ── 5. Swimming pools (Schwimmbäder) — hardcoded ─────────────────────────────
# Source: Holding Graz / Grazer Freizeitbetriebe, license CC BY 4.0
# https://www.holding-graz.at/de/freizeit/
# These are not available via a clean open API endpoint; hardcoded for reproducibility.
POOLS = [
    ("pool_1501767308", "Augartenbad",           "Schönaugürtel 1, 8010 Graz",        "8010", 47.0585362, 15.4360009),
    ("pool_1501767309", "Stukitzbad",             "Andritzer Reichsstraße 25a, 8045 Graz","8045",47.1022092,15.4245686),
    ("pool_1501767310", "Bad Eggenberg (Auster)", "Janzgasse 21, 8020 Graz",           "8020", 47.0729377, 15.4009717),
    ("pool_1501767311", "Bad Straßgang",           "Martinhofstraße 3, 8054 Graz",      "8054", 47.0255429, 15.3956441),
    ("pool_1501767312", "Ragnitzbad",              "Pesendorferweg 7, 8047 Graz",       "8047", 47.0772227, 15.4867204),
    ("pool_1501767313", "Bad zur Sonne",           "Feuerbachgasse 11-13, 8020 Graz",   "8020", 47.0692642, 15.4319899),
]
for pid, name, address, plz, lat, lon in POOLS:
    records.append({
        "id":           pid,
        "name":         name,
        "category":     "Schwimmbad",
        "subcategory":  "Öffentliches Freibad/Hallenbad",
        "address":      address,
        "plz":          plz,
        "lat":          lat,
        "lon":          lon,
        "coole_raeume": "no",
        "source":       "Grazer Freizeitbetriebe / Stadt Graz OGD",
        "license":      "CC BY 4.0",
        "opening_hours":"May-Sep: 10:00-18:00, Jun-Aug: 09:00-20:00",
    })

# ── 6. Water playgrounds (Wasserspielplätze) — hardcoded ─────────────────────
# Source: Stadt Graz / Freizeitinfo.at / Mamilade, license CC BY 4.0
# https://www.holding-graz.at/de/stadtraum/spielplaetze/
WATERPLAY = [
    ("wasserspiel_1", "Wasserspielplatz Theodor-Körner-Straße",
     "Theodor-Körner-Straße 59", "8010", 47.0942093, 15.4237645,
     "Stadt Graz OGD / Mamilade"),
    ("wasserspiel_2", "Wasserspielplatz Tändelwiese",
     "Auf der Tändelwiese 8",    "8020", 47.052327,  15.431239,
     "Stadt Graz / Freizeitinfo.at"),
    ("wasserspiel_3", "Wasserspielplatz Langedelwehr",
     "Am Langedelwehr",          "8010", 47.0556638, 15.4371868,
     "Stadt Graz / Freizeitinfo.at"),
]
for wid, name, address, plz, lat, lon, source in WATERPLAY:
    records.append({
        "id":           wid,
        "name":         name,
        "category":     "Wasserspielplatz",
        "subcategory":  "Wasserspielplatz",
        "address":      address,
        "plz":          plz,
        "lat":          lat,
        "lon":          lon,
        "coole_raeume": "no",
        "source":       source,
        "license":      "CC BY 4.0",
        "opening_hours":"May-Sep: 09:00-19:00 (weather dependent)",
    })

# ── 7. Spray mist cooling (Sprühnebel-Lanzen) — hardcoded ────────────────────
# Source: Stadt Graz / Holding Graz Wasserwirtschaft, license CC BY 4.0
# Pilot installations active as of June 2026.
# https://www.inside-graz.at/chronik/graz-testet-spruehnebel-lanzen-gegen-sommerhitze.html
SPRAY = [
    ("spruehnebel_1", "Spruehnebel-Lanze Bad zur Sonne",
     "Feuerbachgasse 11",  "8020", 47.0695825, 15.4325888),
    ("spruehnebel_2", "Spruehnebel-Lanze Schmiedgasse",
     "Schmiedgasse 26",    "8010", 47.0684135, 15.439261),
]
for sid, name, address, plz, lat, lon in SPRAY:
    records.append({
        "id":           sid,
        "name":         name,
        "category":     "Spruehnebel-Lanze",
        "subcategory":  "Spruehnebel-Lanze",
        "address":      address,
        "plz":          plz,
        "lat":          lat,
        "lon":          lon,
        "coole_raeume": "no",
        "source":       "Stadt Graz / Holding Graz",
        "license":      "CC BY 4.0",
        "opening_hours":"On-demand during heat alerts (summer season)",
    })

# ── 8. Cultural buildings (Kulturgebäude) — hardcoded ────────────────────────
# Source: Hitzeaktionsplan der Stadt Graz, Version 1.0, June 2025, Chapter 5.
# Listed under the "Coole Räume" heading without a separating subheading,
# so coole_raeume = yes.
# https://www.sicherheit.graz.at/cms/beitrag/10395815/12275502/
CULTURAL = [
    ("cultural_1", "Kunsthaus Graz (Foyer)",
     "Lendkai 1",    "8020", 47.07140, 15.43410),
    ("cultural_2", "Graz Museum (Stadtoase)",
     "Sackstraße 18","8010", 47.07264, 15.43650),
]
for cid, name, address, plz, lat, lon in CULTURAL:
    records.append({
        "id":           cid,
        "name":         name,
        "category":     "Kulturgebäude",
        "subcategory":  "Kulturgebäude",
        "address":      address,
        "plz":          plz,
        "lat":          lat,
        "lon":          lon,
        "coole_raeume": "yes",
        "source":       "Hitzeaktionsplan der Stadt Graz (Version 1.0, Juni 2025)",
        "license":      "CC BY 4.0",
        "opening_hours":"Tue-Sun 10:00-17:00 (approx; check venue website)",
    })

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"Total records: {len(records)}")
print(dict(Counter(r["category"] for r in records)))
print(f"Coole Raeume flagged: {sum(1 for r in records if r['coole_raeume'] == 'yes')}")

# ── Write CSV ─────────────────────────────────────────────────────────────────
csv_path = OUT / "graz_cool_spots.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(records)
print(f"Written: {csv_path}")

# ── Write GeoJSON ─────────────────────────────────────────────────────────────
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r["lon"], r["lat"]],
            },
            "properties": {k: v for k, v in r.items() if k not in ("lat", "lon")},
        }
        for r in records
    ],
}
geojson_path = OUT / "graz_cool_spots.geojson"
with open(geojson_path, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)
print(f"Written: {geojson_path}")
print("Done.")
