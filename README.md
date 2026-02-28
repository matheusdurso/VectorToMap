# 🗺️ VectorToMap (v0.3.1)
**Automated High-Performance Atlas Generation for QGIS**

VectorToMap is a specialized QGIS plugin designed to solve common "clipping" and data overflow issues in automated cartography. Version 0.3.1 introduces critical UX improvements, including real-time progress tracking, safety interruption, and a modernized professional interface.

---

## 🚀 Key Features

* **Real-Time Progress Tracking (v0.3.1)**: Integrated blue-accented Progress Bars for both **Render Preview** (indeterminate) and **Layout Export** (deterministic 0-100%).
* **Safety Abort Mechanism (v0.3.1)**: Allows users to safely interrupt long-running export loops via the "Cancel" button, preventing QGIS freezes and providing native MessageBar feedback.
* **Universal Scaling Engine**: Supports both **Fixed Scales** (e.g., 1:10,000) and **Automatic Scaling**. It mathematically detects the limiting dimension (Width vs. Height) to fit irregular geometries with a 25% safety margin.
* **Balanced 3-Column Layout**: A smart attribute selection panel that automatically distributes fields into three balanced columns, ensuring a clean UI regardless of the dataset size.
* **Modernized UX**: Custom-styled minimalist scrollbars with high-contrast hover effects and professional window management (Maximize/Minimize/Center).
* **Trilingual i18n Support**: Full internationalization for **English**, **Spanish**, and **Portuguese**.

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
1. Download the latest release: `vector_to_map_v0.3.1.zip`.
2. Extract the content into your QGIS plugins directory:
    * **Windows**: `%AppData%\QGIS\QGIS3\profiles\default\python\plugins\vector_to_map\`
3. Restart QGIS and activate **VectorToMap** via **Plugins > Manage and Install Plugins**.

---

## 📜 Changelog (v0.3.1)
* **New**: Integrated **Progress Bars** for Preview and Export operations.
* **New**: Added **Abort/Cancel** functionality to interrupt processing safely.
* **New**: Modernized UI with **Blue Accent** styles and high-contrast scrollbars.
* **Fix**: Resolved duplicate layout generation bug on OK click.
* **Refactor**: Improved signal-slot management to prevent memory leaks during cancelation.

---

## 👤 Author
**Matheus Durso**
* **Master in Data Science** (Nuclio Digital School, Spain)
* **GitHub**: [matheusdurso](https://github.com/matheusdurso)
* **Location**: Governador Valadares, MG, Brazil