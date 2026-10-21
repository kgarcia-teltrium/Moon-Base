import re
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# INPUT FILE
# ==========================================================

csv_file = r"C:\Users\kgarcia\MoonBase\Moon Base Frequencies(Sheet1).csv"

# ==========================================================
# LINK / BAND DEFINITIONS (MHz)
# Each link type -> band -> list of allowed (min, max) ranges.
# Bands with more than one range (e.g. Surface-to-Surface UHF)
# are plotted on one axis with each allowed range shaded.
# ==========================================================

LINK_BANDS = {
    "Uplink": {
        "S":  [(2025, 2110)],
        "X":  [(7190, 7235)],
        "Ka": [(22550, 23150)],
    },
    "Downlink": {
        "S":  [(2200, 2290)],
        "X":  [(8450, 8500)],
        "Ka": [(25500, 27000)],
    },
    "Lunar Relay Crosslink (Forward Link)": {
        "Ku": [(13750, 14000)],
        "Ka": [(23150, 23550)],
    },
    "Lunar Relay Crosslink (Return Link)": {
        "Ku": [(14500, 15350)],
        "Ka": [(27000, 27500)],
    },
    "Lunar Orbit-to-Lunar Surface (Proximity Link)": {
        "UHF": [(390, 405)],
        "S":   [(2025, 2100)],
        "Ka":  [(23150, 23550)],
    },
    "Lunar Surface-to-Lunar Orbit (Proximity Link)": {
        "UHF": [(435, 450)],
        "S":   [(2200, 2290)],
        "Ka":  [(27000, 27500)],
    },
    "Lunar Surface to Surface (Proximity Link)": {
        "UHF": [(390, 405), (410, 420), (435, 450)],
        "ISM": [(2400, 2480)],
    },
}

LINK_ORDER = list(LINK_BANDS.keys())
BAND_ORDER = ["UHF", "S", "ISM", "X", "Ku", "Ka"]

BAND_LABEL = {
    "UHF": "UHF-Band",
    "S":   "S-Band",
    "ISM": "2.4 GHz ISM Band",
    "X":   "X-Band",
    "Ku":  "Ku-Band",
    "Ka":  "Ka-Band",
}

LINK_COLOR = {
    "Uplink": "tab:blue",
    "Downlink": "tab:red",
    "Lunar Relay Crosslink (Forward Link)": "tab:green",
    "Lunar Relay Crosslink (Return Link)": "tab:orange",
    "Lunar Orbit-to-Lunar Surface (Proximity Link)": "tab:purple",
    "Lunar Surface-to-Lunar Orbit (Proximity Link)": "tab:brown",
    "Lunar Surface to Surface (Proximity Link)": "tab:cyan",
}

LINK_SHORT = {
    "Uplink": "Uplink",
    "Downlink": "Downlink",
    "Lunar Relay Crosslink (Forward Link)": "Relay Forward",
    "Lunar Relay Crosslink (Return Link)": "Relay Return",
    "Lunar Orbit-to-Lunar Surface (Proximity Link)": "Orbit-Surface",
    "Lunar Surface-to-Lunar Orbit (Proximity Link)": "Surface-Orbit",
    "Lunar Surface to Surface (Proximity Link)": "Surface-Surface",
}


# ==========================================================
# CLASSIFIERS
# ==========================================================

def link_type(direction):
    """Map a 'Mission Link Direction' string to one of the LINK_BANDS keys."""
    d = re.sub(r"[-_/]", " ", str(direction).lower())
    d = re.sub(r"\s+", " ", d)

    # Crosslinks first ("forward" would otherwise be read as an uplink)
    if "crosslink" in d or "cross link" in d:
        if "return" in d:
            return "Lunar Relay Crosslink (Return Link)"
        return "Lunar Relay Crosslink (Forward Link)"

    # Proximity links
    if re.search(r"surface to (lunar )?surface", d):
        return "Lunar Surface to Surface (Proximity Link)"
    if re.search(r"orbit to (lunar )?surface", d):
        return "Lunar Orbit-to-Lunar Surface (Proximity Link)"
    if re.search(r"surface to (lunar )?orbit", d):
        return "Lunar Surface-to-Lunar Orbit (Proximity Link)"

    # Direct-to-Earth links
    if "uplink" in d or "forward" in d:
        return "Uplink"
    return "Downlink"


