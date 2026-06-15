import csv
import folium
from folium.plugins import LocateControl
from pathlib import Path

DATA = Path("graz_cool_spots.csv")
OUT  = Path("graz_cool_spots_map.html")

STYLE = {
    "Trinkbrunnen":     {"color": "#1f78b4", "icon": "tint",             "label": "Drinking fountains (Trinkbrunnen)"},
    "Bibliothek":       {"color": "#33a02c", "icon": "book",             "label": "Libraries (Bibliotheken)"},
    "Kirche":           {"color": "#6a3d9a", "icon": "place-of-worship", "label": "Churches (Kirchen)"},
    "Park/Gruenraum":   {"color": "#33a02c", "icon": "tree",             "label": "Parks & green spaces"},
    "Wasserspielplatz": {"color": "#0ea5e9", "icon": "water",            "label": "Water playgrounds (Wasserspielplätze)"},
    "Schwimmbad":       {"color": "#2E86AB", "icon": "swimmer",          "label": "Public swimming pools (Schwimmbäder)"},
    "Spruehnebel-Lanze":{"color": "#06b6d4", "icon": "shower",          "label": "Spray mist cooling (Sprühnebel-Lanzen)"},
    "Kulturgebäude":    {"color": "#b45309", "icon": "landmark",         "label": "Cultural buildings / Coole Räume (Kulturgebäude)"},
}
COOL_COLOR = "#e31a1c"

with open(DATA, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Fix viewport: allow user scaling (accessibility)
m = folium.Map(
    location=[47.0707, 15.4395],
    zoom_start=13,
    tiles="CartoDB positron",
    zoom_control=True,
)

# Patch viewport meta to allow user scaling
m.get_root().header.add_child(folium.Element(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
))

# Layer control: collapsed=True — expands on tap, doesn't cover the map
groups = {
    t: folium.FeatureGroup(name=STYLE[t]["label"], show=True)
    for t in STYLE
}

for row in rows:
    cat = row["category"]
    if cat not in STYLE:
        continue
    style = STYLE[cat]
    lat, lon = float(row["lat"]), float(row["lon"])
    is_cool = row["coole_raeume"] == "yes"

    popup_lines = [f"<b>{row['name']}</b>"]
    if row["address"]:
        popup_lines.append(f"<span style='color:#555'>📍 {row['address']}</span>")
    if row.get("opening_hours") and row["opening_hours"].strip():
        popup_lines.append(f"<span style='color:#555'>🕐 {row['opening_hours']}</span>")
    if is_cool:
        popup_lines.append("<b style='color:#e31a1c'>★ Official Coole Räume</b>")
    popup_lines.append(f"<span style='color:#888;font-size:11px'>{row['source']}<br>{row['license']}</span>")
    popup_html = "<br>".join(popup_lines)

    color = COOL_COLOR if is_cool else style["color"]
    icon = folium.Icon(color="white", icon_color=color, icon=style["icon"], prefix="fa")
    marker = folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=row["name"],
        icon=icon,
    )
    marker.add_to(groups[cat])

for g in groups.values():
    g.add_to(m)

# collapsed=True: always collapses behind a layers icon — works great on mobile
folium.LayerControl(collapsed=True).add_to(m)

# "Locate me" button
LocateControl(auto_start=False, position="topleft").add_to(m)

# ── Responsive title panel ──────────────────────────────────────────────────
# On mobile: compact bar at bottom of screen; on desktop: top-left panel.
# Toggle button lets users hide/show the info text.
title_html = """
<style>
  /* ── Info panel ── */
  #cs-panel {
    position: fixed;
    z-index: 9999;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    font-family: Calibri, Arial, sans-serif;
    transition: all 0.2s ease;
  }
  /* Desktop: top-left */
  @media (min-width: 600px) {
    #cs-panel {
      top: 10px;
      left: 50px;
      max-width: 340px;
      padding: 10px 14px 10px 14px;
    }
    #cs-toggle { display: none; }
  }
  /* Mobile: bottom bar that expands upward */
  @media (max-width: 599px) {
    #cs-panel {
      bottom: 0;
      left: 0;
      right: 0;
      border-radius: 12px 12px 0 0;
      padding: 0;
      max-width: 100%;
    }
    #cs-toggle {
      display: block;
      width: 100%;
      background: #0C4A6E;
      color: white;
      border: none;
      border-radius: 12px 12px 0 0;
      padding: 10px 16px;
      font-size: 15px;
      font-family: Calibri, Arial, sans-serif;
      font-weight: bold;
      text-align: left;
      cursor: pointer;
      letter-spacing: 0.02em;
    }
    #cs-toggle::after {
      float: right;
      content: attr(data-arrow);
    }
    #cs-body { padding: 12px 16px 16px; }
    #cs-body.hidden { display: none; }
  }
  #cs-body h3 {
    margin: 0 0 4px 0;
    font-size: 15px;
    color: #0C4A6E;
  }
  #cs-body p {
    margin: 0 0 6px 0;
    font-size: 13px;
    color: #333;
    line-height: 1.4;
  }
  #cs-body a {
    font-size: 13px;
    color: #1C7293;
    font-weight: bold;
    text-decoration: none;
  }
  /* Legend dots */
  .cs-legend { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px 12px; }
  .cs-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>

<div id="cs-panel">
  <button id="cs-toggle" data-arrow="▲" onclick="togglePanel()">🌊 Cool Spots Graz</button>
  <div id="cs-body">
    <h3>Cool Spots Graz</h3>
    <p>
      <span style="background:#e31a1c;color:white;border-radius:3px;padding:1px 5px;font-size:12px">RED</span>
      = official <b>Coole Räume</b>.
      Tap the <b>⊞ layers icon</b> (top right) to filter by type.
    </p>
    <a href="about.html">About this dataset &rarr;</a>
  </div>
</div>

<script>
function togglePanel() {
  var body  = document.getElementById('cs-body');
  var btn   = document.getElementById('cs-toggle');
  var open  = !body.classList.contains('hidden');
  body.classList.toggle('hidden', open);
  btn.setAttribute('data-arrow', open ? '▲' : '▼');
}
// Start collapsed on mobile
if (window.innerWidth < 600) {
  document.getElementById('cs-body').classList.add('hidden');
  document.getElementById('cs-toggle').setAttribute('data-arrow', '▲');
}
</script>
"""
m.get_root().html.add_child(folium.Element(title_html))

m.save(str(OUT))
print(f"Saved map with {len(rows)} markers to {OUT}")
