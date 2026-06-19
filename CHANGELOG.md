# Changelog
All notable changes to VectorToMap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), 
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [3.8.5] - 2026-06-19
### Adicionado
- Fallback Inteligente de SRC: Caso o projeto do QGIS esteja sem sistema de coordenadas (SRC) definido ou com unidades desconhecidas, o motor passa a utilizar automaticamente o SRC da camada vetorial selecionada para garantir o cálculo preciso da escala e do enquadramento do mapa.

### Corrigido
- Bug da Legenda (QGIS 4): Resolvido problema de *Lazy Loading* invertendo a ordem de inicialização do item no layout, garantindo a filtragem correta das camadas.

## [3.8.4] - 2026-06-17
### Adicionado
- Resolvedor Inteligente de Imagens: Converte automaticamente caminhos relativos (`./imagem.png`) para absolutos dentro de templates `.qpt`.

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