def normalize_band(value):
    """Normalize the 'Frequency Band' cell to S, X, Ka, Ku, UHF or ISM."""
    b = str(value).strip().upper()
    if "ISM" in b or "2.4" in b:
        return "ISM"
    b = re.sub(r"[\s\-]*BAND", "", b).strip()
    return {"S": "S", "X": "X", "KA": "Ka", "KU": "Ku", "UHF": "UHF"}.get(b, b)


def in_any_range(freq, ranges):
    return any(lo <= freq < hi for lo, hi in ranges)


# ==========================================================
# READ CSV
# ==========================================================

df = pd.read_csv(csv_file)
df.columns = df.columns.str.strip()

for col in ["Mission Name", "Mission Link Direction", "Frequency Band"]:
    df[col] = df[col].astype(str).str.strip()

df["Center Frequency"] = pd.to_numeric(df["Center Frequency"], errors="coerce")
df["Max Bandwidth"] = pd.to_numeric(df["Max Bandwidth"], errors="coerce")

df["Link"] = df["Mission Link Direction"].apply(link_type)
df["Band"] = df["Frequency Band"].apply(normalize_band)

# ==========================================================
# VALIDATE BAND ASSIGNMENTS
# ==========================================================

print("\nChecking frequency assignments...\n")

for _, row in df.iterrows():
    link, band, center = row["Link"], row["Band"], row["Center Frequency"]

    if pd.isna(center):
        continue

    ranges = LINK_BANDS[link].get(band)

    if ranges is None:
        print(
            f"WARNING: {row['Mission Name']} - {band} band is not defined "
            f"for {link} (row will not be plotted)"
        )
        continue

    if not in_any_range(center, ranges):
        allowed = ", ".join(f"{lo}-{hi}" for lo, hi in ranges)
        print(
            f"WARNING: {row['Mission Name']} - {center} MHz is outside "
            f"{band} / {link} ({allowed} MHz)"
        )

# ==========================================================
# PLOT FUNCTION  (one band + one link type per axis)
# ==========================================================

def create_band_plot(ax, band_df, mission, band, link):

    ranges = LINK_BANDS[link][band]
    x_min = min(lo for lo, _ in ranges)
    x_max = max(hi for _, hi in ranges)

    channels = band_df.sort_values(by="Center Frequency").to_dict("records")
    color = LINK_COLOR[link]

    # Shade each allowed sub-range when the band has more than one
    if len(ranges) > 1:
        for lo, hi in ranges:
            ax.axvspan(lo, hi, color="lightgray", alpha=0.35, zorder=0)

    # Stagger annotation boxes so labels for nearby channels don't overlap
    label_offsets = [(8, 45), (8, -45), (8, 75), (8, -75)]

    for i, row in enumerate(channels):
        center = row["Center Frequency"]
        bw = row["Max Bandwidth"]
        start_freq = center - (bw / 2)

        # All channels share a single row (y = 0)
        ax.barh(
            y=0, width=bw, left=start_freq, height=0.8,
            color=color, edgecolor="black", linewidth=1.5, zorder=3
        )

        ax.axvline(center, color="black", linestyle="--", linewidth=1)

        ax.annotate(
            f"{center:.3f} MHz\nBW={bw:.4f}",
            xy=(center, 0),
            xytext=label_offsets[i % len(label_offsets)],
            textcoords="offset points",
            ha="left", va="center", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.30", facecolor="white", edgecolor="gray"),
            arrowprops=dict(arrowstyle="->", color="gray"),
            zorder=4
        )

    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([])

    ax.set_xlim(x_min, x_max)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel(LINK_SHORT[link])

    ax.grid(True, axis="x", linestyle="--", alpha=0.4)

    ax.set_title(
        f"{mission} - {BAND_LABEL[band]}\n{link}",
        fontsize=12, fontweight="bold"
    )



