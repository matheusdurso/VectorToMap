# 🗺️ VectorToMap - QGIS Plugin

**VectorToMap** é uma ferramenta profissional para QGIS desenvolvida para automatizar a geração em massa de layouts de impressão (*Print Layouts*). Ele transforma dados vetoriais complexos em centenas de páginas padronizadas em segundos, ideal para inventários, vistorias e relatórios cartográficos.

---

## ✨ Funcionalidades

* **🚀 Alta Performance:** * Consultas otimizadas via banco de dados (Geopackage/PostGIS) usando `QgsFeatureRequest`.
    * Processamento inteligente de valores únicos para agrupamentos ultrarrápidos.
* **📂 Geração Multi-páginas:** Crie uma página por feição individual ou agrupe múltiplas feições automaticamente usando um campo de "Atlas".
* **👁️ Preview em Tempo Real:** * Motor de renderização em memória para validar o design antes do processamento final.
    * Barra de progresso dedicada para feedback visual instantâneo.
* **🛑 Interrupção Segura (Abort):** * Botão **Cancelar** funcional que interrompe o motor de renderização com segurança, sem travar a interface do QGIS.
* **🛡️ Gestão de Memória:** * Implementação de *Garbage Collector* (`gc`) e limpeza de objetos `SIP` (C++) para garantir estabilidade em projetos com milhares de feições.
* **📏 Escala Cartográfica:**
    * **Auto-escala:** Ajuste dinâmico à geometria com proteção para pontos únicos.
    * **Escala Fixa:** Padrões técnicos (1:1.000 a 1:500.000) selecionáveis.
* **🎨 Modos de Exibição:** * **Modo Formulário:** Atributos organizados em bloco HTML limpo.
    * **Modo Individual:** Rótulos técnicos em linha com ajuste automático de tamanho.
* **📐 Presets de Design:** Formatos otimizados (75% da altura ou Quadrado) compatíveis com folhas de **A4 a A0**.

---

## 🚀 Como Usar

1. **Camada Vetorial:** Selecione a camada de origem no menu suspenso.
2. **Seleção de Atributos:** Marque os campos da tabela que aparecerão no layout.
3. **Configuração Técnica:** Defina tamanho da página, orientação (Retrato/Paisagem) e o preset visual.
4. **Agrupamento (Opcional):** Selecione um campo em "Group by" para gerar mapas por bairros, proprietários ou categorias.
5. **Render Preview:** Clique para gerar uma prévia técnica da primeira página.
6. **Processamento:** Clique em **OK**. 
    * **Dica:** Se notar algo errado durante a geração de muitas páginas, clique em **Cancelar** para interromper o processo imediatamente.

---

## 🛠️ Instalação

1. Baixe a pasta do plugin `vector_to_map`.
2. Cole-a no diretório de plugins do seu perfil QGIS:
   * **Windows:** `%AppData%\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   * **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
   * **MacOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
3. No QGIS, vá em **Complementos > Gerenciar e Instalar Complementos** e ative o **VectorToMap**.

---

## 💻 Requisitos

* **QGIS:** 3.22 LTR ou superior.
* **Dependências:** `PyQt5`, `sip` e `gc` (Inclusos no ambiente Python do QGIS).

---

## 👤 Autor

* **Matheus Durso** - *Desenvolvimento e Arquitetura de Software*

---