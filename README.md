# 🗺️ VectorToMap (v0.3.0)
**Automated High-Performance Atlas Generation for QGIS**

VectorToMap is a specialized QGIS plugin designed to solve common "clipping" and data overflow issues in automated cartography. Version 0.3.0 represents a major milestone, introducing a professional scaling engine, balanced attribute layouts, and full multilingual support.

---

## 🚀 Key Features

* **Universal Scaling Engine (v0.3.0)**: Supports both **Fixed Scales** (e.g., 1:10,000) and **Automatic Scaling**. It mathematically detects the limiting dimension (Width vs. Height) to fit irregular geometries with a 25% safety margin.
* **Balanced 3-Column Layout (v0.3.0)**: A smart attribute selection panel that automatically distributes fields into three balanced columns, ensuring a clean UI regardless of the dataset size.
* **Trilingual i18n Support (v0.3.0)**: Full internationalization for **English**, **Spanish**, and **Portuguese**. The plugin automatically detects the QGIS locale for a native user experience.
* **Professional Window Management (v0.3.0)**: Added system-level **Maximize/Minimize** buttons and automatic screen centering for improved workflow on high-resolution monitors.
* **Dynamic Page Handling**: Support for A4 through A0 page sizes using dynamic data objects, ensuring high-precision layouts in both Portrait and Landscape orientations.
* **Row-Based Data Reporting**: Renders grouped features in individual horizontal lines, preventing text overlapping and ensuring 100% visibility for complex attribute tables.

---

## 🧠 Technical Deep Dive: The Scaling Logic

The plugin's scaling engine is deterministic. When set to **Auto**, it identifies the most restrictive axis using the following formula:

### The Scaling Formula
$$Scale = \max\left(\frac{W_{geo} \cdot f_{unit}}{W_{frame}}, \frac{H_{geo} \cdot f_{unit}}{H_{frame}}\right) \cdot 1.25$$

* $W_{geo}, H_{geo}$: Feature dimensions in map units.
* $f_{unit}$: Unit conversion factor to millimeters.
* $W_{frame}, H_{frame}$: Layout item dimensions in millimeters.
* **1.25**: Fixed 25% safety margin for label "breathing" room.



---

## 🛠️ Installation & Development

### For Users
1.  Download the latest release: `vector_to_map_v0.3.0.zip`.
2.  Extract the content into your QGIS plugins directory:
    * **Windows**: `%AppData%\QGIS\QGIS3\profiles\default\python\plugins\vector_to_map\`
3.  Restart QGIS and activate **VectorToMap** via **Plugins > Manage and Install Plugins**.

### For Developers
* **Update Translations**: Use `pylupdate5` to scan for new strings and `lrelease` to compile `.qm` files.
* **Recompile Resources**: Run `pyrcc5 -o resources.py resources.qrc`.

---

## 📜 Changelog (v0.3.0)
* **New**: Full **Spanish (es_ES)** translation added.
* **New**: Professional window flags (Maximize/Minimize/Center).
* **Improved**: Smart 3-column attribute distribution logic.
* **Improved**: Refactored scale engine to support **Fixed Scaling** at 1:10,000.
* **Safety**: Added conditional warning for Multi-point geometries to prevent auto-zoom errors.
* **Refactor**: Full PEP 8 compliance and optimized signal-slot connections for faster layer switching.

---

## 👤 Author
**Matheus**
* **Master in Data Science** (Nuclio Digital School, Spain)
* **GitHub**: [matheusdurso](https://github.com/matheusdurso)
* **Location**: Governador Valadares, MG, Brazil