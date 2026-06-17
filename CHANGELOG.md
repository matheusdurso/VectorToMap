# Changelog
Todas as mudanças notáveis no VectorToMap serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), 
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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