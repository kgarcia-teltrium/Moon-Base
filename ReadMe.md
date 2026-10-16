# MoonBase Spectrum Usage Tool

A Python-based visualization tool for displaying mission spectrum allocations from the MoonBase frequency database.

The tool reads mission frequency assignments from a CSV file and generates frequency spectrum utilization plots for selected missions. It supports all standard RF bands from HF through W-band and calculates spectrum usage statistics for each mission.

---

## Features

- Visualize mission frequency assignments by frequency band
- Support for:
  - HF
  - VHF
  - UHF
  - L
  - S
  - C
  - X
  - Ku
  - Ka
  - V
  - W
- Mission selection menu
- Plot a single mission
- Plot all missions simultaneously
- Spectrum occupancy calculations
- Frequency assignment validation
- Center frequency and bandwidth annotations
- Uplink/Downlink color coding

---

## Requirements

- Python 3.10+
- pandas
- matplotlib

---

## requirements.txt

Create a file named:

```text
requirements.txt
```

with the following contents:

```text
pandas>=2.0.0
matplotlib>=3.8.0
```

---

## Supported Frequency Bands

| Band | Frequency Range (MHz) |
|--------|--------|
| HF | 3 - <30 |
| VHF | 30 - <400 |
| UHF | 400 - <1000 |
| L | 1000 - <2000 |
| S | 2000 - <3000 |
| C | 3000 - <7000 |
| X | 7000 - <12000 |
| Ku | 12000 - <18000 |
| Ka | 18000 - <40000 |
| V | 40000 - <75000 |
| W | 75000 - <110000 |

---

## Configuration

Update the CSV file location inside:

```python
csv_file = r"C:\Users\kgarcia\MoonBase\Moon Base Frequencies(Sheet1).csv"
```

to match the location on your system.

---

## Running the Tool

Activate the virtual environment and run:

```bash
python MoonBaseSpectrumUsage.py
```

---

## Mission Selection Menu

When launched, the tool displays a list of available missions.

Example:

```text
Available Missions:

0  : Exit
00 : Plot All Missions

1: AGM-1
2: BGM-2
3: BM MK-1
4: CAPSTONE-02
5: CLV-1
6: FLIP
7: IM-3
8: VIPER
```

### Options

#### Plot a Single Mission

Enter a mission number:

```text
5
```

This will generate plots for CLV-1 only.

---

#### Plot All Missions

Enter:

```text
00
```

This will generate a separate figure for every mission found in the CSV file.

---

#### Exit

Enter:

```text
0
```

to exit the application.

---

## Plot Information

Each plot contains:

- Frequency assignments
- Center frequency markers
- Bandwidth labels
- Spectrum occupancy statistics
- Uplink/downlink color coding

### Color Legend

| Color | Meaning |
|---------|---------|
| Blue | Uplink / Forward Link |
| Red | Downlink / Return Link |

---

## Troubleshooting

### ModuleNotFoundError

Example:

```text
ModuleNotFoundError: No module named 'pandas'
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### CSV Not Found

Example:

```text
FileNotFoundError
```

Verify that the path specified in:

```python
csv_file
```

matches the location of the CSV file on your machine.

---

### Permission Denied When Activating Virtual Environment

Run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then reactivate:

```powershell
.venv\Scripts\Activate.ps1
```

---

## Author

Kaleb Garcia

MoonBase Spectrum Analysis and Visualization Tool