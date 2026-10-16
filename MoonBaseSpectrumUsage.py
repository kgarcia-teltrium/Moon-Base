import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# INPUT FILE
# ==========================================================

# Ensure the CSV file path is correct and accessible. Update the path as needed.

csv_file = r"C:\Users\kgarcia\MoonBase\Moon Base Frequencies(Sheet1).csv"

# ==========================================================
# BAND DEFINITIONS (MHz)
# ==========================================================

BANDS = {
    "HF":  {"min": 3,     "max": 30},
    "VHF": {"min": 30,    "max": 400},
    "UHF": {"min": 400,   "max": 1000},
    "L":   {"min": 1000,  "max": 2000},
    "S":   {"min": 2000,  "max": 3000},
    "C":   {"min": 3000,  "max": 7000},
    "X":   {"min": 7000,  "max": 12000},
    "Ku":  {"min": 12000, "max": 18000},
    "Ka":  {"min": 18000, "max": 40000},
    "V":   {"min": 40000, "max": 75000},
    "W":   {"min": 75000, "max": 110000},
}

# ==========================================================
# READ CSV
# ==========================================================

df = pd.read_csv(csv_file)

df.columns = df.columns.str.strip()

columns_to_strip = [
    "Mission Name",
    "Mission Link Direction",
    "Frequency Band"
]

for col in columns_to_strip:
    df[col] = df[col].astype(str).str.strip()

df["Center Frequency"] = pd.to_numeric(
    df["Center Frequency"],
    errors="coerce"
)

df["Max Bandwidth"] = pd.to_numeric(
    df["Max Bandwidth"],
    errors="coerce"
)

# ==========================================================
# VALIDATE BAND ASSIGNMENTS
# ==========================================================

print("\nChecking frequency assignments...\n")

for _, row in df.iterrows():

    band = row["Frequency Band"]

    if band not in BANDS:
        print(
            f"WARNING: Unknown band '{band}' "
            f"for mission {row['Mission Name']}"
        )
        continue

    center = row["Center Frequency"]

    band_min = BANDS[band]["min"]
    band_max = BANDS[band]["max"]

    if center < band_min or center >= band_max:
        print(
            f"WARNING: {row['Mission Name']} - "
            f"{center} MHz is outside "
            f"{band} band ({band_min}-{band_max} MHz)"
        )

# ==========================================================
# PLOT FUNCTION
# ==========================================================

def create_band_plot(
    ax,
    band_df,
    mission,
    band
):

    band_min = BANDS[band]["min"]
    band_max = BANDS[band]["max"]

    band_width = band_max - band_min

    total_bw = band_df["Max Bandwidth"].sum()

    usage_pct = (
        total_bw / band_width
    ) * 100

    band_df = band_df.sort_values(
        by="Center Frequency"
    )

    channels = band_df.to_dict("records")

    for i, row in enumerate(channels):

        direction = row["Mission Link Direction"]
        center = row["Center Frequency"]
        bw = row["Max Bandwidth"]

        start_freq = center - (bw / 2)

        if (
            "uplink" in direction.lower()
            or "forward" in direction.lower()
        ):
            color = "tab:blue"
        else:
            color = "tab:red"

        # Alternate row shading
        if i % 2 == 0:
            ax.axhspan(
                i - 0.5,
                i + 0.5,
                color="lightgray",
                alpha=0.15,
                zorder=0
            )

        # Allocation
        ax.barh(
            y=i,
            width=bw,
            left=start_freq,
            height=0.8,
            color=color,
            edgecolor="black",
            linewidth=1.5,
            zorder=3
        )

        # Center frequency marker
        ax.axvline(
            center,
            color="black",
            linestyle="--",
            linewidth=1
        )

        # Annotation
        ax.annotate(
            (
                f"{center:.3f} MHz\n"
                f"BW={bw:.4f}"
            ),
            xy=(center, i),
            xytext=(8, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8,
            bbox=dict(
                boxstyle="round,pad=0.30",
                facecolor="white",
                edgecolor="gray"
            ),
            arrowprops=dict(
                arrowstyle="->",
                color="gray"
            )
        )

    ax.set_yticks(range(len(channels)))

    ax.set_yticklabels(
        [
            row["Mission Link Direction"]
            for row in channels
        ]
    )

    ax.set_xlim(
        band_min,
        band_max
    )

    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Direction")

    ax.grid(
        True,
        axis="x",
        linestyle="--",
        alpha=0.4
    )

    ax.set_title(
        f"{mission} {band}-Band Spectrum Usage",
        fontsize=14,
        fontweight="bold"
    )

    ax.text(
        0.99,
        0.98,
        (
            f"{band}-Band Usage\n\n"
            f"Occupied BW: {total_bw:.4f} MHz\n"
            f"Band Width: {band_width:.0f} MHz\n"
            f"Usage: {usage_pct:.6f}%"
        ),
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="lightyellow",
            edgecolor="black"
        )
    )

