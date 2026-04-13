# -*- coding: utf-8 -*-
import os
import re
import gc
import unicodedata
import math
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt import sip
from qgis.PyQt.QtCore import QCoreApplication, Qt, QSize
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    QgsPrintLayout, QgsLayoutExporter, QgsProject, QgsRectangle,
    QgsCoordinateTransform, QgsLayoutItemPage, QgsLayoutItemLabel,
    QgsLayoutItemMap, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes,
    QgsWkbTypes, QgsVectorLayer, QgsLayoutItem, NULL,
    QgsExpression, QgsExpressionContextUtils, QgsLayoutItemScaleBar,
    QgsLayoutItemPicture, QgsLayoutItemLegend, Qgis, QgsLegendStyle,
    QgsLayoutRenderContext, QgsFeature, QgsLayoutItemMapGrid,
    QgsReadWriteContext, QgsLayoutItemMapOverview, QgsFillSymbol,
    QgsMessageLog, QgsMapLayerType, QgsApplication
)

class LayoutEngine:
    """Motor de geração de layouts e mapas do VectorToMap (Desacoplado da UI)."""

    def __init__(self, iface):
        self.iface = iface
        self.abort_processing = False
        self.clones_preview = [] # Controle interno de lixo




    def tr(self, message):
        """Helper para traduções dentro do motor."""
        return QCoreApplication.translate('VectorToMap', message)




    def _gerar_nome_arquivo_pagina(self, dados, index, campo_atlas):
        """Gera um sufixo limpo baseado no resultado da expressão pré-calculada ou sequencial."""
        if campo_atlas == "__ALL_FEATURES__":
            return self.tr("Zoom_Camada")
            
        # O Cérebro Python (vector_to_map.py) já calculou a expressão e colocou na chave 'valor_grupo'
        if campo_atlas and 'valor_grupo' in dados and dados['valor_grupo'] is not None:
            nome = str(dados['valor_grupo'])
            return re.sub(r'[\\/*?:"<>|]', "", nome).strip()[:8].strip()
            
        return str(index + 1)




    # =========================================================================
    # --- MÉTODOS DE EXPORTAÇÃO PRINCIPAIS
    # =========================================================================

    def exportar_paginas_individuais(self, project, camada, paginas_dados, config, progress_callback=None):
        """Modo Descartável: Cria, exporta e destrói um layout para cada página."""
        preset = config['preset']
        orientacao = config['orientacao']
        base_sem_ext = config['base_sem_ext']
        ext = config['ext']
        campo_atlas = config['campo_atlas']

        for i, dados in enumerate(paginas_dados):
            if self.abort_processing: break

            # --- PROTEÇÃO: ABORTA SE O USUÁRIO DELETAR A CAMADA/PROJETO NO MEIO ---
            if sip.isdeleted(camada):
                self.abort_processing = True
                raise RuntimeError(self.tr("A camada original foi removida do QGIS durante a exportação. Processo abortado."))
            # ----------------------------------------------------------------------

            nome_arquivo = self._gerar_nome_arquivo_pagina(dados, i, campo_atlas)
            
            layout_temp = QgsPrintLayout(project)
            layout_temp.initializeDefaults()
            
            self.montar_design_da_pagina(
                layout_temp, camada, dados['feicoes'], preset, orientacao, config, 
                pagina_index=0, is_preview=False, nome_sufixo=nome_arquivo
            )
            layout_temp.refresh()
            
            caminho_final = f"{base_sem_ext}_{nome_arquivo}{ext}"
            exporter = QgsLayoutExporter(layout_temp)
            
            if ext in [".png", ".jpg", ".jpeg"]:
                img_settings = QgsLayoutExporter.ImageExportSettings()
                img_settings.dpi = 300 
                exporter.exportToImage(caminho_final, img_settings)
            elif ext == ".svg":
                svg_settings = QgsLayoutExporter.SvgExportSettings()
                svg_settings.exportLabelsToPaths = True
                exporter.exportToSvg(caminho_final, svg_settings)
            else:
                pdf_settings = QgsLayoutExporter.PdfExportSettings()
                pdf_settings.dpi = 300
                exporter.exportToPdf(caminho_final, pdf_settings)
                
            # --- CORREÇÃO: LIMPEZA DE MEMÓRIA SEGURA ---
            # Desconecta as camadas do quadro para o C++ não apagá-las junto com o layout
            for item in layout_temp.items():
                if isinstance(item, QgsLayoutItemMap):
                    item.setKeepLayerSet(False)
                    item.setLayers([])
                    
            layout_temp.pageCollection().clear()
            layout_temp.deleteLater() # Exclusão segura escalonada do Qt
            layout_temp = None
            # -------------------------------------------

            if progress_callback: progress_callback(i + 1)
            QCoreApplication.processEvents()




    def montar_layout_persistente(self, project, manager, camada, paginas_dados, config, progress_callback=None):
        """Modo Acumulador: Adiciona todas as páginas num único layout do QGIS."""
        preset = config['preset']
        orientacao = config['orientacao']
        campo_atlas = config['campo_atlas']

        nome_camada = re.sub(r'[^a-zA-Z0-9_]', '_', unicodedata.normalize('NFD', camada.name()).encode('ascii', 'ignore').decode('utf-8'))
        layout_name = f"VectorToMap_{nome_camada}"
        
        contador = 1
        while manager.layoutByName(layout_name):
            layout_name = f"VectorToMap_{nome_camada}_{contador}"
            contador += 1
            
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)

        # --- OTIMIZAÇÃO 1: Calcular invariantes FORA do loop ---
        is_template = str(preset).endswith('.qpt') or preset == "template"
        tamanho_template = None 
        
        # --- OTIMIZAÇÃO 2: Silenciar o Layout durante a construção em lote ---
        layout.blockSignals(True)

        for i, dados in enumerate(paginas_dados):
            if self.abort_processing: break

            # --- PROTEÇÃO: ABORTA SE O USUÁRIO DELETAR A CAMADA/PROJETO NO MEIO ---
            if sip.isdeleted(camada):
                self.abort_processing = True
                raise RuntimeError(self.tr("A camada original foi removida do QGIS durante a exportação. Processo abortado."))
            # ----------------------------------------------------------------------
            
            nome_sufixo = self._gerar_nome_arquivo_pagina(dados, i, campo_atlas)

            if i > 0: 
                # 1. Sempre adiciona uma página física (Fundo branco)
                nova_pagina = QgsLayoutItemPage(layout)
                layout.pageCollection().addPage(nova_pagina)
                
                # 2. Se for um modelo, aplica o tamanho capturado na página 0
                if is_template:
                    if tamanho_template is None:
                        # Captura o tamanho apenas uma vez, na primeira necessidade
                        tamanho_template = layout.pageCollection().page(0).pageSize()
                    
                    nova_pagina.setPageSize(tamanho_template)
                
            self.montar_design_da_pagina(
                layout, camada, dados['feicoes'], preset, orientacao, config, 
                pagina_index=i, is_preview=False, nome_sufixo=nome_sufixo
            )

            # --- OTIMIZAÇÃO 3: Agrupar limpeza e UI Updates para evitar gargalos ---
            # Atualiza a interface (barra de progresso e destrava tela) a cada 3 mapas
            if i % 5 == 0:
                if progress_callback: progress_callback(i + 1)
                QCoreApplication.processEvents()

            # Faz a coleta de lixo pesada a cada 20 mapas
            if i > 0 and i % 25 == 0:
                gc.collect()
        
        # --- Religamos os sinais ao terminar o processo bruto ---
        layout.blockSignals(False)
        
        # Garantir que a barra de progresso chegue a 100% caso não tenha parado no múltiplo de 3
        if progress_callback and not self.abort_processing: 
            progress_callback(len(paginas_dados))
            QCoreApplication.processEvents()
            
        return layout




    # =========================================================================
    # --- RENDERIZAÇÃO E DESIGN
    # =========================================================================

    def montar_design_da_pagina(self, layout, camada, feicoes_da_pagina, preset, orientacao, config, pagina_index=0, is_preview=False, nome_sufixo=""):
        """Orquestra a montagem completa da página lendo dados do dicionário config."""
        if preset.endswith('.qpt') and os.path.exists(preset):
            self._montar_por_template(layout, camada, feicoes_da_pagina, preset, config, is_preview, nome_sufixo, pagina_index)
            return

        geometria, apenas_mapa, cor_fundo_mapa = self._configurar_papel_e_fundo(layout, pagina_index, preset, orientacao, config)

        if not apenas_mapa:
            self._adicionar_titulo(layout, geometria, config)

        map_item = self._adicionar_item_mapa(layout, geometria, apenas_mapa, cor_fundo_mapa)
        map_item.setId("main_map")

        self._aplicar_extensao_e_escala(map_item, camada, feicoes_da_pagina, geometria['w_map'], geometria['h_map'], config)
        self._adicionar_grade_ao_mapa(map_item, config)

        self._gerenciar_visibilidade_camadas(map_item, camada, feicoes_da_pagina, is_preview, nome_sufixo, pagina_index, config)

        # A MÁGICA AGORA ACONTECE TODA AQUI DENTRO (Sem sobreposições!)
        self._orquestrar_decoracoes_3_momentos(layout, map_item, geometria, config)
        
        self._renderizar_textos_e_atributos(layout, camada, feicoes_da_pagina, preset, orientacao, geometria, apenas_mapa, config)

        if not apenas_mapa:
            self.adicionar_numeracao_pagina(layout, geometria['w_pg'], geometria['h_pg'], geometria['y_zero'], config)

    
    
    
    def _montar_por_template(self, layout, camada, feicoes_da_pagina, caminho_qpt, config, is_preview, nome_sufixo, pagina_index):
        """Carrega o .qpt limpando centenas de mapas duplicados e fantasmas do XML corrompido."""
        if not os.path.exists(caminho_qpt): return

        nome_original = layout.name()

        with open(caminho_qpt, 'rt', encoding='utf-8') as f:
            template_content = f.read()

        # =====================================================================
        # A OPERAÇÃO FAXINA (MATADOR DE MAPAS FANTASMAS)
        # Seu arquivo tem centenas de <LayoutItem type="65639"> (Mapas).
        # Vamos usar Regex para manter APENAS os mapas que você nomeou como 
        # 'main_map' ou 'overview_map'. Todo o resto será deletado do texto.
        # =====================================================================
        
        # 1. Identifica todos os blocos de LayoutItem do tipo Mapa (65639)
        padrao_mapa = re.compile(r'<LayoutItem[^>]*type="65639"[^>]*>.*?</LayoutItem>', re.DOTALL)
        
        def filtrar_mapas(match):
            bloco = match.group(0)
            # SÓ mantém o mapa se ele tiver o ID que o VectorToMap usa
            if 'id="main_map"' in bloco or 'id="overview_map"' in bloco:
                return bloco
            # Deleta qualquer mapa sem ID ou com tamanho zerado (lixo do QGIS)
            return ""

        # Executa a limpeza pesada no texto
        template_content = padrao_mapa.sub(filtrar_mapas, template_content)
        
        # 2. Remove miras vermelhas e travas que restaram
        template_content = re.sub(r'<overviews>.*?</overviews>', '<overviews/>', template_content, flags=re.DOTALL)
        template_content = re.sub(r'keepLayerSet="[^"]+"', 'keepLayerSet="1"', template_content)
        template_content = re.sub(r'<LayerSet>.*?</LayerSet>', '<LayerSet/>', template_content, flags=re.DOTALL)

        doc = QDomDocument()
        doc.setContent(template_content)
        
        itens_antes = set(layout.items())
        limpar = (pagina_index == 0)
        layout.loadFromTemplate(doc, QgsReadWriteContext(), clearExisting=limpar)
        layout.setName(nome_original)

        # --- Localização dos Itens Reais ---
        novos_itens = list(set(layout.items()) - itens_antes)
        map_item = None
        overview_map = None
        
        for item in novos_itens:
            if hasattr(item, 'id'):
                if item.id() == 'main_map': map_item = item
                elif item.id() == 'overview_map': overview_map = item
        
        # Fallback caso os IDs não estejam no XML (pega os primeiros mapas que sobraram da faxina)
        if not map_item:
            for item in novos_itens:
                if isinstance(item, QgsLayoutItemMap) and item != overview_map:
                    map_item = item
                    break
        
        if not map_item: return

        # ====================================================================
        # --- EXORCISMO FINAL (SEGURANÇA) ---
        # ====================================================================
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

        # ====================================================================
        # --- DESLOCAMENTO MULTI-PÁGINA E TRADUÇÃO (O QUE FALTAVA) ---
        # ====================================================================
        h_pg = layout.pageCollection().page(0).rect().height() if pagina_index > 0 else 0
        y_offset = pagina_index * (h_pg + 10.0) if pagina_index > 0 else 0

        for item in novos_itens:
            if isinstance(item, QgsLayoutItemLabel):
                texto_original = item.text()
                texto_traduzido = self.tr(texto_original)
                if texto_traduzido != texto_original:
                    item.setText(texto_traduzido)
                    item.adjustSizeToText() 
            
            elif isinstance(item, QgsLayoutItemLegend):
                titulo_original = item.title()
                titulo_traduzido = self.tr(titulo_original)
                if titulo_traduzido != titulo_original:
                    item.setTitle(titulo_traduzido)

            # Empurra os itens para a página correta lá embaixo!
            if pagina_index > 0 and not isinstance(item, QgsLayoutItemPage):
                pos_x = item.pos().x()
                pos_y = item.pos().y()
                item.attemptMove(QgsLayoutPoint(pos_x, pos_y + y_offset, QgsUnitTypes.LayoutMillimeters))

        # --- Processamento de Escala e Visibilidade ---
        w_map, h_map = map_item.rect().width(), map_item.rect().height()
        self._aplicar_extensao_e_escala(map_item, camada, feicoes_da_pagina, w_map, h_map, config)
        self._gerenciar_visibilidade_camadas(map_item, camada, feicoes_da_pagina, is_preview, nome_sufixo, pagina_index, config)

        if overview_map:
            self._aplicar_regras_overview(overview_map, map_item, config, is_template=True)




    # -------------------------------------------------------------------------
    # --- SUB-FUNÇÕES DE MONTAGEM
    # -------------------------------------------------------------------------

    def _configurar_papel_e_fundo(self, layout, pagina_index, preset, orientacao, config):
        dim = config.get('tamanho_pg', (210.0, 297.0))
        w_pg, h_pg = (dim[1], dim[0]) if orientacao == "Paisagem" else (dim[0], dim[1])
        
        pagina = layout.pageCollection().pages()[pagina_index]
        pagina.setPageSize(QgsLayoutSize(w_pg, h_pg, QgsUnitTypes.LayoutMillimeters))

        y_zero_folha = pagina_index * (h_pg + 10)
        margin_padrao = 15.0

        cor_pagina = config.get('cor_pagina', QColor(255, 255, 255, 255))
        cor_mapa = config.get('cor_fundo', QColor(255, 255, 255, 255))

        # --- NOVO: Lógica que zera a opacidade (Alpha = 0) mantendo a cor RGB original ---
        if config.get('pag_fundo_transp', False):
            cor_pagina.setAlpha(0)
            
        if config.get('map_fundo_transp', False):
            cor_mapa.setAlpha(0)
        # --------------------------------------------------------------------------------
        
        pagina.setBackgroundEnabled(True)
        if pagina.pageStyleSymbol():
            simbolo_novo = pagina.pageStyleSymbol().clone()
            simbolo_novo.setColor(cor_pagina)
            pagina.setPageStyleSymbol(simbolo_novo)

        if preset == "horizontal":
            header_h = 35.0
            h_util = h_pg - (2 * margin_padrao) - header_h
            w_map_f = w_pg - (2 * margin_padrao)
            
            if orientacao == "Paisagem":
                h_map_f = h_util * 0.75
                x_map_f = margin_padrao
                y_map_f = y_zero_folha + margin_padrao + header_h
            else:
                altura_antiga = h_util * 0.75
                y_antigo = y_zero_folha + margin_padrao + header_h
                centro_y = y_antigo + (altura_antiga / 2.0)
                h_map_f = w_map_f * 0.75
                x_map_f = margin_padrao
                y_map_f = centro_y - (h_map_f / 2.0)
                
        elif preset == "vertical":
            if orientacao == "Retrato":
                w_map_f = w_pg - (2 * margin_padrao)
                x_map_f = margin_padrao
                y_map_f = y_zero_folha + margin_padrao + 30.0
                h_map_f = w_pg + 10.0 
            else:
                largura_util = w_pg - (2 * margin_padrao)
                h_map_f = h_pg - (2 * margin_padrao)
                w_map_f = largura_util * 0.50
                x_map_f = w_pg - margin_padrao - w_map_f
                y_map_f = y_zero_folha + margin_padrao
                
        else: # "quadrado"
            if orientacao == "Retrato":
                w_map_f, h_map_f = w_pg - (2 * margin_padrao), w_pg - (2 * margin_padrao)
                x_map_f, y_map_f = margin_padrao, y_zero_folha + 40.0
            else:
                h_map_f = h_pg - (2 * margin_padrao)
                w_map_f = h_map_f
                x_map_f, y_map_f = w_pg - margin_padrao - w_map_f, y_zero_folha + margin_padrao

        apenas_mapa = config.get('apenas_mapa', False)

        if apenas_mapa:
            w_pg, h_pg = w_map_f, h_map_f
            x_map_f = 0.0
            y_zero_folha = pagina_index * (h_pg + 10)
            y_map_f = y_zero_folha
            pagina.setPageSize(QgsLayoutSize(w_pg, h_pg, QgsUnitTypes.LayoutMillimeters))

        geometria = {
            'w_pg': w_pg, 'h_pg': h_pg, 'w_map': w_map_f, 'h_map': h_map_f,
            'x_map': x_map_f, 'y_map': y_map_f, 'y_zero': y_zero_folha, 'margin': margin_padrao
        }
        return geometria, apenas_mapa, cor_mapa

    def _adicionar_titulo(self, layout, geo, config):
        texto = config.get('texto_titulo', '').strip()
        if not texto: return

        lbl_titulo = QgsLayoutItemLabel(layout)
        lbl_titulo.setText(texto)
        
        if 'fonte_titulo' in config:
            lbl_titulo.setFont(config['fonte_titulo'])
            
        alinhamento = config.get('alinhamento_titulo', Qt.AlignmentFlag.AlignHCenter)
        lbl_titulo.setHAlign(alinhamento)
        lbl_titulo.setVAlign(Qt.AlignmentFlag.AlignTop)
        
        x = geo['margin'] 
        y = geo['y_zero'] + geo['margin'] 
        largura = geo['w_pg'] - (2 * geo['margin'])
        altura_livre = 60.0 
        
        lbl_titulo.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
        lbl_titulo.attemptResize(QgsLayoutSize(largura, altura_livre, QgsUnitTypes.LayoutMillimeters))
        lbl_titulo.setZValue(50) 
        layout.addLayoutItem(lbl_titulo)
    

    def _adicionar_item_mapa(self, layout, geo, apenas_mapa, cor_fundo):
        map_item = QgsLayoutItemMap(layout)
        map_item.setFrameEnabled(not apenas_mapa) 
        map_item.setBackgroundEnabled(True)
        map_item.setBackgroundColor(cor_fundo)
        layout.addLayoutItem(map_item)
        
        map_item.attemptResize(QgsLayoutSize(geo['w_map'], geo['h_map'], QgsUnitTypes.LayoutMillimeters))
        map_item.attemptMove(QgsLayoutPoint(geo['x_map'], geo['y_map'], QgsUnitTypes.LayoutMillimeters))
        map_item.setZValue(0)
        return map_item
    

    
    
    def _aplicar_regras_overview(self, overview_map, main_map, config, is_template):
        
        chk_ativada = config.get('inserir_mapa_loc', False)
        camada_loc = config.get('camada_loc')

        try:
            overview_map.blockSignals(True)

            project_crs = QgsProject.instance().crs()
            overview_map.setCrs(project_crs)

            if is_template and not chk_ativada:
                overview_map.setKeepLayerSet(True)
                overview_map.setLayers(main_map.layers())
                overview_map.setKeepLayerStyles(True)

                ext = main_map.extent()
                if not ext.isEmpty():
                    ext.scale(10.0) 
                    overview_map.zoomToExtent(ext) 

            else:
                layers_to_show = []
                root = QgsProject.instance().layerTreeRoot()
                
                # Recupera a configuração do usuário
                incluir_rasters_loc = config.get('add_raster_loc', False)
                
                # ====================================================================
                # A CURA DA ORDEM: root.layerOrder() puxa as camadas exatamente na 
                # ordem Z (de cima para baixo) que está no painel do seu QGIS!
                # ====================================================================
                for layer in root.layerOrder():
                    if layer.name().startswith("Mapa_") or "Preview" in layer.name():
                        continue
                    node = root.findLayer(layer.id())
                    if node and node.isVisible():
                        
                        # --- NOVO: Lógica de filtro do Raster ---
                        is_raster = (layer.type() == QgsMapLayerType.RasterLayer)
                        if is_raster and not incluir_rasters_loc:
                            continue # Pula a camada raster se a checkbox estiver desmarcada
                        # ----------------------------------------
                        
                        layers_to_show.append(layer)

                if camada_loc and camada_loc not in layers_to_show:
                    # Se a camada de localização estava com o olhinho fechado, 
                    # a gente joga ela no final da lista (fundo do mapa) para não tampar nada
                    layers_to_show.append(camada_loc)

                overview_map.setKeepLayerSet(True)
                overview_map.setLayers(layers_to_show)
                overview_map.setKeepLayerStyles(True)

                if camada_loc:
                    ext = camada_loc.extent()
                    if camada_loc.crs() != project_crs:
                        trans = QgsCoordinateTransform(camada_loc.crs(), project_crs, QgsProject.instance().transformContext())
                        try: ext = trans.transformBoundingBox(ext)
                        except: pass
                    
                    if not ext.isEmpty():
                        ext.scale(1.15) 
                        overview_map.zoomToExtent(ext)

            # MIRA VERMELHA VAZADA
            overviews = overview_map.overviews()
            for ov in overviews.asList():
                overviews.removeOverview(ov.name())

            overview = QgsLayoutItemMapOverview("Overview_Plugin", overview_map)
            overview.setLinkedMap(main_map)

            simbolo = QgsFillSymbol.createSimple({'outline_color': 'red', 'outline_width': '0.8', 'outline_style': 'solid'})
            if simbolo:
                try: simbolo.symbolLayer(0).setBrushStyle(Qt.NoBrush)
                except AttributeError: simbolo.symbolLayer(0).setBrushStyle(Qt.BrushStyle.NoBrush)
                overview.setFrameSymbol(simbolo)

            overview.setEnabled(True)
            overview_map.overviews().addOverview(overview)

        except Exception as e:
            import traceback
            QgsMessageLog.logMessage(f"Erro Overview: {str(e)}\n{traceback.format_exc()}", "VectorToMap", Qgis.Warning)
            
        finally:
            overview_map.blockSignals(False)
            overview_map.invalidateCache()
    

    
    
    def _orquestrar_decoracoes_3_momentos(self, layout, map_item, geo, config):
        """
        1º Momento: Criação (Nascimento dos itens)
        2º Momento: Maturação (Ensaio na memória com Invisibilidade de Mapas)
        3º Momento: Posicionamento (A sua matemática exata)
        """
        # =====================================================================
        # 1º MOMENTO: CRIAÇÃO
        # =====================================================================
        elementos = []

        # --- 1. O MAPA DE LOCALIZAÇÃO ---
        if config.get('inserir_mapa_loc', False) and config.get('camada_loc'):
            
            overview_map = QgsLayoutItemMap(layout)
            layout.addLayoutItem(overview_map) 
            
            overview_map.setId("overview_map")
            overview_map.setFrameEnabled(True)
            overview_map.setBackgroundEnabled(True)
            overview_map.setBackgroundColor(QColor(255, 255, 255, 255))
            
            w_loc = geo['w_map'] * 0.22
            h_loc = geo['h_map'] * 0.22
            overview_map.attemptResize(QgsLayoutSize(w_loc, h_loc, QgsUnitTypes.LayoutMillimeters))
            
            self._aplicar_regras_overview(overview_map, map_item, config, is_template=False)
            elementos.append({'tipo': 'mapa_loc', 'item': overview_map, 'pos': config.get('pos_mapa_loc', 'ID')})

        # --- 2. LEGENDA ---
        if config.get('inserir_legenda', False):
            legenda = QgsLayoutItemLegend(layout)
            legenda.setTitle(self.tr("Legenda"))
            legenda.setLinkedMap(map_item)
            legenda.setBackgroundEnabled(True)
            legenda.setBackgroundColor(QColor(255, 255, 255, 204))
            try: legenda.rstyle(Qgis.LegendComponent.Title).setMargin(QgsLegendStyle.Side.Bottom, 2.5)
            except: pass

            legenda.setAutoUpdateModel(False)
            root_projeto = QgsProject.instance().layerTreeRoot()
            root_legenda = legenda.model().rootGroup()
            
            # Recupera a configuração do usuário
            incluir_rasters = config.get('add_raster_legend', False)

            for no_camada in root_projeto.findLayers():
                layer = no_camada.layer()
                if not layer: continue
                
                is_raster = (layer.type() == QgsMapLayerType.RasterLayer)
                
                # Regra: Removemos a camada da legenda SE:
                # 1. Ela estiver com o olhinho fechado (invisível) OU
                # 2. Ela for um raster E o usuário não marcou a checkbox
                deve_remover = (not no_camada.isVisible()) or (is_raster and not incluir_rasters)
                
                if deve_remover:
                    no_legenda = root_legenda.findLayer(no_camada.layerId())
                    if no_legenda: 
                        no_legenda.parent().removeChildNode(no_legenda)

            # Limpa grupos vazios e as camadas temporárias do plugin
            for no_grupo in root_legenda.findGroups():
                if "VectorToMap" in no_grupo.name() or not no_grupo.children():
                    no_grupo.parent().removeChildNode(no_grupo)

            layout.addLayoutItem(legenda)
            elementos.append({'tipo': 'legenda', 'item': legenda, 'pos': config.get('pos_legenda', 'IE')})

        # --- 3. ESCALA ---
        if config.get('inserir_escala', False):
            escala = QgsLayoutItemScaleBar(layout)
            layout.addLayoutItem(escala)
            escala.setLinkedMap(map_item)
            escala.setStyle('Line Ticks Up') 
            
            # --- NOVO: Fundo branco com 80% de opacidade ---
            escala.setBackgroundEnabled(True)
            escala.setBackgroundColor(QColor(255, 255, 255, 204))
            # -----------------------------------------------
            
            escala_mapa = map_item.scale()

            if escala_mapa <= 0:
                escala_mapa = config.get('escala_val', 10000.0)
            
            # Descobre qual unidade usar
            unidade = QgsUnitTypes.DistanceKilometers if escala_mapa >= 50000 else QgsUnitTypes.DistanceMeters
            
            escala.setUnits(unidade)
            escala.setUnitLabel("km" if unidade == QgsUnitTypes.DistanceKilometers else "m")
            
            escala.setNumberOfSegments(2)
            escala.setNumberOfSegmentsLeft(0)
            escala.setMinimumBarWidth(55.0)
            escala.setMaximumBarWidth(110.0)
            
            # A BALA DE PRATA: Passamos a nossa unidade para ele não resetar pro padrão!
            escala.applyDefaultSize(unidade)
            escala.update()
            
            elementos.append({'tipo': 'escala', 'item': escala, 'pos': config.get('pos_escala', 'ID')})

        # --- 4. NORTE ---
        if config.get('inserir_norte', False):
            norte = QgsLayoutItemPicture(layout)
            
            # --- NOVA LÓGICA DO ESTILO DA SETA ---
            try:
                pasta_svg = QgsApplication.svgPaths()[0]
                estilo = config.get('estilo_norte', 'NorthArrow_02.svg')
                caminho_seta = os.path.join(pasta_svg, "arrows", estilo)
                norte.setPicturePath(caminho_seta)
            except Exception:
                # Fallback de segurança se o QGIS do usuário estiver com as pastas bagunçadas
                norte.setPicturePath(':/images/north_arrows/layout_default_north_arrow.svg')
            # -------------------------------------
            
            norte.setLinkedMap(map_item)
            layout.addLayoutItem(norte)
            elementos.append({'tipo': 'norte', 'item': norte, 'pos': config.get('pos_norte', 'SD')})

        if not elementos: return

        # =====================================================================
        # 2º MOMENTO: MATURAÇÃO (Com Truque de Invisibilidade)
        # =====================================================================
        # Encontra todos os mapas no layout (Principal e Localização)
        mapas_na_tela = [item for item in layout.items() if isinstance(item, QgsLayoutItemMap)]
        visibilidades = {m.uuid(): m.isVisible() for m in mapas_na_tela}
        
        # DESLIGA a renderização dos mapas pesados
        for m in mapas_na_tela:
            m.setVisibility(False)

        contexto = layout.renderContext()
        flags_originais = contexto.flags()
        contexto.setFlags(flags_originais & ~QgsLayoutRenderContext.FlagAntialiasing)

        # O Rascunho cego e instantâneo
        exporter = QgsLayoutExporter(layout)
        _ = exporter.renderPageToImage(0, QSize(), 15.0)

        contexto.setFlags(flags_originais)

        # LIGA a renderização dos mapas novamente para a foto final
        for m in mapas_na_tela:
            m.setVisibility(visibilidades.get(m.uuid(), True))

        for el in elementos:
            item = el['item']
            if el['tipo'] == 'legenda':
                item.updateLegend() 
                item.adjustBoxSize() 
            elif el['tipo'] == 'escala':
                # Passa a unidade que a escala já tem, protegendo contra o reset
                item.applyDefaultSize(item.units()) 
                item.update()
            elif el['tipo'] == 'norte':
                item.attemptResize(QgsLayoutSize(18.0, 18.0, QgsUnitTypes.LayoutMillimeters))
        
        # (NÃO TEM MAIS layout.refresh() AQUI! Limpamos a redundância)

        # =====================================================================
        # 3º MOMENTO: POSICIONAMENTO FINAL
        # =====================================================================
        cantos = {'SE': [], 'SD': [], 'IE': [], 'ID': []}
        for el in elementos:
            cantos[el['pos']].append(el)

        margem = 2.5 
        espacamento = 3.0

        for canto, lista_itens in cantos.items():
            if not lista_itens: continue

            is_superior = canto.startswith('S')
            is_esquerdo = canto.endswith('E')

            if is_superior:
                lista_itens.sort(key=lambda x: {'mapa_loc': 0, 'legenda': 1, 'escala': 2, 'norte': 3}[x['tipo']])
                y_teto = geo['y_map'] + margem
                ancora = QgsLayoutItem.UpperLeft if is_esquerdo else QgsLayoutItem.UpperRight

                for el in lista_itens:
                    item = el['item']
                    h = item.rect().height()
                    x = geo['x_map'] + margem if is_esquerdo else geo['x_map'] + geo['w_map'] - margem
                    
                    item.setReferencePoint(ancora)
                    item.attemptMove(QgsLayoutPoint(x, y_teto, QgsUnitTypes.LayoutMillimeters))
                    item.setZValue(15)
                    y_teto += (h + espacamento)

            else:
                lista_itens.sort(key=lambda x: {'mapa_loc': 0, 'legenda': 1, 'escala': 2, 'norte': 3}[x['tipo']])
                y_chao = geo['y_map'] + geo['h_map'] - margem
                ancora = QgsLayoutItem.LowerLeft if is_esquerdo else QgsLayoutItem.LowerRight

                for el in lista_itens:
                    item = el['item']
                    h = item.rect().height() 
                    x = geo['x_map'] + margem if is_esquerdo else geo['x_map'] + geo['w_map'] - margem
                    
                    item.setReferencePoint(ancora)
                    item.attemptMove(QgsLayoutPoint(x, y_chao, QgsUnitTypes.LayoutMillimeters))
                    item.setZValue(15)
                    y_chao -= (h + espacamento)

        for el in elementos:
            if el['tipo'] == 'legenda': el['item'].update()


    
    
    def _aplicar_extensao_e_escala(self, map_item, camada, feicoes_da_pagina, w_map, h_map, config):
        """Gerencia o BoundingBox, CRS e regras de zoom com suporte a Expressões (DDO)."""
        if not feicoes_da_pagina or sip.isdeleted(camada): return
        
        campo_atlas = config.get('campo_atlas')

        if campo_atlas == "__ALL_FEATURES__":
            ext = camada.extent()
        else:
            ext = QgsRectangle()
            
            # --- Compatibilidade Universal entre versões do QGIS 3 ---
            if hasattr(ext, 'setNull'):
                ext.setNull()    # QGIS Novo: Usa o método atual e evita o DeprecationWarning
            else:
                ext.setMinimal() # QGIS Antigo: Fallback seguro onde o setNull não existe
            # ---------------------------------------------------------
            
            for f in feicoes_da_pagina: ext.combineExtentWith(f.geometry().boundingBox())
        
        project_crs = QgsProject.instance().crs()
        trans = QgsCoordinateTransform(camada.crs(), project_crs, QgsProject.instance().transformContext())
        ext_proj = trans.transformBoundingBox(ext)
        
        is_coordenada_unica = (ext_proj.width() == 0 and ext_proj.height() == 0)
        if is_coordenada_unica: 
            respiro = 0.0001 if project_crs.isGeographic() else 1.0
            ext_proj.grow(respiro)
        
        map_item.setExtent(ext_proj)
        
        # --- A MÁGICA DA EXPRESSÃO (EPSILON) ---
        if campo_atlas == "__ALL_FEATURES__":
            feicao_atual = QgsFeature() # Dummy feature vazia para não quebrar a calculadora
        else:
            feicao_atual = feicoes_da_pagina[0]
            
        contexto = QgsExpressionContextUtils.createFeatureBasedContext(feicao_atual, camada.fields())
        
        if config.get('escala_fixa', False):
            escala_config = config.get('escala_val', 10000.0)
            escala_final = 10000.0 # Valor de segurança
            
            # Se a combo estiver em "expressao", rodamos a matemática do ε
            if escala_config == "expressao":
                exp_str = config.get('escala_fixa_exp', "")
                if exp_str:
                    try:
                        exp = QgsExpression(exp_str)
                        exp.prepare(contexto)
                        val = exp.evaluate(contexto)
                        if val is not None and not exp.hasEvalError():
                            escala_final = float(val)
                    except:
                        pass
            else:
                # Se for um valor normal da combo (ex: 5000), usa ele direto
                try:
                    escala_final = float(escala_config)
                except:
                    escala_final = 10000.0
                    
            map_item.setScale(escala_final)
            
        else:
            if is_coordenada_unica:
                escala_final = 10000.0
            else:
                unit_to_mm = QgsUnitTypes.fromUnitToUnitFactor(project_crs.mapUnits(), QgsUnitTypes.DistanceMillimeters)
                scale_w = (ext_proj.width() * unit_to_mm) / w_map
                scale_h = (ext_proj.height() * unit_to_mm) / h_map
                
                # --- NOVA LÓGICA DE ZOOM OUT DINÂMICO ---
                zoom_out_config = config.get('zoom_out_auto', 25.0)
                fator_zoom = 1.25 # Padrão de segurança
                
                if zoom_out_config == "expressao":
                    exp_str = config.get('escala_auto_exp', "")
                    if exp_str:
                        try:
                            exp = QgsExpression(exp_str)
                            exp.prepare(contexto)
                            val = exp.evaluate(contexto)
                            if val is not None and not exp.hasEvalError():
                                fator_zoom = 1.0 + (float(val) / 100.0)
                        except:
                            pass 
                else:
                    # Pega o valor fixo escolhido na combo (ex: 0.0, 15.0, 50.0)
                    try:
                        fator_zoom = 1.0 + (float(zoom_out_config) / 100.0)
                    except:
                        pass
                # ---------------------------------------- 
                
                escala_calculada = max(scale_w, scale_h) * fator_zoom
                escala_final = 10000.0 if escala_calculada < 500.0 else escala_calculada
        
            map_item.setScale(escala_final)

        map_item.refresh()
        map_item.attemptResize(QgsLayoutSize(w_map, h_map, QgsUnitTypes.LayoutMillimeters))
        map_item.attemptMove(QgsLayoutPoint(map_item.pos().x(), map_item.pos().y(), QgsUnitTypes.LayoutMillimeters))

    
    
    
    def atualizar_mapa_para_canvas(self, map_item):
        map_item.setKeepLayerSet(False)
        map_item.setKeepLayerStyles(False)
        map_item.invalidateCache()
        map_item.refresh()

    
    
    
    def criar_camada_temporaria(self, camada_original, feicoes, nome_pagina, is_preview=False):
        """Cria uma camada isolada. Tenta Subset de alta performance; se falhar, usa Memory Layer segura."""
        nome_temp = f"{self.tr('Mapa')}_{nome_pagina}"
        pk_idxs = camada_original.primaryKeyAttributes()
        
        camada_temp = None
        
        # =========================================================================
        # 1. CAMINHO DE ALTA PERFORMANCE (Clone + Filtro SQL / Subset)
        # =========================================================================
        if pk_idxs:
            camada_temp = camada_original.clone()
            camada_temp.setName(nome_temp)
            
            pk_name = camada_original.fields()[pk_idxs[0]].name()
            
            # Coleta os valores da Chave Primária apenas das feições da página atual
            valores = []
            for f in feicoes:
                val = f[pk_name]
                if isinstance(val, str):
                    valores.append(f"'{val}'") # Protege com aspas se for texto (UUID)
                else:
                    valores.append(str(val))
                    
            # Aplica o filtro direto no provedor (Não gasta RAM!)
            if valores:
                filtro_sql = f"\"{pk_name}\" IN ({','.join(valores)})"
                camada_temp.setSubsetString(filtro_sql)
            else:
                camada_temp.setSubsetString("1 = 0") # Esconde tudo se o grupo estiver vazio

        # =========================================================================
        # 2. CAMINHO DE SEGURANÇA (Fallback para Memory Layer)
        # =========================================================================
        else:
            crs_auth = camada_original.crs().authid()
            geom_type = QgsWkbTypes.displayString(camada_original.wkbType())
            uri = f"{geom_type}?crs={crs_auth}"
            
            camada_temp = QgsVectorLayer(uri, nome_temp, "memory")
            camada_temp.setCrs(camada_original.crs())
            
            provider = camada_temp.dataProvider()
            provider.addAttributes(camada_original.fields())
            camada_temp.updateFields()
            provider.addFeatures(feicoes)
            camada_temp.updateExtents() 
            
            if camada_original.renderer():
                camada_temp.setRenderer(camada_original.renderer().clone())
            
            if camada_original.labelsEnabled():
                camada_temp.setLabeling(camada_original.labeling().clone())
                camada_temp.setLabelsEnabled(True)
            
            camada_temp.triggerRepaint()

        # =========================================================================
        # 3. SALVAMENTO DA CAMADA (Impede que o Python delete a camada temp)
        # Serve tanto para o GeoPackage quanto para o Shapefile!
        # =========================================================================
        if is_preview:
            # Na preview, entra como oculta e sem grupo para não poluir a tela
            QgsProject.instance().addMapLayer(camada_temp, False)
        else:
            # Na exportação / OK, criamos a pastinha Temp na árvore de camadas
            root = QgsProject.instance().layerTreeRoot()
            nome_grupo_temp = f"{self.tr('Temp')} - VectorToMap ({camada_original.name()})"
            grupo = root.findGroup(nome_grupo_temp)
            
            if not grupo:
                no_camada_original = root.findLayer(camada_original.id())
                if no_camada_original:
                    no_pai = no_camada_original.parent()
                    idx_insercao = 0
                    for i, filho in enumerate(no_pai.children()):
                        if filho == no_camada_original:
                            idx_insercao = i
                            break
                    grupo = no_pai.insertGroup(idx_insercao, nome_grupo_temp)
                else:
                    grupo = root.insertGroup(0, nome_grupo_temp)
            
            # Avisa o QGIS que ele é o dono da camada agora (salva a vida dela)
            QgsProject.instance().addMapLayer(camada_temp, False) 
            grupo.addLayer(camada_temp)
            
        return camada_temp

    def _gerenciar_visibilidade_camadas(self, map_item, camada, feicoes_da_pagina, is_preview, nome_sufixo, pagina_index, config):
        camada_alvo = camada

        is_filtrado = config.get('filtrar_feicoes', False)
        is_isolado = config.get('exibir_so_camada_atual', False)
        is_travado_manualmente = config.get('travar_camadas', False)

        if is_filtrado:
            nome_camada_limpo = re.sub(r'[^a-zA-Z0-9_]', '_', unicodedata.normalize('NFD', camada.name()).encode('ascii', 'ignore').decode('utf-8'))
            nome_temp = f"{nome_camada_limpo}_{nome_sufixo}" if nome_sufixo else f"{nome_camada_limpo}_{pagina_index + 1}"
            camada_alvo = self.criar_camada_temporaria(camada, feicoes_da_pagina, nome_temp, is_preview)
            if is_preview: self.clones_preview.append(camada_alvo.id())

        if is_isolado or is_filtrado or is_travado_manualmente:
            camadas_finais_para_layout = []
            
            if is_isolado:
                camadas_finais_para_layout = [camada_alvo]
            else:
                root = QgsProject.instance().layerTreeRoot()
                for layer in root.layerOrder():
                    is_visible_in_toc = root.findLayer(layer.id()).isVisible()
                    if layer.id() == camada.id():
                        if is_visible_in_toc or is_filtrado:
                            if camada_alvo not in camadas_finais_para_layout: 
                                camadas_finais_para_layout.append(camada_alvo)
                    else:
                        if is_visible_in_toc and layer.id() not in self.clones_preview and layer.id() != camada_alvo.id():
                            camadas_finais_para_layout.append(layer)
            
            map_item.setLayers(camadas_finais_para_layout)
            map_item.setKeepLayerSet(True)
            
            if config.get('travar_estilos', False):
                map_item.setKeepLayerStyles(True)
        else:
            self.atualizar_mapa_para_canvas(map_item)

        map_item.refresh()

        if is_filtrado and not is_preview:
            no_da_camada = QgsProject.instance().layerTreeRoot().findLayer(camada_alvo.id())
            if no_da_camada: no_da_camada.setItemVisibilityChecked(False)
    

    def _renderizar_textos_e_atributos(self, layout, camada, feicoes_da_pagina, preset, orientacao, geo, apenas_mapa, config):
        campo_atlas = config.get('campo_atlas')
        if apenas_mapa: return
        if not config.get('exibir_atributos', True): return

        geom = self._calcular_geometria_textos(preset, orientacao, geo, config)

        if campo_atlas == "__ALL_FEATURES__":
            self._renderizar_resumo_camada(layout, camada, geom, geo)
            return

        colunas = config.get('colunas', [])
        
        # Proteção contra lista 'dummy' e lista vazia
        if not colunas or not feicoes_da_pagina or isinstance(feicoes_da_pagina[0], str):
            return

        if config.get('modo_formulario', False):
            self._renderizar_modo_formulario(layout, feicoes_da_pagina, colunas, geom, config)

        if config.get('modo_individual', False):
            self._renderizar_modo_individual(layout, feicoes_da_pagina, colunas, geom, preset, orientacao, config)


    def _renderizar_resumo_camada(self, layout, camada, geom, geo):
        """Renderiza um bloco de metadados quando o mapa for da camada inteira, usando toda a largura."""
        
        nome = camada.name()
        total = camada.featureCount()
        geom_tipo = QgsWkbTypes.displayString(camada.wkbType())
        
        crs_camada = camada.crs()
        crs_camada_str = f"{crs_camada.authid()} - {crs_camada.description()}"
        
        crs_projeto = QgsProject.instance().crs()
        crs_projeto_str = f"{crs_projeto.authid()} - {crs_projeto.description()}"
        
        t_tit = self.tr("Resumo do Mapa Geral")
        t_camada = self.tr("Camada Vetorial")
        t_geometria = self.tr("Tipo de Geometria")
        t_total = self.tr("Total de Feições")
        t_crs_camada = self.tr("SRC da Camada")
        t_crs_proj = self.tr("SRC do Projeto")
        
        txt_html = f"""
            <b style='font-size: 14px; color: #2c3e50;'>{t_tit}</b><br><br>
            <b>{t_camada}:</b> {nome}<br>
            <b>{t_geometria}:</b> {geom_tipo}<br>
            <b>{t_total}:</b> {total}<br>
            <b>{t_crs_camada}:</b> {crs_camada_str}<br>
            <b>{t_crs_proj}:</b> {crs_projeto_str}
        """
        
        largura_maxima = geo['w_pg'] - geom['x_form'] - geo['margin']
        
        self._inserir_label_no_layout(
            layout, txt_html, 
            geom['x_form'], geom['y_form'], 
            largura_maxima, geom['h_form'], 
            is_html=True
        )


    def _calcular_geometria_textos(self, preset, orientacao, geo, config):
        limite_fundo = geo['y_zero'] + geo['h_pg'] - geo['margin']
        geom = {'limite_fundo': limite_fundo}

        if orientacao == "Retrato" or preset == "horizontal":
            largura_util = geo['w_pg'] - (2 * geo['margin'])
            terco_x = geo['margin'] + (largura_util * 0.33) 
            
            geom['x_form'] = geo['margin']
            geom['y_form'] = geo['y_map'] + geo['h_map'] + 7.0
            geom['w_form'] = (largura_util * 0.33) - 2.0
            geom['h_form'] = limite_fundo - geom['y_form']
            
            geom['x_ind_start'] = terco_x + 2.0
            geom['y_ind_min'] = geo['y_map'] + geo['h_map'] + 7.0
            
        elif preset == "vertical":
            geom['x_form'] = geo['margin']
            h_util = geo['h_map']
            h_top = h_util * 0.34 
            geom['y_form'] = geo['y_map'] + h_top 
            geom['h_form'] = h_util * 0.33       
            geom['w_form'] = (geo['x_map'] - geo['margin']) - 5.0 
            geom['x_ind_start'] = geom['x_form']
            geom['y_ind_min'] = geom['y_form'] + geom['h_form'] 
            
        else: # "quadrado"
            geom['x_form'] = geo['margin']
            geom['y_form'] = geo['y_map'] + (geo['h_map'] / 2)
            geom['w_form'] = geo['x_map'] - (2 * geo['margin'])

            geom['x_ind_start'] = geom['x_form']
            if config.get('modo_individual', False):
                geom['h_form'] = (limite_fundo - geom['y_form']) * 0.5
                geom['y_ind_min'] = geom['y_form'] + geom['h_form'] + 2.0
            else:
                geom['h_form'] = limite_fundo - geom['y_form']
                geom['y_ind_min'] = geom['y_form']

        return geom

    def _inserir_label_no_layout(self, layout, texto, x, y, w=None, h=None, is_html=False, auto_resize=False):
        lbl = QgsLayoutItemLabel(layout)
        
        if is_html:
            mode = QgsLayoutItemLabel.ContentMode.ModeHtml if hasattr(QgsLayoutItemLabel, 'ContentMode') else (QgsLayoutItemLabel.ModeHtml if hasattr(QgsLayoutItemLabel, 'ModeHtml') else 1)
            lbl.setMode(mode)
        
        # Garantimos que a caixa (frame) fique sempre desligada por padrão
        lbl.setFrameEnabled(False) 

        lbl.setText(texto)
        
        if auto_resize:
            lbl.adjustSizeToText()
            w = lbl.rect().width() + 2.0
            h = lbl.rect().height()
            
        if w is not None and h is not None:
            lbl.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
            
        lbl.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(lbl)
        
        return float(w) if w is not None else 0.0

    def _renderizar_modo_formulario(self, layout, feicoes_da_pagina, colunas, geom, config):
        txt = ""
        # Verifica a extensão. Se for SVG, fugimos do HTML para não acionar o bug do QGIS
        is_svg = config.get('ext', '') == '.svg'
        
        for f in feicoes_da_pagina:                    
            for col in colunas:
                try: 
                    valor = str(f.attribute(col) or '').strip()
                    if is_svg:
                        # Texto puro com quebra de linha normal (\n)
                        txt += f"{col}: {valor}\n"
                    else:
                        # HTML com negrito e quebra web (<br>)
                        txt += f"<b>{col}:</b> {valor}<br>"
                except: continue
        
        # O parâmetro is_html desliga automaticamente se for um arquivo SVG
        self._inserir_label_no_layout(
            layout, txt, geom['x_form'], geom['y_form'], 
            geom['w_form'], geom['h_form'], is_html=not is_svg
        )

    def _renderizar_modo_individual(self, layout, feicoes_da_pagina, colunas, geom, preset, orientacao, config):
        campo_atlas = config.get('campo_atlas')
        altura_linha = 5.5
        xi, yi = geom['x_ind_start'], geom['y_ind_min']

        if campo_atlas is None:
            f = feicoes_da_pagina[0]
            
            if orientacao == "Retrato":
                limite_colunas = 3
            else:
                if preset == "horizontal":
                    limite_colunas = 5 
                else:
                    limite_colunas = 3 

            for idx, col in enumerate(colunas):
                if idx > 0 and idx % limite_colunas == 0:
                    yi += altura_linha
                    xi = geom['x_ind_start']
                try:
                    val = f.attribute(col)
                    texto = f"{col}: {str(val).strip() if val is not None else ''}"
                    largura_ocupada = self._inserir_label_no_layout(layout, texto, xi, yi, auto_resize=True)
                    xi += largura_ocupada + 2.0 
                except: continue
        else:
            altura_total = len(feicoes_da_pagina) * altura_linha
            yi = (geom['limite_fundo'] - altura_total) if (geom['y_ind_min'] + altura_total) > geom['limite_fundo'] else geom['y_ind_min']

            for f in feicoes_da_pagina:
                xi = geom['x_ind_start']
                for col in colunas:
                    try:
                        val = f.attribute(col)
                        texto = f"{col}: {str(val).strip() if val is not None else ''}"
                        largura_ocupada = self._inserir_label_no_layout(layout, texto, xi, yi, auto_resize=True)
                        xi += largura_ocupada + 2.0
                    except: continue
                yi += altura_linha

    def adicionar_numeracao_pagina(self, layout, w_pg, h_pg, y_zero_folha, config):
        if not config.get('numeracao', False): return
        label_page = QgsLayoutItemLabel(layout)
        label_page.setText("[% @layout_page %]") 
        label_page.adjustSizeToText() 
        label_page.setReferencePoint(QgsLayoutItem.LowerRight)
        x, y = w_pg - 5, y_zero_folha + h_pg - 5
        label_page.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
        label_page.setZValue(100)
        layout.addLayoutItem(label_page)
    

    def _adicionar_grade_ao_mapa(self, map_item, config):
        """Adiciona a grade de coordenadas com cálculo automático de intervalo e estilo refinado."""
        if not config.get('inserir_grade', False): return
        
        # 1. Cria a Grade
        grid = QgsLayoutItemMapGrid(self.tr("Grade Automática"), map_item)
        grid.setEnabled(True)
        
        # 2. Estilo (Sólido ou Cruz)
        estilo = config.get('estilo_grade', 'solido')
        if estilo == 'cruz':
            grid.setStyle(QgsLayoutItemMapGrid.Cross)
            grid.setCrossLength(2.0)
            grid.setFrameStyle(QgsLayoutItemMapGrid.NoFrame) 
            # Como não alteramos o lineSymbol aqui, a cruz mantém a força padrão do QGIS!
        else:
            grid.setStyle(QgsLayoutItemMapGrid.Solid)
            grid.setFrameStyle(QgsLayoutItemMapGrid.Zebra)
            grid.setFrameWidth(2.0)
            
            # Aplicamos a leveza APENAS na linha sólida (e um pouco mais forte que antes)
            linha_simbolo = grid.lineSymbol().clone()
            linha_simbolo.setWidth(0.18) # Aumentado de 0.12 para 0.18
            linha_simbolo.setColor(QColor(130, 130, 130, 220)) # Cinza levemente mais escuro
            grid.setLineSymbol(linha_simbolo)
        
        # 3. Controle de Posição e Rotação das Coordenadas
        grid.setAnnotationEnabled(True)
        grid.setAnnotationFormat(QgsLayoutItemMapGrid.DecimalWithSuffix)
        
        is_geo = map_item.crs().isGeographic()
        grid.setAnnotationPrecision(3 if is_geo else 0) 
        
        # a) Desliga as coordenadas da Direita e do Topo
        grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Right)
        grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Top)
        
        # b) Garante que Baixo e Esquerda estejam ligados
        grid.setAnnotationDisplay(QgsLayoutItemMapGrid.ShowAll, QgsLayoutItemMapGrid.Bottom)
        grid.setAnnotationDisplay(QgsLayoutItemMapGrid.ShowAll, QgsLayoutItemMapGrid.Left)
        
        # c) Rotaciona as coordenadas da Esquerda para Vertical Ascendente
        grid.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)

        # 4. A MATEMÁTICA DO INTERVALO 
        ext = map_item.extent()
        largura_mapa = ext.width()
        
        if largura_mapa > 0:
            alvo = largura_mapa / 4.0
            magnitude = 10 ** math.floor(math.log10(alvo))
            multiplicador = alvo / magnitude
            
            if multiplicador < 1.5: fator = 1.0
            elif multiplicador < 3.5: fator = 2.0
            elif multiplicador < 7.5: fator = 5.0
            else: fator = 10.0
            
            intervalo_ideal = magnitude * fator
            
            grid.setIntervalX(intervalo_ideal)
            grid.setIntervalY(intervalo_ideal)
            
        # 5. Adiciona a grade à "pilha" de grades do mapa
        map_item.grids().addGrid(grid)