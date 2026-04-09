# 🗺️ VectorToMap - QGIS Plugin

🎉 **VERSION 3.0: ALL PRO FEATURES ARE NOW 100% FREE AND OPEN-SOURCE!** 🎉

**VectorToMap** is a professional QGIS tool designed to automate the mass generation of Print Layouts. It transforms complex vector data into hundreds of standardized map pages in seconds, making it ideal for inventories, field inspections, and cartographic reports.

---

## 🇺🇸 English Documentation

### ✨ Key Features

* **🌟 Professional Templates (.qpt):** Load built-in native layout templates or import your custom corporate designs. The engine preserves your layout and injects the dynamic maps.
* **🖨️ Multi-Format Export:** Bypass the QGIS layout manager and export hundreds of maps directly to **PDF (multi-page), PNG, JPG, and SVG** (with editable paths).
* **🧮 Data-Defined Overrides (DDO):** Use QGIS SQL expressions (ε) to dynamically control map scales, margins, and complex Atlas grouping based on attribute values.
* **📐 Smart Decorations:** Auto-generate Coordinate Grids, North Arrows, Scale Bars, Legends, and Overview (Locator) Maps tailored to each page.
* **✨ Transparent Backgrounds:** Export maps and pages with alpha channel transparency (perfect for PNG/SVG overlays).
* **🚀 High Performance & Smart Grouping:** Optimized database queries (`QgsFeatureRequest`) and ultra-fast unique value processing for Atlas-style map books.
* **🛡️ Advanced Layer Management:** Cleanly isolates features using temporary memory layers without cluttering your main project. Full support for locking layer visibility and styles per page.
* **👁️ Real-Time Preview:** Lightning-fast in-memory rendering engine to validate your design before final processing, complete with a dedicated progress bar.
* **🛑 Safe Abort & Memory Management:** Functional **Cancel** button that safely stops the rendering engine without freezing the QGIS interface. Uses Python's Garbage Collector (`gc`) and `sip` object cleanup.
* **🎨 Attribute Display Modes:** Form Mode (HTML block) or Individual Mode (inline technical labels with automatic size adjustment).

### 🚀 How to Use

1. **Vector Layer:** Select your source layer from the dropdown menu.
2. **Attribute Selection:** Check the table fields you want to display on the layout.
3. **Technical Setup:** Define the page size, orientation, and choose a visual preset or a `.qpt` Template.
4. **Decorations:** Enable Grids, Legends, North Arrows, or Locator Maps from the UI.
5. **Grouping (Optional):** Select a "Group by" field or write an SQL expression to generate maps by neighborhoods, owners, etc.
6. **Render Preview:** Click **Preview** to generate a technical snapshot of the first page.
7. **Processing:** Click **Export** to save directly to disk (PDF/PNG/SVG) or **OK** to open the generated layouts in the QGIS Layout Designer.

---

## 🇧🇷 Documentação em Português

### ✨ Funcionalidades

* **🌟 Templates Profissionais (.qpt):** Carregue templates nativos já inclusos ou importe seus layouts corporativos personalizados. O motor preserva seu design original e injeta os mapas dinamicamente.
* **🖨️ Exportação Multi-Formato:** Pule o gerenciador de layouts do QGIS e exporte centenas de mapas diretamente para **PDF (múltiplas páginas), PNG, JPG e SVG** (com vetores editáveis).
* **🧮 Expressões Dinâmicas (DDO):** Use SQL do QGIS (ε) para controlar dinamicamente escalas, margens de respiro e agrupamentos complexos no Atlas com base na tabela de atributos.
* **📐 Decorações Inteligentes:** Geração automática e adaptativa de Grades de Coordenadas, Rosas dos Ventos, Escalas, Legendas e Mapas de Localização (Overview).
* **✨ Fundos Transparentes:** Exporte mapas e pranchas com canal alfa (transparência), ideal para sobreposições em PNG e SVG.
* **🚀 Alta Performance e Agrupamento:** Consultas otimizadas via banco de dados (`QgsFeatureRequest`) para geração de cadernos de mapas (estilo Atlas) ultrarrápidos.
* **🛡️ Gestão Avançada de Camadas:** Isola feições de forma limpa usando camadas em memória, sem poluir o projeto. Suporte total para travar a visibilidade e os estilos das camadas por página.
* **👁️ Preview em Tempo Real:** Motor de renderização para validar o design antes do processamento final, com barra de progresso dedicada.
* **🛑 Interrupção Segura:** Botão **Cancelar** funcional que interrompe o motor com segurança. Implementação de *Garbage Collector* (`gc`) para garantir estabilidade com milhares de feições.
* **🎨 Modos de Exibição de Atributos:** Modo Formulário (bloco HTML) ou Modo Individual (rótulos independentes com ajuste contra sobreposição).

### 🚀 Como Usar

1. **Camada Vetorial:** Selecione a camada de origem no menu suspenso.
2. **Seleção de Atributos:** Marque os campos da tabela que aparecerão no layout impresso.
3. **Configuração Técnica:** Defina o tamanho da página, orientação e escolha um Preset visual ou um Template `.qpt`.
4. **Decorações:** Ative Grades, Legendas, Rosas dos Ventos ou Mapas de Localização diretamente na interface.
5. **Agrupamento (Opcional):** Selecione um campo ou crie uma expressão SQL em "Agrupar" para gerar mapas por bairros, proprietários, etc.
6. **Preview:** Clique em **Preview** para validar o design da primeira página na tela.
7. **Processamento:** Clique em **Exportar** para salvar direto no disco (PDF/PNG/SVG) ou em **OK** para abrir os layouts no Gerenciador do QGIS.

---

## 🛠️ Installation / Instalação

1. Download the `vector_to_map` plugin folder. / *Baixe a pasta do plugin.*
2. Paste it into your QGIS plugins directory: / *Cole-a no diretório de plugins do seu perfil QGIS:*
   * **Windows:** `%AppData%\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   * **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
   * **MacOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
3. In QGIS, go to **Plugins > Manage and Install Plugins** and enable **VectorToMap**. / *No QGIS, vá em **Complementos > Gerenciar e Instalar Complementos** e ative o plugin.*

---

## 💻 Requirements / Requisitos

* **QGIS:** 3.22 LTR or higher / *ou superior* (Supports QGIS 4.0 / Qt6).
* **Dependencies / Dependências:** `PyQt5`/`PyQt6`, `sip`, and `gc` (Included in the QGIS Python environment / *Inclusos no ambiente Python do QGIS*).

---

## 👤 Author / Autor

* **Matheus Durso** - *Software Architecture & Development / Desenvolvimento e Arquitetura de Software*