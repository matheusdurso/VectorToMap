# 🗺️ VectorToMap - QGIS Plugin

🎉 **VERSION 3.8.6.1: ALL PRO FEATURES ARE 100% FREE AND OPEN-SOURCE!** 🎉

**VectorToMap** is a professional QGIS tool designed to automate the mass generation of Print Layouts. It transforms complex vector data into hundreds of standardized map pages in seconds, making it ideal for inventories, field inspections, and cartographic reports.

---

## 🇺🇸 English Documentation

### ✨ Key Features

* **🌟 Professional Templates (.qpt):** Load built-in native layout templates or import your custom corporate designs. The engine features robust XML sanitization (via `QDomDocument`) to automatically clean corrupted templates and remove "ghost" maps. It preserves your layout and injects the dynamic maps, including support for auto-text substitution via `["Column_Name"]` syntax and native QGIS expressions `[% %]`.
* **🧩 Smart Template Image Resolver:** Automatically converts relative image paths (`./logo.png`) to absolute paths inside `.qpt` templates, ensuring corporate logos, watermarks, and custom SVGs are always perfectly rendered across different computers.
* **🖨️ Multi-Format Export:** Bypass the QGIS layout manager and export hundreds of maps directly to **PDF (multi-page), PNG, JPG, and SVG** (with editable paths).
* **🎨 Native Map Themes Support:** Fully integrated with QGIS visibility presets. The main map item can strictly follow a selected Map Theme, syncing instantly with the Live Preview engine. The plugin features dynamic UI state management that automatically locks conflicting layer isolation and feature filtering tools when a theme is active, ensuring a foolproof rendering pipeline.
* **🧮 Data-Defined Overrides (DDO):** Use QGIS SQL expressions (ε) to dynamically control map scales, margins, and complex Atlas grouping based on attribute values.
* **📐 Smart Decorations:** Auto-generate Coordinate Grids, North Arrows, Scale Bars, Legends, and Overview (Locator) Maps tailored to each page. **Legends are fully compatible with QGIS 4's Lazy Loading architecture**, ensuring accurate layer filtering. Overview maps feature dynamic relative Zoom Out (2x-25x) and fixed global framing.
* **✨ Transparent Backgrounds:** Export maps and pages with alpha channel transparency (perfect for PNG/SVG overlays).
* **🚀 High Performance & Smart Grouping:** Optimized database queries (`QgsFeatureRequest`) and ultra-fast unique value processing with intelligent UI event throttling and advanced Memory Garbage Collection (`gc.collect`) for massive batch exports.
* **🌐 Smart CRS Reprojection:** Seamlessly handles layers and projects with different Coordinate Reference Systems (CRS). If the active project lacks a defined CRS, the engine **intelligently falls back to the vector layer's CRS** for accurate scale calculation. It also features a robust fallback mechanism (`QgsCsException` protection) to prevent crashes if geometries fall outside the projection domain, and smartly adapts map padding for both geographic (degrees) and projected (meters) systems.
* **🛡️ Rock-Solid Stability:** Cleanly isolates features using temporary memory layers without cluttering your project. Features foolproof UI signal handling, safe layout deletion (`deleteLater`), and 100% secure "Ghost Layer" exorcism.
* **⚙️ Optimized CI/CD Pipeline:** Automated security scanning (SAST), PII sanitization, and a streamlined DevSecOps build process that automatically excludes test suites from the final package, resulting in a lighter and cleaner plugin download.
* **🚨 Smart Error Handling:** Optional and anonymous automatic crash reporting via Sentry to help improve the plugin continuously.
* **👁️ Real-Time Preview:** Lightning-fast in-memory rendering engine to validate your design before final processing, complete with a dedicated progress bar.
* **🛑 Safe Abort & Memory Management:** Functional **Cancel** button that safely stops the rendering engine without freezing the QGIS interface.
* **🎨 Attribute Display Modes:** Form Mode (HTML block) or Individual Mode (inline technical labels with automatic size adjustment).
* **🌍 Multi-Language Support (i18n):** Fully translated interface available in English, Spanish, French, German, Italian, Russian, Chinese, and Portuguese.

### 🚀 How to Use

1. **Vector Layer:** Select your source layer from the dropdown menu.
2. **Attribute Selection:** Check the table fields you want to display on the layout.
3. **Technical Setup:** Define the page size, orientation, and choose a visual preset or a `.qpt` Template. *You can also enable a Map Theme to govern layer visibility.*
4. **Decorations:** Enable Grids, Legends, North Arrows, or Locator Maps from the UI.
5. **Grouping (Optional):** Select a "Group by" field or write an SQL expression to generate maps by neighborhoods, owners, etc.
6. **Render Preview:** Click **Preview** to generate a technical snapshot of the first page.
7. **Processing:** Click **Export** to save directly to disk (PDF/PNG/SVG) or **OK** to open the generated layouts in the QGIS Layout Designer.

---

## 🇧🇷 Documentação em Português

### ✨ Funcionalidades

