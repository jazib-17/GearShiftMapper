import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import fastf1

fastf1.Cache.enable_cache("fastf1_cache")

year = 2025
race = "Belgium"
rotate_angle = 90

# ---------------------------------------------------------
# Load session and pole lap
# ---------------------------------------------------------
session = fastf1.get_session(year, race, "Q")
session.load()

lap = session.laps.pick_fastest()
tel = lap.get_telemetry()

# ---------------------------------------------------------
# Build line segments and per-segment gear (raw telemetry, no mini-sectors)
# ---------------------------------------------------------
gear = tel["nGear"].to_numpy(dtype=float)

def rotate(x, y, degrees):
    a = np.deg2rad(degrees)
    return (x * np.cos(a) - y * np.sin(a),
            x * np.sin(a) + y * np.cos(a))

x = tel["X"].to_numpy(dtype=float)
y = tel["Y"].to_numpy(dtype=float)

x, y = rotate(x, y, rotate_angle)

points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Each segment takes the gear at its starting sample
segment_gears = gear[:-1]

# Drop segments containing NaN positions or gears
valid = ~np.isnan(segments).any(axis=(1, 2)) & ~np.isnan(segment_gears)
segments = segments[valid]
segment_gears = np.clip(segment_gears[valid], 1, 8)

# ---------------------------------------------------------
# Colors: same palette, as a discrete colormap
# ---------------------------------------------------------
gear_colors = [
    "#0E4831",  # 1st
    "#0B9994",  # 2nd
    "#6DB45F",  # 3rd
    "#E8C61E",  # 4th
    "#D99309",  # 5th
    "#BF512C",  # 6th
    "#B389A7",  # 7th
    "#8A6FE7",  # 8th
]

cmap = ListedColormap(gear_colors)
norm = BoundaryNorm(np.arange(0.5, 9.5), cmap.N)  # gear n -> n-th color

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor("#2e2e2e")
ax.set_facecolor("#2e2e2e")

lc = LineCollection(
    segments,
    cmap=cmap,
    norm=norm,
    linewidths=6,
    capstyle="butt",
    joinstyle="round",
)
lc.set_array(segment_gears)
ax.add_collection(lc)

ax.autoscale()
ax.set_aspect("equal", adjustable="box")
ax.axis("off")
ax.margins(0.02)

plt.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.02)

ax.set_title(
    f"{session.event.year} {session.event['EventName']} – Qualifying Pole Lap\n"
    f"Gear Shifts ({lap['Driver']})",
    fontsize=22,
    color="#ffffff",
    pad=15,
)

# ---------------------------------------------------------
# Legend (unchanged)
# ---------------------------------------------------------
legend_handles = [
    Patch(facecolor=gear_colors[g - 1], edgecolor="none", label=str(g))
    for g in range(1, 9)
]

legend = ax.legend(
    handles=legend_handles,
    title="Gear",
    loc="upper left",
    frameon=False,
    ncol=1,
    handlelength=1,
    handleheight=1,
    handletextpad=0.7,
    borderpad=0.5,
    labelcolor="#ffffff",
    title_fontsize=14,
    fontsize=12,
)
legend.get_title().set_color("#ffffff")

plt.show()