# ==========================================================
# BUILD ONE FIGURE FOR A MISSION
# ==========================================================

def build_mission_figure(mission):
    """One subplot per (link, band) that has data. x-axes are NOT shared."""

    mission_df = df[df["Mission Name"] == mission]

    panels = []  # (band, link, subset_df)
    for link in LINK_ORDER:
        for band in BAND_ORDER:
            if band not in LINK_BANDS[link]:
                continue
            subset = mission_df[
                (mission_df["Band"] == band)
                & (mission_df["Link"] == link)
                & mission_df["Center Frequency"].notna()
                & mission_df["Max Bandwidth"].notna()
            ]
            if not subset.empty:
                panels.append((band, link, subset))

    if not panels:
        print(f"\nNo supported bands found for {mission}")
        return None

    print(f"\nGenerating plots for {mission}")
    for band, link, _ in panels:
        print(f"  {band:<4} {link}")

    fig, axes = plt.subplots(
        len(panels), 1,
        figsize=(11, 4.0 * len(panels)),
        sharex=False
    )
    if len(panels) == 1:
        axes = [axes]

    for ax, (band, link, subset) in zip(axes, panels):
        create_band_plot(ax, subset, mission, band, link)

    fig.suptitle(
        f"{mission} Frequency Spectrum Utilization",
        fontsize=18, fontweight="bold"
    )
    fig.tight_layout(pad=1.0, w_pad=0.5, h_pad=2.5)
    fig.subplots_adjust(left=0.08, right=0.95, top=0.93 if len(panels) > 2 else 0.88)

    return fig


# ==========================================================
# ALL-MISSIONS PLOT  (one figure per link + band, every mission on it)
# ==========================================================

# False: every mission's channels share one row, colored by mission.
# True : one row per mission (mission names on the y-axis).
SEPARATE_ROW_PER_MISSION = False


def create_all_missions_plot(ax, band, link, band_df, mission_colors):

    ranges = LINK_BANDS[link][band]
    x_min = min(lo for lo, _ in ranges)
    x_max = max(hi for _, hi in ranges)

    missions_here = sorted(band_df["Mission Name"].unique())
    row_of = {m: i for i, m in enumerate(missions_here)}

    if len(ranges) > 1:
        for lo, hi in ranges:
            ax.axvspan(lo, hi, color="lightgray", alpha=0.35, zorder=0)

    label_offsets = [(8, 40), (8, -40), (8, 75), (8, -75), (8, 110), (8, -110)]
    channels = band_df.sort_values(by="Center Frequency").to_dict("records")

    for i, row in enumerate(channels):
        mission = row["Mission Name"]
        center = row["Center Frequency"]
        bw = row["Max Bandwidth"]
        y = row_of[mission] if SEPARATE_ROW_PER_MISSION else 0

        # Semi-transparent so overlapping missions remain visible
        ax.barh(
            y=y, width=bw, left=center - bw / 2, height=0.8,
            color=mission_colors[mission], alpha=0.75,
            edgecolor="black", linewidth=1.2, zorder=3
        )

        ax.axvline(center, color=mission_colors[mission],
                   linestyle="--", linewidth=1, alpha=0.8)

        if SEPARATE_ROW_PER_MISSION:
            offset = (8, 18)
        else:
            offset = label_offsets[i % len(label_offsets)]

        ax.annotate(
            f"{mission}\n{center:.3f} MHz",
            xy=(center, y),
            xytext=offset,
            textcoords="offset points",
            ha="left", va="center", fontsize=7,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=mission_colors[mission]),
            arrowprops=dict(arrowstyle="->", color="gray"),
            zorder=4
        )

    if SEPARATE_ROW_PER_MISSION:
        ax.set_yticks(range(len(missions_here)))
        ax.set_yticklabels(missions_here)
        ax.set_ylim(-0.8, len(missions_here) - 0.2)
    else:
        ax.set_ylim(-2.5, 2.5)
        ax.set_yticks([])

    ax.set_xlim(x_min, x_max)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel(LINK_SHORT[link])
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)

    ax.set_title(
        f"All Missions - {BAND_LABEL[band]}\n{link}",
        fontsize=13, fontweight="bold"
    )


    # Legend: mission + its occupied BW in this band
    handles = []
    for m in missions_here:
        m_bw = band_df.loc[band_df["Mission Name"] == m, "Max Bandwidth"].sum()
        handles.append(
            plt.Rectangle((0, 0), 1, 1, facecolor=mission_colors[m],
                          edgecolor="black", alpha=0.75,
                          label=f"{m} ({m_bw:.4f} MHz)")
        )
    ax.legend(
        handles=handles, title="Missions",
        loc="upper left", bbox_to_anchor=(1.07, 1.0),
        fontsize=8, title_fontsize=9
    )


