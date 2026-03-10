# 🗺️ VectorToMap - QGIS Plugin

**VectorToMap** is a professional QGIS tool designed to automate the mass generation of Print Layouts. It transforms complex vector data into hundreds of standardized map pages in seconds, making it ideal for inventories, field inspections, and cartographic reports.

---

## 🇺🇸 English Documentation

### ✨ Key Features

* **🚀 High Performance & Smart Grouping:** Optimized database queries (`QgsFeatureRequest`) and ultra-fast unique value processing for Atlas-style map books.
* **🛡️ Advanced Layer Management:** Cleanly isolates features using temporary memory layers without cluttering your main project. Full support for locking layer visibility and styles per page.
* **👁️ Real-Time Preview:** Lightning-fast in-memory rendering engine to validate your design before final processing, complete with a dedicated progress bar.
* **🛑 Safe Abort & Memory Management:** Functional **Cancel** button that safely stops the rendering engine without freezing the QGIS interface. Uses Python's Garbage Collector (`gc`) and `sip` object cleanup to guarantee stability even with thousands of features.
* **📏 Cartographic Scaling:** * **Auto-scale:** Dynamic bounding-box adjustment with mathematical protection for single-point geometries.
    * **Fixed Scale:** Selectable technical standards (from 1:1,000 up to 1:1,000,000).
    * **CRS Protection:** Built-in safeguards for layers with missing or custom EPSG definitions.
* **🎨 Attribute Display Modes:** * **Form Mode:** Clean, unified HTML block for all selected attributes.
    * **Individual Mode:** Inline technical labels with automatic size adjustment to prevent overlapping.
* **📐 Page Designs & Presets:** Optimized frame proportions (e.g., 75% height or Square) fully compatible with **A4 to A0** paper sizes and Portrait/Landscape orientations.
* **🔮 Future-Proof:** Fully compatible with QGIS 3.x (Qt5) and the new QGIS 4.x (Qt6).

### 🚀 How to Use

1. **Vector Layer:** Select your source layer from the dropdown menu.
2. **Attribute Selection:** Check the table fields you want to display on the layout.
3. **Technical Setup:** Define the page size, orientation (Portrait/Landscape), and visual preset.
4. **Layer Control:** Choose whether to filter features, isolate the current layer, and lock styles.
5. **Grouping (Optional):** Select a "Group by" field to generate maps by neighborhoods, owners, or categories.
6. **Render Preview:** Click to generate a technical snapshot of the first page.
7. **Processing:** Click **OK** to generate all layouts. 
    * *Tip:* If you notice something wrong during a massive batch generation, click **Cancel** to abort the process safely.

---

## 🇧🇷 Documentação em Português

### ✨ Funcionalidades

* **🚀 Alta Performance e Agrupamento:** Consultas otimizadas via banco de dados (`QgsFeatureRequest`) e processamento inteligente de valores únicos para geração de cadernos de mapas (estilo Atlas) ultrarrápidos.
* **🛡️ Gestão Avançada de Camadas:** Isola feições de forma limpa usando camadas em memória temporárias, sem poluir o projeto principal. Suporte total para travar a visibilidade e os estilos das camadas por página.
* **👁️ Preview em Tempo Real:** Motor de renderização em memória para validar o design antes do processamento final, com barra de progresso dedicada para feedback visual instantâneo.
* **🛑 Interrupção Segura e Gestão de Memória:** Botão **Cancelar** funcional que interrompe o motor de renderização com segurança, sem travar a interface. Implementação de *Garbage Collector* (`gc`) e limpeza de objetos `SIP` (C++) para garantir estabilidade com milhares de feições.
* **📏 Escala Cartográfica:**
    * **Auto-escala:** Ajuste dinâmico à geometria com proteção matemática para pontos únicos.
    * **Escala Fixa:** Padrões técnicos selecionáveis (de 1:1.000 até 1:1.000.000).
    * **Blindagem de CRS:** Proteção nativa para camadas com definições EPSG ausentes ou customizadas.
* **🎨 Modos de Exibição:** * **Modo Formulário:** Atributos organizados em bloco HTML limpo.
    * **Modo Individual:** Rótulos técnicos em linha com ajuste automático de tamanho para evitar sobreposições.
* **📐 Presets de Design:** Formatos otimizados (ex: 75% da altura ou Quadrado) compatíveis com folhas de **A4 a A0**, nas orientações Retrato ou Paisagem.
* **🔮 Preparado para o Futuro:** Totalmente compatível com QGIS 3.x (Qt5) e o novo QGIS 4.x (Qt6).

### 🚀 Como Usar

1. **Camada Vetorial:** Selecione a camada de origem no menu suspenso.
2. **Seleção de Atributos:** Marque os campos da tabela que aparecerão no layout impresso.
3. **Configuração Técnica:** Defina o tamanho da página, orientação e o preset visual.
4. **Controle de Camadas:** Escolha se deseja filtrar as feições, isolar a camada atual e travar os estilos.
5. **Agrupamento (Opcional):** Selecione um campo em "Group by" para gerar mapas por bairros, proprietários, etc.
6. **Render Preview:** Clique para gerar uma prévia técnica da primeira página.
7. **Processamento:** Clique em **OK** para gerar todos os layouts. 
    * *Dica:* Se notar algo errado durante a geração de muitas páginas, clique em **Cancelar** para interromper o processo imediatamente.

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