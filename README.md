# 🗺️ VectorToMap (v0.3.2.1)
**Recompiled i18n translations (EN/ES) for layout consistency**
**Automated High-Performance Atlas Generation for QGIS**

VectorToMap is a specialized QGIS plugin designed for high-precision cartography. Version 0.3.2.1 introduces adaptive layout management, featuring side-by-side attribute positioning and smart column balancing to optimize page space.

---

## 🚀 Key Features

* **Adaptive Side-by-Side Layout (v0.3.2.1)**: New 1/3-width form positioning that places HTML attributes alongside individual labels, maximizing space in both Portrait and Landscape.
* **Smart Column Grouping (v0.3.2.1)**: Dynamic attribute distribution for "No Grouping" mode:
    * **Portrait**: 3 or 5 columns depending on the map preset.
    * **Landscape**: 3 or 5 columns optimized for wide-screen viewing.
* **Real-Time Progress Tracking**: Integrated blue-accented Progress Bars for both **Render Preview** and **Layout Export**.
* **Universal Scaling Engine**: Engineering-grade accuracy with 25% safety margins for all geometries.

---

## 🧠 The Scaling & Layout Formula

### Adaptive Layout Logic
$$W_{form} = (W_{page} - 20mm) \cdot 0.33$$
$$W_{labels} = (W_{page} - 20mm) \cdot 0.67$$

### Scaling Formula
$$Scale = \max\left(\frac{W_{geo} \cdot f_{unit}}{W_{frame}}, \frac{H_{geo} \cdot f_{unit}}{H_{frame}}\right) \cdot 1.25$$

---

## 📜 Changelog (v0.3.2.1)
* **New**: Side-by-side layout (1/3 Form vs 2/3 Individual Labels).
* **New**: Context-aware column limits (3/5 columns) based on orientation and map type.
* **Fix**: Unified 75% height layout behavior for Portrait and Landscape.
* **Refactor**: Optimized coordinate calculation for side-by-side rendering.

---

## 👤 Author
**Matheus Durso**
* **Master in Data Science** (Nuclio Digital School, Spain)
* **GitHub**: [matheusdurso](https://github.com/matheusdurso)