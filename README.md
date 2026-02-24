# VectorToMap: Automated Multi-Page Layout Generator for QGIS

**VectorToMap** is a QGIS plugin designed to automate the production of professional, high-consistency map books and reports from vector features. Unlike the native Atlas tool, it provides rigid geometry presets and a custom scaling engine to ensure that every map page looks identical and fits perfectly within the print frame.

## 🚀 Key Features

* **Dynamic Page Generation**: Automatically creates a print layout with multiple pages based on feature selection or attribute grouping.
* **"Iron-Lock" Geometry Presets**: Choose between **75% Height** or **Square Map** models. The plugin locks the map frame's dimensions and position, preventing QGIS from auto-resizing during zoom operations.
* **Smart Scaling Engine**: Uses a manual calculation logic to find the optimal scale for each feature based on its longest dimension (Width vs. Height).
* **Dual Attribute Modes**:
    * **HTML Form**: Displays attributes in a clean, centralized list using HTML for easy reading.
    * **Individual Labels**: Generates bordered, independent labels with automatic line-breaking and smart placement.
* **Performance Optimization**: Includes a "Manual Render Preview" button and an optional automatic preview toggle to handle complex datasets without lag.

---

## 🛠 Technical Scaling Logic

The plugin solves the "clipping" problem by calculating the scale manually before locking the map item. It applies a **20% safety margin** to ensure features are perfectly centered and visible:

$$Scale = \max\left(\frac{W_{geo}}{W_{frame}}, \frac{H_{geo}}{H_{frame}}\right) \times 1.2$$

---

## 📖 How to Use

1.  **Select Layer**: Choose the vector layer you want to map.
2.  **Grouping**: Select an attribute to group features (Atlas mode) or leave empty to generate one page per feature.
3.  **Choose Layout**: Pick your page size (A4 to A0), orientation, and geometry preset.
4.  **Select Columns**: Check the attributes you want to display in the final layout.
5.  **Preview**: Click **"Render Preview"** to see a live sample of the first feature.
6.  **Generate**: Hit **OK** to create the final multi-page layout in the QGIS Layout Manager.

---

## ⚙ Installation

1.  Download the repository as a `.zip` file.
2.  In QGIS, go to **Plugins > Manage and Install Plugins > Install from ZIP**.
3.  Select the downloaded file and click **Install**.

---

## 👤 Author

* **Matheus Durso** - [GitHub Profile](https://github.com/matheusdurso)