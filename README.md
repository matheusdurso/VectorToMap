# 🗺️ VectorToMap - QGIS Plugin

**VectorToMap** é um plugin para QGIS desenvolvido para automatizar a criação de layouts de impressão (Print Layouts) a partir de camadas vetoriais. Ele elimina o trabalho repetitivo de configurar mapas individualmente, permitindo gerar centenas de páginas padronizadas em segundos.

---

## ✨ Funcionalidades

* **Geração Multi-páginas:** Crie uma página por feição ou agrupe várias feições usando um campo de "Atlas".
* **Preview em Tempo Real:** Visualize o design técnico antes de processar toda a camada.
* **🛑 Interrupção Segura de Processamento:**
    * O plugin permite interromper o processamento a qualquer momento clicando no botão **Cancelar**. 
    * O motor de renderização será encerrado com segurança, mantendo a janela aberta para ajustes sem travar o QGIS.
* **Escala Inteligente:**
    * **Auto-escala:** Ajuste automático à geometria com trava de segurança para pontos únicos.
    * **Escala Fixa:** Padrões cartográficos (ex: 1:10.000, 1:25.000) selecionáveis via menu.
* **Exibição de Atributos:** Escolha entre **Modo Formulário (HTML)** para um resumo limpo ou **Modo Individual** para rótulos em linha.
* **Presets de Design:** Formatos otimizados (75% da altura ou Quadrado) para folhas de A4 a A0.

---

## 🚀 Como Usar

1.  **Selecione a Camada:** Escolha a camada vetorial no menu suspenso.
2.  **Escolha os Atributos:** Marque os campos que deseja exibir no mapa.
3.  **Configure o Layout:** Defina o tamanho da página (A4 a A0), orientação e o preset de design.
4.  **Agrupamento:** Selecione um campo no "Group by" para organizar as feições por página.
5.  **Render Preview:** Use para validar o visual da primeira página antes de gerar o arquivo final.
6.  **Gerar:** Clique em **OK**. Acompanhe o progresso pela barra dedicada.
    * **Precisa parar?** Clique em **Cancelar** para abortar o processo se notar algum erro ou se o volume de dados for muito grande.

---

## 🛠️ Instalação

1.  Baixe a pasta do plugin.
2.  Cole-a no diretório de plugins do seu QGIS:
    * **Windows:** `%AppData%\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
    * **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
3.  Abra o QGIS, vá em **Complementos > Gerenciar e Instalar Complementos** e ative o **VectorToMap**.

---

## 💻 Requisitos

* **QGIS:** 3.x ou superior.
* **PyQt5:** (Incluso na instalação padrão do QGIS).

---

## 👤 Autor

* **Matheus Durso** - *Desenvolvimento e Idealização*

---