# 🗺️ VectorToMap (v0.2.6)
**Automated High-Performance Atlas Generation for QGIS**

VectorToMap is a specialized QGIS plugin developed to solve common "clipping" and "data overflow" issues in automated cartography. Unlike standard "zoom-to-feature" methods, this plugin utilizes a custom-built **Geometric Scaling Engine** to ensure every vector feature is perfectly framed with consistent margins, regardless of its shape or grouping.

---

## 🚀 Key Features

* **Smart Scaling Engine**: Mathematically detects the limiting dimension (Width vs. Height) to frame irregular geometries with a constant 25% safety buffer.
* **Row-Based Data Layout**: Each feature in a group (Grouped Atlas) is rendered in its own horizontal row, ensuring 100% attribute visibility without text wrapping.
* **Geometric Presets**: "Iron-Lock" layout models (75% Height or Square maps) to maintain professional consistency across multi-page documents.
* **Professional UI**: Integrated custom toolbar, window management (Minimize/Maximize support), and manual render preview for handling heavy datasets.
* **Smart Overlap Handling**: Automatically shifts attribute labels over the map area if footer space is exhausted, ensuring no data is lost in high-density groups.

---

## 🧠 Technical Deep Dive: The Scaling Logic

The core of the plugin is a deterministic scaling engine. It calculates the optimal scale by comparing the feature's projected bounding box against the available layout frame dimensions in millimeters.

### The Scaling Formula
To prevent clipping on irregular features, the plugin identifies the most restrictive axis using the following logic:

$$Scale = \max\left(\frac{W_{geo} \cdot f_{unit}}{W_{frame}}, \frac{H_{geo} \cdot f_{unit}}{H_{frame}}\right) \cdot 1.25$$

* $W_{geo}, H_{geo}$: Dimensions of the feature in map units.
* $f_{unit}$: Unit-to-millimeter conversion factor.
* $W_{frame}, H_{frame}$: Target layout item dimensions in millimeters.
* **1.25**: Fixed 25% safety margin to ensure "breathing room" for labels.



---

## 🛠️ Installation

1.  Download the latest release: `vector_to_map_v0.2.6.zip`.
2.  Extract the content into your QGIS plugins directory:
    * **Windows**: `%AppData%\QGIS\QGIS3\profiles\default\python\plugins\`
    * **Linux/Mac**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3.  Restart QGIS and enable **VectorToMap** via the **Plugins > Manage and Install Plugins** menu.

---

## 📜 Changelog (v0.2.6)
* **Feature**: Implemented "One Row Per Feature" logic for individual labels in grouped atlases.
* **Added**: 2mm horizontal safety buffer to prevent internal text wrapping in attribute chips.
* **UI**: Added Minimize/Maximize buttons and custom system toolbar.
* **Fix**: Unified naming conventions and fixed Maranhão/Tocantins scaling issues.

---

## 👤 Author
**Matheus Durso**
* **Master's in Data Science**
* **Email**: matheusdursonc@gmail.com
* **GitHub**: [matheusdurso](https://github.com/matheusdurso)