# -*- coding: utf-8 -*-
import os
import re
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsReadWriteContext, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemLegend, QgsExpression, QgsExpressionContextUtils,
    QgsLayoutPoint, QgsUnitTypes, NULL, QgsLayoutItemPage
)

class TemplateManager:
    """Gerencia a sanitização, leitura e processamento de templates XML (.qpt)."""

    @staticmethod
    def carregar_template_sanitizado(layout, caminho_qpt, pagina_index):
        """Lê o arquivo, limpa mapas fantasmas, ajusta imagens e garante os IDs do mapa."""
        if not os.path.exists(caminho_qpt): return None, None, []

        nome_original = layout.name()

        with open(caminho_qpt, 'rt', encoding='utf-8') as f:
            template_content = f.read()

        # A OPERAÇÃO FAXINA (DOM)
        doc = QDomDocument()
        doc.setContent(template_content)

        pasta_template = os.path.dirname(caminho_qpt)
        elementos_gerais = doc.elementsByTagName("LayoutItem")

        # PASSO 0: O FIXADOR DE IMAGENS
        for i in range(elementos_gerais.count()):
            pic_el = elementos_gerais.at(i).toElement()
            if pic_el.attribute("type") == "65640":
                caminho_antigo = pic_el.attribute("file")
                if caminho_antigo and not caminho_antigo.startswith("http"):
                    nome_arquivo = caminho_antigo.replace('\\', '/').split('/')[-1]
                    caminho_novo = os.path.join(pasta_template, nome_arquivo)
                    if os.path.exists(caminho_novo):
                        pic_el.setAttribute("file", caminho_novo.replace('\\', '/'))

        # PASSO 1: O EXTERMINADOR DE FANTASMAS
        elementos = doc.elementsByTagName("LayoutItem")
        for i in range(elementos.count() - 1, -1, -1):
            el = elementos.at(i).toElement()
            size_str = el.attribute("size", "0,0,mm")
            is_ghost = False
            try:
                w, h = map(float, size_str.split(',')[:2])
                if w <= 0.1 or h <= 0.1:
                    is_ghost = True
            except Exception:
                pass
            if is_ghost:
                el.parentNode().removeChild(el)

        # PASSO 2: O AVALIADOR DE MAPAS (Garantiando a trava dos IDs corretos)
        elementos = doc.elementsByTagName("LayoutItem")
        mapas_validos = []
        tem_mapa_explicito = False

        for i in range(elementos.count()):
            el = elementos.at(i).toElement()
            if el.attribute("type") == "65639":
                item_id = el.attribute("id")
                if item_id in ["main_map", "overview_map"]:
                    tem_mapa_explicito = True
                try:
                    w, h = map(float, el.attribute("size", "0,0,mm").split(',')[:2])
                    area = w * h
                except:
                    area = 0
                mapas_validos.append({'area': area, 'el': el, 'id': item_id})

        def limpar_memoria_mapa(map_node):
            map_node.setAttribute("keepLayerSet", "1")
            for tag in ["LayerSet", "overviews"]:
                tags = map_node.elementsByTagName(tag)
                for j in range(tags.count()):
                    node = tags.at(j)
                    while node.hasChildNodes():
                        node.removeChild(node.firstChild())

        if tem_mapa_explicito:
            main_achado = False
            overview_achado = False
            for mapa in mapas_validos:
                el = mapa['el']
                item_id = mapa['id']
                is_clone = False
                if item_id == "main_map":
                    if main_achado: is_clone = True
                    else: main_achado = True
                elif item_id == "overview_map":
                    if overview_achado: is_clone = True
                    else: overview_achado = True
                if item_id not in ["main_map", "overview_map"] or is_clone:
                    el.parentNode().removeChild(el)
                else:
                    limpar_memoria_mapa(el)
        else:
            mapas_validos.sort(key=lambda x: x['area'], reverse=True)
            for idx, mapa in enumerate(mapas_validos):
                el = mapa['el']
                if idx == 0:
                    el.setAttribute("id", "main_map")
                    limpar_memoria_mapa(el)
                elif idx == 1:
                    el.setAttribute("id", "overview_map")
                    limpar_memoria_mapa(el)
                else:
                    el.parentNode().removeChild(el)

        # CARREGAMENTO DO TEMPLATE LIMPO NO QGIS
        itens_antes = set(layout.items())
        limpar = (pagina_index == 0)

        layout.loadFromTemplate(doc, QgsReadWriteContext(), clearExisting=limpar)
        layout.setName(nome_original)

        novos_itens = list(set(layout.items()) - itens_antes)
        map_item = None
        overview_map = None

        for item in novos_itens:
            if hasattr(item, 'id'):
                if item.id() == 'main_map': map_item = item
                elif item.id() == 'overview_map': overview_map = item

        if not map_item: return None, None, []

        # EXORCISMO FINAL NO C++
        map_item.blockSignals(True)
        map_item.setAtlasDriven(False)
        map_item.setLayers([])
        map_item.blockSignals(False)

        if overview_map:
            overview_map.blockSignals(True)
            overviews = overview_map.overviews()
            for ov in overviews.asList(): overviews.removeOverview(ov.name())
            overview_map.setLayers([])
            overview_map.blockSignals(False)

        return map_item, overview_map, novos_itens

    @staticmethod
    def processar_textos_dinamicos(novos_itens, layout, feicao_atual, camada, pagina_index, tr_func):
        """Aplica o deslocamento de múltiplas páginas e substitui variáveis de texto e expressões."""
        h_pg = layout.pageCollection().page(0).rect().height() if pagina_index > 0 else 0
        y_offset = pagina_index * (h_pg + 10.0) if pagina_index > 0 else 0

        for item in novos_itens:
            if isinstance(item, QgsLayoutItemLabel):
                texto_original = item.text()

                # Injeção de dependência para tradução!
                texto_final = tr_func(texto_original)

                if feicao_atual:
                    def replace_chave(match):
                        coluna = match.group(1)
                        try:
                            idx = feicao_atual.fields().lookupField(coluna)
                            if idx != -1:
                                val = feicao_atual.attribute(coluna)
                                return str(val).strip() if val is not None and val != NULL else ""
                        except:
                            pass
                        return match.group(0)

                    texto_final = re.sub(r'\["(.*?)"\]', replace_chave, texto_final)

                    if '[%' in texto_final:
                        contexto = QgsExpressionContextUtils.createFeatureBasedContext(feicao_atual, camada.fields())
                        texto_final = QgsExpression.replaceExpressionText(texto_final, contexto)

                if texto_final != texto_original:
                    item.setText(texto_final)
                    item.adjustSizeToText()

            elif isinstance(item, QgsLayoutItemLegend):
                titulo_original = item.title()
                titulo_traduzido = tr_func(titulo_original)
                if titulo_traduzido != titulo_original:
                    item.setTitle(titulo_traduzido)

            # Empurra os itens para a página correta
            if pagina_index > 0 and not isinstance(item, QgsLayoutItemPage):
                pos_x = item.pos().x()
                pos_y = item.pos().y()
                item.attemptMove(QgsLayoutPoint(pos_x, pos_y + y_offset, QgsUnitTypes.LayoutMillimeters))