def build_all_missions_figures():
    """One figure per (link, band) containing every mission that uses it."""

    all_missions = sorted(df["Mission Name"].unique())
    # tab10 gives more distinct colors; fall back to tab20 for many missions
    cmap = plt.get_cmap("tab10" if len(all_missions) <= 10 else "tab20")
    mission_colors = {m: cmap(i % cmap.N) for i, m in enumerate(all_missions)}

    figures = []

    for link in LINK_ORDER:
        for band in BAND_ORDER:
            if band not in LINK_BANDS[link]:
                continue

            band_df = df[
                (df["Band"] == band)
                & (df["Link"] == link)
                & df["Center Frequency"].notna()
                & df["Max Bandwidth"].notna()
            ]

            if band_df.empty:
                continue

            n_missions = band_df["Mission Name"].nunique()
            print(f"  {band:<4} {link}  ({n_missions} mission(s))")

            fig, ax = plt.subplots(figsize=(13, 5.5))
            create_all_missions_plot(ax, band, link, band_df, mission_colors)

#            fig.suptitle(
#                "MoonBase Frequency Spectrum Utilization - All Missions",
#                fontsize=16, fontweight="bold"
#            )
            fig.subplots_adjust(left=0.07, right=0.68, top=0.80, bottom=0.12)
            figures.append(fig)

    if not figures:
        print("\nNo plottable data found.")

    return figures


# ==========================================================
# MAIN LOOP
# ==========================================================

while True:

    missions = sorted(df["Mission Name"].unique())

    print("\nAvailable Missions:\n")
    print("0  : Exit")
    print("00 : Plot All Missions (one figure per band/link, all missions combined)\n")

    for idx, mission in enumerate(missions, start=1):
        print(f"{idx}: {mission}")

    selection = input("\nEnter mission number (0=Exit, 00=Plot All): ").strip()

    if selection == "0":
        print("\nExiting MoonBase Spectrum Usage Tool.")
        break

    figures = []

    if selection == "00":
        print("\nGenerating combined plots for all missions")
        figures = build_all_missions_figures()
    else:
        try:
            mission_index = int(selection)
        except ValueError:
            print("\nInvalid selection.")
            continue

        if mission_index < 1 or mission_index > len(missions):
            print(f"\nPlease enter a value between 1 and {len(missions)}.")
            continue

        fig = build_mission_figure(missions[mission_index - 1])
        if fig is not None:
            figures.append(fig)

    if figures:
        plt.show()          # shows all figures at once

    for fig in figures:
        plt.close(fig)

print("\nDone.")