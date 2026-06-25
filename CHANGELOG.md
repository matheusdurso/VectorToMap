# Changelog
All notable changes to VectorToMap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.8.6.1] - 2026-06-25
### Changed
- Codebase Hygiene & Formatting: Stripped trailing whitespaces, redundant tabs, and accidental indentations from all empty lines across the source files to eliminate Git diff noise, prevent merge conflicts, and strictly adhere to PEP 8 standards.

## [3.8.6] - 2026-06-24
### Added
- Native QGIS Map Themes Support: Complete integration with native QGIS visibility presets, enabling the main map item (`main_map`) to follow a selected project theme during batch exports and layouts.
- Dynamic Theme UI Components: Integrated a new checkbox (`chk_usar_tema`) and combobox (`combo_temas`) that actively monitors the QGIS project's theme collection and updates available presets in real-time without requiring a plugin restart.
- Multilingual Translation Support: Added full translation strings for the new theme-based interface widgets across 7 languages (German, English, Spanish, French, Italian, Russian, and Simplified Chinese).

### Changed
- UI State Conflict Management: Enhanced the interface hierarchy engine to automatically disable and uncheck feature filtering (`chk_filtrar_feicoes`) and layer isolation (`chk_exibir_so_camada_atual`) whenever Map Themes are active, eliminating conflicting visibility instructions and establishing a single source of truth.
- Live Preview Synchronization: Connected the theme selection combobox signals directly to the automated layout rendering pipeline, triggering real-time preview canvas updates upon selection change.

## [3.8.5] - 2026-06-19
### Added
- Smart CRS Fallback: If the active QGIS project lacks a defined Coordinate Reference System (CRS) or has unknown units, the engine now automatically falls back to the selected vector layer's CRS to ensure accurate scale calculation and map framing.

### Fixed
- Legend Bug (QGIS 4): Resolved the *Lazy Loading* issue by initializing the legend item in the layout prior to layer exclusion, ensuring correct filtering.

## [3.8.4] - 2026-06-17
### Added
- Smart Template Image Resolver: Automatically converts relative image paths (`./image.png`) to absolute paths inside `.qpt` templates.

### Security
- DevSecOps Optimization: CI/CD Pipeline (GitHub Actions) configured to exclude the test suite from the final release package.

## [3.8.3] - 2026-06-15
### Added
- Robust XML template parsing via `QDomDocument` to automatically clean corrupted layouts and ghost maps.

### Changed
- Performance Optimization: Improved memory garbage collection (`gc.collect`) ensuring stability in massive batch exports.
- UX/UI: Fortified interface signals with `try...finally` blocks to prevent QGIS freezing.

### Fixed
- Projection Exception (CRS): Added robust fallback mechanism to prevent crashes when geometries fall outside the valid projection domain.

---

# Changelog (Português)
Todas as mudanças notáveis no VectorToMap serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [3.8.6.1] - 2026-06-25
### Modificado
- Higiene e Formatação do Código: Removidos todos os espaços em branco residuais (*trailing whitespaces*), tabulações redundantes e indentações acidentais em linhas vazias nos arquivos fontes do projeto, eliminando ruídos em diffs do Git, mitigando conflitos de merge e consolidando a adesão estrita às diretrizes da PEP 8.

## [3.8.6] - 2026-06-24
### Adicionado
- Suporte Nativo a Temas do QGIS: Integração completa com os presets de visibilidade do QGIS, permitindo que o quadro do mapa principal (`main_map`) siga rigorosamente um tema selecionado do projeto durante a exportação em lote e geração de layouts.
- Componentes Dinâmicos de Interface: Implementação de uma checkbox de ativação (`chk_usar_tema`) e combobox (`combo_temas`) que monitorizam o ecossistema do QGIS e atualizam a lista de temas ativos em tempo real, sem necessidade de reiniciar o complemento.
- Internacionalização de Interface: Inclusão de suporte de tradução completo para os novos elements visuais em 7 idiomas (Alemão, Inglês, Espanhol, Francês, Italiano, Russo e Chinês Simplificado).

### Modificado
- Gestão de Conflitos e Estados de UI: Refatoração do motor de hierarquia da interface para desativar e desmarcar automaticamente o filtro de feições (`chk_filtrar_feicoes`) e o isolamento de camadas (`chk_exibir_so_camada_atual`) quando um tema está ativo, extinguindo ordens contraditórias de renderização e definindo um ponto único de autoridade lógica.
- Sincronização com o Motor de Preview: Vinculação dos gatilhos de alteração de índice da combo de temas diretamente ao renderizador automático de layout, forçando a atualização da pré-visualização em tempo real.

## [3.8.5] - 2026-06-19
### Adicionado
- Fallback Inteligente de SRC: Caso o projeto do QGIS esteja sem sistema de coordenadas (SRC) definido ou com unidades desconhecidas, o motor passa a utilizar automaticamente o SRC da camada vetorial selecionada para garantir o cálculo preciso da escala e do enquadramento do mapa.

### Corrigido
- Bug da Legenda (QGIS 4): Resolvido problema de *Lazy Loading* invertendo a ordem de inicialização do item no layout, garantindo a filtragem correta das camadas.

## [3.8.4] - 2026-06-17
### Adicionado
- Resolvedor Inteligente de Imagens: Converte automaticamente caminhos relativos de imagens (`./imagem.png`) para absolutos dentro de templates `.qpt`.

### Segurança
- Otimização DevSecOps: Pipeline de CI/CD (GitHub Actions) configurada para excluir a suíte de testes do pacote final da release.

## [3.8.3] - 2026-06-15
### Adicionado
- Sanitização robusta de templates XML via `QDomDocument` para limpar mapas fantasmas e layouts corrompidos automaticamente.

### Modificado
- Otimização de Performance: Melhoria na limpeza de memória (`gc.collect`) garantindo estabilidade em exportações de lotes gigantescos.
- UX/UI: Sinais da interface blindados com blocos `try...finally` para evitar o congelamento do QGIS.

### Corrigido
- Exceção de Projeção (CRS): Adicionado mecanismo de fallback robusto para evitar *crash* quando geometrias caem fora do domínio válido da projeção do projeto.