* **🌟 Templates Profissionais (.qpt):** Carregue templates nativos já inclusos ou importe seus layouts corporativos personalizados. O motor conta com sanitização robusta de XML (via `QDomDocument`) para limpar automaticamente templates corrompidos e remover mapas "fantasmas". Ele preserva seu design original e injeta os mapas dinamicamente, suportando substituição inteligente de textos com a sintaxe `["Nome_da_Coluna"]` e expressões do QGIS `[% %]`.
* **🧩 Resolvedor Inteligente de Imagens:** Converte automaticamente caminhos relativos de imagens (`./logo.png`) para caminhos absolutos dentro de templates `.qpt`, garantindo que logotipos corporativos, marcas d'água e SVGs personalizados sejam sempre renderizados perfeitamente em diferentes computadores.
* **🖨️ Exportação Multi-Formato:** Pule o gerenciador de layouts do QGIS e exporte centenas de mapas diretamente para **PDF (múltiplas páginas), PNG, JPG e SVG** (com vetores editáveis).
* **🎨 Suporte Nativo a Temas de Mapa:** Integração completa com os presets de visibilidade do QGIS. O quadro do mapa principal segue rigorosamente o Tema selecionado, sincronizando em tempo real com o motor de Preview. A interface possui gestão de estado dinâmica que bloqueia ferramentas conflitantes (como o filtro de feições e isolamento de camadas) quando um tema está ativo, garantindo uma renderização à prova de falhas e sem ambiguidades.
* **🧮 Expressões Dinâmicas (DDO):** Use SQL do QGIS (ε) para controlar dinamicamente escalas, margens de respiro e agrupamentos complexos no Atlas com base na tabela de atributos.
* **📐 Decorações Inteligentes:** Geração automática e adaptativa de Grades de Coordenadas, Rosas dos Ventos, Escalas, Legendas e Mapas de Localização (Overview). **As legendas possuem suporte nativo à arquitetura Lazy Loading do QGIS 4**, garantindo a exclusão cirúrgica de camadas invisíveis. O mapa de localização possui opções de Zoom Out relativo dinâmico (2x a 25x) ou enquadramento global fixo.
* **✨ Fundos Transparentes:** Exporte mapas e pranchas com canal alfa (transparência), ideal para sobreposições em PNG e SVG.
* **🚀 Alta Performance e Agrupamento:** Consultas otimizadas via banco de dados (`QgsFeatureRequest`) para geração de cadernos de mapas ultrarrápidos. Conta com controle inteligente de eventos de interface e Limpeza de Memória (*Garbage Collection*) avançada para lotes gigantes.
* **🌐 Reprojeção Inteligente de SRC:** Lida perfeitamente com camadas e projetos em diferentes Sistemas de Referência de Coordenadas (SRC). **Se o projeto estiver sem SRC definido, o motor utiliza o SRC da camada vetorial como fallback** para cálculos precisos de escala. Possui um mecanismo de segurança avançado (proteção contra `QgsCsException`) que evita travamentos de domínio de projeção, e adapta inteligentemente as margens de respiro para geometrias pontuais em graus ou metros.
* **🛡️ Estabilidade Blindada:** Isola feições de forma limpa usando camadas em memória. Traz interface à prova de travamentos, deleção segura de layouts (`deleteLater`) e "exorcismo" 100% seguro de Camadas Fantasmas.
* **⚙️ Pipeline CI/CD Otimizado:** Varredura de segurança automatizada (SAST), sanitização de PII e um processo de *build* DevSecOps aprimorado que exclui as suítes de testes do pacote final, resultando em um download mais leve e limpo do plugin.
* **🚨 Tratamento Inteligente de Erros:** Integração opcional e anônima de relatórios de falhas via Sentry para melhoria contínua.
* **👁️ Preview em Tempo Real:** Motor de renderização para validar o design antes do processamento final, com barra de progresso dedicada.
* **🛑 Interrupção Segura:** Botão **Cancelar** funcional que interrompe o motor com segurança e não congela o QGIS.
* **🎨 Modos de Exibição de Atributos:** Modo Formulário (bloco HTML) ou Modo Individual (rótulos independentes com ajuste contra sobreposição).
* **🌍 Suporte Multilíngue (i18n):** Interface totalmente traduzida para Português, Inglês, Espanhol, Francês, Alemão, Italiano, Russo e Chinês.

### 🚀 Como Usar

1. **Camada Vetorial:** Selecione a camada de origem no menu suspenso.
2. **Seleção de Atributos:** Marque os campos da tabela que aparecerão no layout impresso.
3. **Configuração Técnica:** Defina o tamanho da página, orientação e escolha um Preset visual ou um Template `.qpt`. *Você também pode ativar um Tema de Mapa para ditar a visibilidade das camadas.*
4. **Decorações:** Ative Grades, Legendas, Rosas dos Ventos ou Mapas de Localização diretamente na interface.
5. **Agrupamento (Opcional):** Selecione um campo ou crie uma expressão SQL em "Agrupar" para gerar mapas por bairros, proprietários, etc.
6. **Preview:** Clique em **Preview** para validar o design da primeira página na tela.
7. **Processamento:** Clique em **Exportar** para salvar direto no disco (PDF/PNG/SVG) ou em **OK** para abrir os layouts no Gerenciador do QGIS.

---

## 🛠️ Installation / Instalação

1. Download the `vector_to_map` plugin folder. / *Baixe a pasta do plugin.*
2. Paste it into your QGIS plugins directory: / *Cole-a no diretório de plugins do seu perfil QGIS:*
   * **Windows:** `%AppData%\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   * **Linux:** `~/.local/share/QGIS\QGIS3\profiles\default\python\plugins`
   * **MacOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python\plugins`
3. In QGIS, go to **Plugins > Manage and Install Plugins** and enable **VectorToMap**. / *No QGIS, vá em **Complementos > Gerenciar e Instalar Complementos** e ative o plugin.*

---

## 💻 Requirements / Requisitos

* **QGIS:** 3.22 LTR or higher / *ou superior* (Supports QGIS 4.0 / Qt6).
* **Dependencies / Dependências:** `PyQt5`/`PyQt6`, `sip`, and `gc` (Included in the QGIS Python environment / *Inclusos no ambiente Python do QGIS*).

---

## 👤 Author / Autor

* **Matheus Durso N. Caetano** - *Software Architecture & Development / Desenvolvimento e Arquitetura de Software*