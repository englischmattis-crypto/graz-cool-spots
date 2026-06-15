import json, csv

OUT_DIR = "/sessions/wizardly-laughing-sagan/mnt/outputs"

records = []

# --- 1. Fountains (Trinkbrunnen) ---
with open(f"{OUT_DIR}/brunnen.json", encoding="utf-8") as f:
    data = json.load(f)
for feat in data["features"]:
    a = feat["attributes"]
    g = feat["geometry"]
    addr_parts = [a.get("STRASSENNAME") or ""]
    if a.get("HAUS_NR"):
        addr_parts.append(a["HAUS_NR"])
    address = " ".join(addr_parts).strip()
    records.append({
        "id": f"fountain_{a['OBJEKT_ID']}",
        "name": f"Trinkbrunnen {address}".strip(),
        "category": "Trinkbrunnen",
        "subcategory": a.get("BRUNNENART") or "Trinkbrunnen",
        "address": address,
        "plz": "",
        "lat": g["y"],
        "lon": g["x"],
        "coole_raeume": "no",
        "source": "Stadt Graz OGD - Oeffentliche Brunnen",
        "license": "CC BY 4.0",
    })

# --- 2. Libraries (Bibliotheken) ---
COOLE_LIBRARIES = {18, 19, 20}
with open(f"{OUT_DIR}/bibliotheken.json", encoding="utf-8") as f:
    data = json.load(f)
for feat in data["features"]:
    a = feat["attributes"]
    g = feat["geometry"]
    addr_parts = [a.get("STRASSENNAME") or ""]
    if a.get("HAUSNR"):
        addr_parts.append(a["HAUSNR"])
    address = " ".join(addr_parts).strip()
    records.append({
        "id": f"library_{a['OBJEKT_ID']}",
        "name": a.get("NAME") or "",
        "category": "Bibliothek",
        "subcategory": "Bibliothek",
        "address": address,
        "plz": a.get("PLZ") or "",
        "lat": g["y"],
        "lon": g["x"],
        "coole_raeume": "yes" if a["OBJEKT_ID"] in COOLE_LIBRARIES else "no",
        "source": "Stadt Graz OGD - Bibliotheken",
        "license": "CC BY 4.0",
    })

# --- 3. Churches (Kirchen) ---
COOLE_CHURCHES = {1704, 1682, 1706, 1732, 1651, 1762, 1663, 1737, 1664, 1646}
with open(f"{OUT_DIR}/kirchen.json", encoding="utf-8") as f:
    data = json.load(f)
for feat in data["features"]:
    a = feat["attributes"]
    g = feat["geometry"]
    address = (a.get("ADRESSE") or "").strip()
    records.append({
        "id": f"church_{a['OBJEKT_ID']}",
        "name": a.get("NAME") or "",
        "category": "Kirche",
        "subcategory": "Kirche",
        "address": address,
        "plz": a.get("PLZ") or "",
        "lat": g["y"],
        "lon": g["x"],
        "coole_raeume": "yes" if a["OBJEKT_ID"] in COOLE_CHURCHES else "no",
        "source": "Stadt Graz OGD - Kirchen und anerkannte Religionsgemeinschaften",
        "license": "CC BY 4.0",
    })

# --- 4. Parks / green spaces (OSM via Overpass) ---
EXCLUDE_TYPES = {"garden", "sports_centre"}
with open(f"{OUT_DIR}/parks_raw.json", encoding="utf-8") as f:
    parks = json.load(f)
for p in parks:
    if p["type"] in EXCLUDE_TYPES:
        continue
    records.append({
        "id": f"park_{p['id']}",
        "name": p["name"],
        "category": "Park/Gruenraum",
        "subcategory": p["type"],
        "address": "",
        "plz": "",
        "lat": p["lat"],
        "lon": p["lon"],
        "coole_raeume": "no",
        "source": "OpenStreetMap (via Overpass API)",
        "license": "ODbL 1.0",
    })

print(f"Total records: {len(records)}")
from collections import Counter
print(Counter(r["category"] for r in records))
print("Coole Raeume flagged:", sum(1 for r in records if r["coole_raeume"] == "yes"))

# --- Write CSV ---
fieldnames = ["id","name","category","subcategory","address","plz","lat","lon","coole_raeume","source","license"]
with open(f"{OUT_DIR}/graz_cool_spots.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in records:
        writer.writerow(r)

# --- Write GeoJSON ---
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
            "properties": {k: v for k, v in r.items() if k not in ("lat","lon")}
        }
        for r in records
    ]
}
with open(f"{OUT_DIR}/graz_cool_spots.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("Done.")