# ==========================================================
# MAIN LOOP
# ==========================================================

while True:

    missions = sorted(
        df["Mission Name"].unique()
    )

    print("\nAvailable Missions:\n")
    print("0  : Exit")
    print("00 : Plot All Missions\n")

    for idx, mission in enumerate(
        missions,
        start=1
    ):
        print(f"{idx}: {mission}")

    selection = input(
        "\nEnter mission number (0=Exit, 00=Plot All): "
    ).strip()

    # ======================================================
    # EXIT
    # ======================================================

    if selection == "0":

        print(
            "\nExiting MoonBase Spectrum Usage Tool."
        )

        break

    # ======================================================
    # PLOT ALL MISSIONS
    # ======================================================

    if selection == "00":

        figures = []

        for selected_mission in missions:

            mission_df = df[
                df["Mission Name"] == selected_mission
            ]

            used_bands = []

            for band in BANDS:

                if (
                    mission_df["Frequency Band"]
                    .str.upper()
                    .eq(band.upper())
                    .any()
                ):
                    used_bands.append(band)

            if len(used_bands) == 0:
                continue

            print(
                f"\nGenerating plots for "
                f"{selected_mission}"
            )

            fig, axes = plt.subplots(
                len(used_bands),
                1,
                figsize=(10, 3.5 * len(used_bands))
            )

            if len(used_bands) == 1:
                axes = [axes]

            for ax, band in zip(
                axes,
                used_bands
            ):

                band_df = mission_df[
                    mission_df["Frequency Band"]
                    .str.upper()
                    == band.upper()
                ]

                create_band_plot(
                    ax,
                    band_df,
                    selected_mission,
                    band
                )

            fig.suptitle(
                f"{selected_mission} Frequency Spectrum Utilization",
                fontsize=18,
                fontweight="bold"
            )

            fig.tight_layout()

            figures.append(fig)

        # Show ALL figures at once
        plt.show()

        # Cleanup
        for fig in figures:
            plt.close(fig)

        continue

    # ======================================================
    # PLOT ONE MISSION
    # ======================================================

    else:

        try:

            mission_index = int(selection)

            if (
                mission_index < 1
                or mission_index > len(missions)
            ):

                print(
                    f"\nPlease enter a value "
                    f"between 1 and {len(missions)}."
                )

                continue

            missions_to_plot = [
                missions[mission_index - 1]
            ]

        except ValueError:

            print(
                "\nInvalid selection."
            )

            continue

    # ======================================================
    # GENERATE PLOTS
    # ======================================================

    for selected_mission in missions_to_plot:

        mission_df = df[
            df["Mission Name"]
            == selected_mission
        ]

        used_bands = []

        for band in BANDS:

            if (
                mission_df["Frequency Band"]
                .str.upper()
                .eq(band.upper())
                .any()
            ):
                used_bands.append(band)

        if len(used_bands) == 0:

            print(
                f"\nNo supported bands found "
                f"for {selected_mission}"
            )

            continue

        print(
            f"\nGenerating plots for "
            f"{selected_mission}"
        )

        print(
            f"Bands Found: "
            f"{', '.join(used_bands)}"
        )

        fig, axes = plt.subplots(
            len(used_bands),
            1,
            figsize=(10, 3.5 * len(used_bands))
        )

        if len(used_bands) == 1:
            axes = [axes]

        for ax, band in zip(
            axes,
            used_bands
        ):

            band_df = mission_df[
                mission_df["Frequency Band"]
                .str.upper()
                == band.upper()
            ]

            create_band_plot(
                ax,
                band_df,
                selected_mission,
                band
            )

        fig.suptitle(
            f"{selected_mission} Frequency Spectrum Utilization",
            fontsize=18,
            fontweight="bold"
        )

        plt.tight_layout(
            pad=1.0,
            w_pad=0.5,
            h_pad=1.0
        )

        plt.subplots_adjust(
            left=0.10,
            right=0.95,
            top=0.90,
            bottom=0.08
        )

        plt.show()

        plt.close(fig)

print("\nDone.")