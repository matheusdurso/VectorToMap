# 🗺️ VectorToMap (v0.2.8)
**Automated High-Performance Atlas Generation for QGIS**

VectorToMap é um plugin especializado para QGIS desenvolvido para resolver problemas comuns de "clivagem" (clipping) e transbordamento de dados em cartografia automatizada. Esta versão 0.2.8 foca na robustez da arquitetura, implementando desacoplamento de interface e suporte para internacionalização total.

---

## 🚀 Key Features

* **Smart Scaling Engine**: Detecta matematicamente a dimensão limitante (Largura vs. Altura) para enquadrar geometrias irregulares com uma margem de segurança constante de 25%.
* **Dynamic Page Numbering (v0.2.8)**: Inserção automatizada de numeração de páginas utilizando a variável `[% @layout_page %]` com posicionamento inteligente no canto inferior direito.
* **Global i18n Engine (v0.2.8)**: Suporte completo para internacionalização (Português/Inglês) utilizando chaves técnicas invariantes para evitar quebras de lógica em diferentes idiomas.
* **Row-Based Data Layout**: Renderiza cada feição em sua própria linha horizontal em atlas agrupados, garantindo 100% de visibilidade dos atributos sem sobreposição de texto.
* **Optimized Preview (v0.2.8)**: Motor de pré-visualização com *debounce* de 400ms, equilibrando fluidez na interface e baixo consumo de CPU.
* **Professional UI**: Barra de ferramentas personalizada integrada ao QGIS, gerenciamento avançado de janelas (Minimizar/Maximizar) e renderização manual de preview.



---

## 🧠 Technical Deep Dive: The Scaling Logic

O motor de escala do plugin é determinístico. Ele calcula a escala ideal comparando a caixa delimitadora (*bounding box*) da geometria projetada contra as dimensões do quadro de layout disponíveis.

### The Scaling Formula
Para evitar o corte de feições irregulares, o plugin identifica o eixo mais restritivo usando a seguinte lógica:

$$Scale = \max\left(\frac{W_{geo} \cdot f_{unit}}{W_{frame}}, \frac{H_{geo} \cdot f_{unit}}{H_{frame}}\right) \cdot 1.25$$

* $W_{geo}, H_{geo}$: Dimensões da feição em unidades do mapa.
* $f_{unit}$: Fator de conversão de unidades para milímetros.
* $W_{frame}, H_{frame}$: Dimensões do item de layout em milímetros.
* **1.25**: Margem de segurança fixa de 25% para "respiro" dos rótulos.

---

## 🛠️ Installation & Development

### For Users
1.  Baixe a última release: `vector_to_map_v0.2.8.zip`.
2.  Extraia o conteúdo no diretório de plugins do QGIS:
    * **Windows**: `%AppData%\QGIS\QGIS3\profiles\default\python\plugins\vector_to_map\`
3.  Reinicie o QGIS e ative o **VectorToMap** via menu **Complementos > Gerenciar e Instalar Complementos**.

### For Developers
Este projeto utiliza ferramentas de build para compilação de recursos e interfaces:
* **Recompilar Recursos**: Execute `pyrcc5 -o resources.py resources.qrc`.
* **Build Automatizado**: Suporte para `pb_tool` (requer configuração local).



---

## 📜 Changelog (v0.2.8)
* **Feature**: Implementada numeração automática de páginas em layouts multi-folhas.
* **i18n**: Adicionado suporte para tradução dinâmica via `QTranslator`.
* **Refatoração**: Migração para `currentData()` em ComboBoxes para garantir invariância da lógica em ambientes multilinguagem.
* **Correção de Bug**: Movida a criação de botões dinâmicos para o `initGui` para prevenir `AttributeError` no carregamento.
* **Performance**: Ajuste do timer de preview automático para 400ms.

---

## 👤 Author
**Matheus**
* **Mestre em Ciência de Dados** (Nuclio Digital School, Espanha)
* **GitHub**: [matheusdurso](https://github.com/matheusdurso)
* **Localização**: Governador Valadares, MG, Brasil