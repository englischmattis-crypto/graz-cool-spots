"""
Build an interactive folium map (graz_cool_spots_map.html) for the
"Cool Spots Graz" POI dataset.

Use case demonstrated: "I'm in Graz on a hot summer day - where can I cool
down?" The map lets a user toggle between drinking fountains, libraries,
churches, and parks/green spaces, and highlights the official "Coole Raeume"
(City of Graz cooling-spot program: 10 churches + 3 libraries).
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
}
COOL_COLOR = "#e31a1c"

with open(DATA, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

m = folium.Map(location=[47.0707, 15.4395], zoom_start=12, tiles="CartoDB positron")

groups = {
    t: folium.FeatureGroup(name=STYLE[t]["label"], show=True)
    for t in STYLE
}
coole_group = folium.FeatureGroup(name="Official 'Coole Raeume' (highlighted)", show=True)

for row in rows:
    cat = row["category"]
    style = STYLE[cat]
    lat, lon = float(row["lat"]), float(row["lon"])
    is_cool = row["coole_raeume"] == "yes"

    popup_lines = [f"<b>{row['name']}</b>"]
    popup_lines.append(f"Category: {cat} ({row['subcategory']})")
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
    if is_cool:
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=row["name"] + " (Coole Raeume)",
            icon=folium.Icon(color="white", icon_color=COOL_COLOR, icon=style["icon"], prefix="fa"),
        ).add_to(coole_group)

for g in groups.values():
    g.add_to(m)
coole_group.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

title_html = """
<div style="position: fixed; top: 10px; left: 50px; z-index: 9999;
            background: white; padding: 8px 14px; border-radius: 6px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-family: sans-serif;">
  <b>Cool Spots Graz - Where to Cool Down on a Hot Day</b><br>
  <span style="font-size: 12px;">Drinking fountains, libraries, churches, and parks/green spaces.
  Red markers = official "Coole Raeume" (City of Graz cooling program).
  Use the layer control (top right) to filter by type.</span>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

m.save(str(OUT))
print(f"Saved map with {len(rows)} markers to {OUT}")
