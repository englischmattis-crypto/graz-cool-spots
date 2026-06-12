"""
Build an interactive folium map (graz_cool_spots_map.html) for the
"Cool Spots Graz" POI dataset.

Use case demonstrated: "I'm in Graz on a hot summer day - where can I cool
down?" The map lets a user toggle between drinking fountains, libraries,
churches, and parks/green spaces. Red markers indicate official "Coole Raeume"
(City of Graz cooling-spot program).
"""

import csv
import folium
from folium.plugins import MarkerCluster
from pathlib import Path

DATA = Path("/sessions/wizardly-laughing-sagan/mnt/outputs/graz_cool_spots.csv")
OUT = Path("/sessions/wizardly-laughing-sagan/mnt/outputs/graz_cool_spots_map.html")

STYLE = {
    "Trinkbrunnen":   {"color": "#1f78b4", "icon": "tint",  "label": "Drinking fountains (Trinkbrunnen)"},
    "Bibliothek":     {"color": "#33a02c", "icon": "book",  "label": "Libraries (Bibliotheken)"},
    "Kirche":         {"color": "#6a3d9a", "icon": "place-of-worship", "label": "Churches (Kirchen)"},
    "Park/Gruenraum": {"color": "#33a02c", "icon": "tree",  "label": "Parks & green spaces"},
    "Wasserspielplatz": {"color": "#0ea5e9", "icon": "water",  "label": "Water playgrounds (Wasserspielplaetze)"},
    "Spruehnebel-Lanze": {"color": "#06b6d4", "icon": "shower",  "label": "Spray mist cooling (Spruehnebel-Lanzen)"},
}
COOL_COLOR = "#e31a1c"

with open(DATA, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

m = folium.Map(location=[47.0707, 15.4395], zoom_start=12, tiles="CartoDB positron")

groups = {
    t: folium.FeatureGroup(name=STYLE[t]["label"], show=True)
    for t in STYLE
}

for row in rows:
    cat = row["category"]
    if cat not in STYLE:
        print(f"Warning: Unknown category {cat}")
        continue
    style = STYLE[cat]
    lat, lon = float(row["lat"]), float(row["lon"])
    is_cool = row["coole_raeume"] == "yes"

    popup_lines = [f"<b>{row['name']}</b>"]
    # Only show subcategory for parks (where it provides useful detail like water_park, nature_reserve)
    if cat == "Park/Gruenraum":
        popup_lines.append(f"Type: {row['subcategory']}")
    if row["address"]:
        popup_lines.append(f"Address: {row['address']}")
    if is_cool:
        popup_lines.append("<b style='color:#e31a1c;'>Official Coole Raeume (City of Graz)</b>")
    popup_lines.append(f"<i>Source: {row['source']} ({row['license']})</i>")
    popup_html = "<br>".join(popup_lines)

    color = COOL_COLOR if is_cool else style["color"]
    icon = folium.Icon(color="white", icon_color=color, icon=style["icon"], prefix="fa")

    marker = folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=row["name"],
        icon=icon,
    )
    marker.add_to(groups[cat])

for g in groups.values():
    g.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

title_html = '<div style="position: fixed; top: 10px; left: 50px; z-index: 9999; background: white; padding: 8px 14px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-family: sans-serif; max-width: 360px;"><b>Cool Spots Graz</b><br><span style="font-size: 12px;">Red markers = official Coole Raeume cooling spots. Use layers (top right) to filter by type: fountains, libraries, churches, parks, water playgrounds, or spray cooling.</span><br><a href="about.html" style="font-size: 12px; color: #1C7293; font-weight: bold;">About this dataset &rarr;</a></div>'

