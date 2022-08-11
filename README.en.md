[Русский](https://github.com/interlark/qdc-converter/blob/main/README.md) | [English](https://github.com/interlark/qdc-converter/blob/main/README.en.md)

<h1>QDC Converter <a href="#"><img width="40px" src="https://user-images.githubusercontent.com/20641837/181224497-52a3bc1b-9e0e-4d12-a40c-da97e6e818ca.svg" alt="Logo" align="left"/></a></h1>

[![Tests](https://github.com/interlark/qdc-converter/actions/workflows/tests.yml/badge.svg)](https://github.com/interlark/qdc-converter/actions/workflows/tests.yml)
[![PyPi version](https://badgen.net/pypi/v/qdc-converter)](https://pypi.org/project/qdc-converter)
[![Supported Python versions](https://badgen.net/pypi/python/qdc-converter)](https://pypi.org/project/qdc-converter)
[![License](https://badgen.net/pypi/license/qdc-converter)](https://github.com/interlark/qdc-converter/blob/main/LICENSE)

Converter of ***.qdc** *(Garmin QuickDraw Contours)* files into ***.csv** *(CSV table)* or ***.grd** *(ESRI ASCII Grid Raster)*

![Screencast](https://user-images.githubusercontent.com/20641837/175391925-eb32664b-ecca-4807-86c0-2fdd1f827125.gif)

## Installation
### Single file build
Download [release](https://github.com/interlark/qdc-converter/releases/latest).

### Install from PyPI
```bash
# CLI
pip install qdc-converter
# CLI + GUI
pip install qdc-converter[gui]
```

## Usage
Base parameters: **-i**, **-o** and **-l**.

* An example of converting folder ```Contours``` which contains ***.qdc** files inside into table ```export_table.csv``` with 3 columns ```X``` *(longitude in decimal degrees)*, ```Y``` *(latitude in decimal degrees)* и  ```Depth(m)``` *(depth in meters)*, using data layer L_**1**:
  ```
  qdc-converter -i "Contours" -o "export_table.csv" -l 1
  ```

* An example of converting folder ```Contours``` which contains ***.qdc** files inside into raster ```export_raster.grd```, using data layer L_**0**:
  ```
  qdc-converter -i "Contours" -o "export_raster.grd" -l 0
  ```
  The result raster could be loaded into many other GIS, like QGIS, etc... and get converted into more readable formats.


## Parameters
```bash
qdc-converter --help
```
```
Usage: qdc-converter [OPTIONS]

  QDC converter.

  Converter of Garmin's QDC files into CSV or GRD.

Options:
  Main parameters:                Key parameters of the converter
    -i, --qdc-folder-path DIRECTORY
                                  Path to folder with
                                  QuickDraw Contours (QDC) inside.  [required]

    -o, --output-path FILE        Path to the result file (*.csv or
                                  *.grd).  [required]

    -l, --layer [0,1,2,3,4,5]     Data layer (0 - Raw user data, 1 -
                                  Recommended).  [0<=x<=5; required]
  Correction parameters:          Corrections
    -dx, --x-correction FLOAT     Correction of X.
    -dy, --y-correction FLOAT     Correction of Y.
    -dz, --z-correction FLOAT     Correction of Z.
  CSV parameters:                 Parameters related to CSV
    -csvd, --csv-delimiter TEXT   CSV delimiter (default ",").
    -csvs, --csv-skip-headers     Do not write header.
    -csvy, --csv-yxz              Change column order from X,Y,Z to Y,X,Z.
  Other parameters:               Other converter parameters
    -st, --singlethreaded         Run converter in a single thread.
    -vc, --validity-codes         Write validity code instead of depth.
    -q, --quite                   "Quite mode"
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

## Convert `.qcc` to `.qdc` files with Android phone
If you have only `.qcc` file, you should convert it to `.qdc` files to use in `qdc-converter`.

1. Install `Garmin ActiveCaptain` Android app.
    > https://play.google.com/store/apps/details?id=com.garmin.android.marine<br/>
    > https://apk.support/download-app/com.garmin.android.marine

2. Launch app, sign up and close it.

2. Copy `.qcc` file to the phone path `/Android/data/com.garmin.android.marine/files/Garmin/esm/internal0/`

3. Launch `Garmin ActiveCaptain` app and wait until it converts the source `.qcc` file to `.qdc` files.
    > The process usually takes less than a minute.

4. Copy folder with `.qdc` files from phone path `/Android/data/com.garmin.android.marine/files/Garmin/esm/internal0/Garmin/Quickdraw/Contours/C/` to your computer.
