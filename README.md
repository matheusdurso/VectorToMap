# VectorToMap (Atlas & Layout) 🗺️

**VectorToMap** é uma ferramenta de automação para QGIS desenvolvida para transformar camadas vetoriais em cadernos de mapas organizados e relatórios técnicos profissionais.

## 🌟 Diferenciais Técnicos
* **Cálculo de Escala Inteligente**: Utiliza o lado dominante do retângulo envolvente para definir o zoom, garantindo que nenhuma parte da geometria seja cortada.
* **Atlas Multi-Páginas Persistente**: Cria um único layout com múltiplas páginas, facilitando a exportação em lote para PDF.
* **Transposição de Atributos**: Converte registros da tabela em formulários verticais legíveis usando renderização HTML.
* **Independência de SRC**: Algoritmo testado para conversão dinâmica entre metros, graus e pés.

## 🚀 Instalação e Uso
1. Baixe o arquivo `.zip` mais recente na aba [Releases](https://github.com/matheusdurso/VectorToMap/releases).
2. No QGIS, vá em `Complementos` > `Gerenciar e Instalar Complementos` > `Instalar a partir do ZIP`.
3. Selecione a camada, abra o plugin pelo menu **Vector to Map** e configure seu layout.

## 🛠️ Reportando Problemas e Sugestões
Para garantir a evolução constante desta ferramenta, utilizamos o **GitHub Issues**. Se você encontrou um erro ou tem uma ideia de nova funcionalidade:

1. Acesse a aba [Issues](https://github.com/matheusdurso/VectorToMap/issues).
2. Clique em **New Issue**.
3. Descreva o problema detalhadamente (se possível, anexe um print do erro ou a camada utilizada).
4. Aguarde o feedback; responderemos o mais breve possível!

---
**Autor:** [Matheus Durso](https://github.com/matheusdurso) – Especialista com mestrado internacional focado em tecnologias digitais e ciência de dados.
**Licença:** GNU GPL v2.