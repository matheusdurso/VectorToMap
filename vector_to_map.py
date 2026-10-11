# -*- coding: utf-8 -*-

# /***************************************************************************
#  VectorToMap - QGIS Plugin
#  Automates the generation of print layouts for vector features.
#  Author: Matheus Durso Neves Caetano
#
#  Copyright (C) 2026 Matheus Durso Neves Caetano
#  ***************************************************************************/

import re
import os
import gc
import traceback
import sys

# Importa o motor que fará o trabalho pesado (desenhar o mapa de fato)
# Mantém a separação de responsabilidades (Arquitetura MVC)
from .layout_engine import LayoutEngine

# Importações do PyQt (Controle da Interface Gráfica)
from qgis.PyQt import sip
from qgis.PyQt.QtCore import QTranslator, QCoreApplication, Qt, QTimer, QUrl, QSize
from qgis.PyQt.QtGui import QIcon, QPixmap, QColor, QFont, QDesktopServices
from qgis.PyQt.QtWidgets import (
    QAction, QCheckBox, QTableWidgetItem, QFrame, QPushButton,
    QDialogButtonBox, QButtonGroup, QApplication, QGridLayout,
    QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFontDialog, QGraphicsDropShadowEffect, QLineEdit, QWidget, QTextBrowser,
    QComboBox, QRadioButton, QSpinBox, QDoubleSpinBox, QScrollArea)

# Importações do QGIS Core (Lógica Espacial e Ferramentas Internas do QGIS)
from qgis.core import (
    QgsProject, QgsPrintLayout, QgsMapLayerProxyModel, QgsFeatureRequest, QgsSettings,
    QgsLayoutExporter, QgsExpression, QgsVectorLayer, NULL, Qgis, QgsMessageLog,
    QgsExpressionContext, QgsExpressionContextUtils, QgsLayoutItemMap
)

# IMPORTAÇÃO ADICIONADA: O construtor visual de expressões do próprio QGIS para o título dinâmico
from qgis.gui import QgsExpressionBuilderDialog

# Recursos compilados (Ícones e imagens) e o design bruto do Qt Designer
from .resources import * # noqa: F403
from .vector_to_map_dialog import VectorToMapDialog

# Adiciona o diretório atual ao PATH para garantir que bibliotecas embutidas funcionem
plugin_dir = os.path.dirname(__file__)
if plugin_dir not in sys.path:
    sys.path.append(plugin_dir)

# SDK do Sentry para monitoramento de erros (DevSecOps)
import sentry_sdk # noqa: E402


# ============================================================================
# --- ESTILOS GLOBAIS DA INTERFACE (CSS) ---
# ============================================================================
# Centralizar o CSS aqui facilita a manutenção do design.
# Evita poluir as funções lógicas com strings HTML/CSS gigantes.
CSS_INTERFACE = """
    QProgressBar { border: 1px solid #dcdcdc; border-radius: 4px; text-align: center; background-color: #f0f0f0; height: 14px; font-size: 10px; color: #333; }
    QProgressBar::chunk { background-color: #3498db; border-radius: 3px; }
    QProgressBar#previewProgressBar { height: 3px; }
    QScrollBar:vertical, QScrollBar:horizontal { border: none; background: #f8f8f8; width: 8px; height: 8px; margin: 0px; }
    QScrollBar::handle { background: #cccccc; border-radius: 4px; min-height: 20px; min-width: 20px; }
    QScrollBar::handle:hover { background: #707070; }
    QScrollBar::add-line, QScrollBar::sub-line { border: none; background: none; height: 0px; width: 0px; }
    QCheckBox, QLabel, QRadioButton, QgsMapLayerComboBox, QComboBox { font-size: 9pt; }
    QPushButton#pushButton_apoiar { background-color: #3498db; color: white; font-weight: bold; font-size: 13px; padding: 8px 20px; border: none; border-radius: 4px; }
    QPushButton#pushButton_apoiar:hover { background-color: #2980b9; }
    QPushButton#pushButton_bugreport { background-color: transparent; color: palette(text); font-size: 12px; padding: 8px 15px; border: 1px solid #cccccc; border-radius: 4px; }
    QPushButton#pushButton_bugreport:hover { background-color: palette(midlight); }
    QPushButton#pushButton_tutorial { background-color: #e74c3c; color: white; font-weight: bold; font-size: 12px; padding: 8px 15px; border: 1px solid #e74c3c; border-radius: 4px; }
    QPushButton#pushButton_tutorial:hover { background-color: #c0392b; }
    QgsFieldExpressionWidget QToolButton { background-color: #f8f9fa; }
    QgsFieldExpressionWidget QToolButton:hover { background-color: #e0e0e0; }
    QPushButton#btn_info_python { background-color: #3498db; color: #ffffff; border-radius: 11px; border: none; font-family: "Times New Roman", serif; font-weight: bold; font-size: 14px; padding-bottom: 2px; }
    QPushButton#btn_info_python:hover { background-color: #2980b9; }
"""

# ============================================================================
# --- JANELA DE BOAS-VINDAS E CONSENTIMENTO (SENTRY) ---
# ============================================================================
class BoasVindasDialog(QDialog):
    """Janela moderna exibida APENAS na primeira vez que o usuário abre o plugin."""
    def __init__(self, parent=None):
        super().__init__(parent)
        def tr(texto): return QCoreApplication.translate('@default', texto)

        self.setWindowTitle("VectorToMap")
        self.resize(600, 420)
        self.setWindowIcon(QIcon(':/plugins/vector_to_map/icon.png'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # Montagem do Layout Principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(35, 30, 35, 25)
        layout_principal.setSpacing(15)

        # Cabeçalho (Ícone + Título)
        layout_cabecalho = QHBoxLayout()
        layout_cabecalho.setSpacing(15)

        self.lbl_icone = QLabel()
        pixmap = QPixmap(':/plugins/vector_to_map/icon.png').scaled(52, 52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_icone.setPixmap(pixmap)
        layout_cabecalho.addWidget(self.lbl_icone)

        lbl_titulo = QLabel(tr("Bem-vindo ao VectorToMap!"))
        lbl_titulo.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2c3e50;")
        layout_cabecalho.addWidget(lbl_titulo)
        layout_cabecalho.addStretch()
        layout_principal.addLayout(layout_cabecalho)

        texto_welcome = tr("Obrigado por instalar o VectorToMap para automatizar sua cartografia técnica!")
        lbl_welcome = QLabel(texto_welcome)
        lbl_welcome.setWordWrap(True)
        lbl_welcome.setStyleSheet("font-size: 12pt; color: #34495e; margin-top: 5px;")
        layout_principal.addWidget(lbl_welcome)

        # Card Promocional Open-Source
        texto_pro_html = tr(
            "<div style='background-color: #f0f8ff; padding: 15px 20px; border-radius: 6px; border-left: 5px solid #3498db;'>"
            "<h3 style='margin: 0 0 10px 0; color: #2980b9; font-size: 14pt;'>🎉 Agora 100% Gratuito e Open-Source!</h3>"
            "<p style='margin: 0 0 12px 0; color: #2c3e50; font-size: 11pt; line-height: 1.4;'>"
            "Todos os recursos avançados da versão Pro, exportação sem limites e templates profissionais foram liberados para a comunidade.</p>"
            "<p style='margin: 0; font-size: 11pt; color: #34495e;'>"
            "☕ <b>Apoie para manter o projeto vivo:</b> <a href='https://buymeacoffee.com/matheusdurso' style='color: #e67e22; text-decoration: none; font-weight: bold;'>buymeacoffee.com/matheusdurso</a></p>"
            "</div>"
        )
        lbl_pro_texto = QLabel(texto_pro_html)
        lbl_pro_texto.setWordWrap(True)
        lbl_pro_texto.setOpenExternalLinks(True)
        lbl_pro_texto.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_principal.addWidget(lbl_pro_texto)
        layout_principal.addSpacing(5)

        # Divisória
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setFrameShadow(QFrame.Shadow.Sunken)
        linha.setStyleSheet("border: 1px solid #e0e0e0; background-color: transparent;")
        layout_principal.addWidget(linha)

        # Aviso de Privacidade Sentry
        texto_sentry = tr(
            "<b style='font-size: 11pt; color: #444;'>Relatórios de Erro:</b><br>"
            "<span style='font-size: 10pt; color: #666;'>Você aceita enviar relatórios automáticos e totalmente anônimos caso algum erro ocorra no sistema? "
            "Nenhuma informação pessoal ou dado geográfico será enviado.</span>"
        )
        lbl_sentry = QLabel(texto_sentry)
        lbl_sentry.setWordWrap(True)
        layout_principal.addWidget(lbl_sentry)
        layout_principal.addStretch()

        # Botões do Rodapé
        layout_botoes = QHBoxLayout()
        layout_botoes.setContentsMargins(0, 10, 0, 0)

        self.btn_recusar = QPushButton(tr("Não aceito, apenas começar"))
        self.btn_recusar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recusar.setStyleSheet("padding: 10px 18px; font-size: 11pt; color: #555; background-color: #f8f9fa; border: 1px solid #ccc; border-radius: 4px;")
        self.btn_recusar.clicked.connect(self.reject)

        self.btn_aceitar = QPushButton(tr("Aceitar e Começar"))
        self.btn_aceitar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aceitar.setDefault(True)
        self.btn_aceitar.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; font-weight: bold; font-size: 11pt; padding: 10px 25px; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.btn_aceitar.clicked.connect(self.accept)

        layout_botoes.addWidget(self.btn_recusar)
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_aceitar)

        layout_principal.addLayout(layout_botoes)


# ====================================================================================
# --- CLASSE PRINCIPAL: VectorToMap ---
# ====================================================================================
class VectorToMap:

    # ================================================================================
    # 1. CICLO DE VIDA E INTEGRAÇÃO QGIS
    # ================================================================================
    def __init__(self, iface):
        """Construtor. Executado uma única vez quando o QGIS inicia e carrega os plugins."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&VectorToMap')
        self.first_start = True

        # Delega o trabalho pesado de renderização para a classe especialista
        self.engine = LayoutEngine(self.iface)

        # Variáveis de Controle de Estado Global
        self.is_rendering = False
        self.ultimo_id_camada_ativa = None
        self.colunas_atuais = []

        self.preview_data_cache = None
        self.ultimo_id_camada = None
        self.cache_val_atlas = None
        self.clones_preview = []

        # i18n (Traduções): Detecta a linguagem do usuário.
        # Se for diferente de Português (PT), tenta carregar a língua correspondente.
        locale = QgsSettings().value('locale/userLocale', 'en')[0:2]
        if locale != 'pt':
            path = os.path.join(self.plugin_dir, 'i18n', f'vector_to_map_{locale}.qm')
            if not os.path.exists(path):
                # Fallback de Segurança: Se não achar Espanhol, carrega Inglês.
                path = os.path.join(self.plugin_dir, 'i18n', 'vector_to_map_en.qm')

            if os.path.exists(path):
                self.translator = QTranslator()
                self.translator.load(path)
                QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        """Helper para traduzir strings usando o motor do Qt."""
        return QCoreApplication.translate('VectorToMap', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        """Helper para adicionar botões no QGIS."""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip: action.setStatusTip(status_tip)
        if whats_this: action.setWhatsThis(whats_this)
        if add_to_toolbar: self.iface.addToolBarIcon(action)
        if add_to_menu: self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        """Cria as barras de ferramentas e atalhos na tela inicial do QGIS."""
        icon_path = ':/plugins/vector_to_map/icon.png'
        self.toolbar = self.iface.addToolBar(u'VectorToMap')
        self.toolbar.setObjectName(u'VectorToMap')

        self.action = self.add_action(
            icon_path,
            text=self.tr(u'VectorToMap'),
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=True,
            add_to_menu=True
        )

        # Registra o atalho global (Ctrl+Alt+C)
        self.iface.registerMainWindowAction(self.action, "Ctrl+Alt+C")

        # Altera o ícone da pasta pai no menu "Complementos"
        menu_complementos = self.iface.pluginMenu()
        icon_pro_path = ':/plugins/vector_to_map/icon.png'
        for acao_menu in menu_complementos.actions():
            if acao_menu.text() == self.tr(u'&VectorToMap'):
                acao_menu.setIcon(QIcon(icon_pro_path))
                break

    def unload(self):
        """Executado quando o plugin é desligado no Gerenciador de Complementos.
        Garante que limpamos a memória e removemos os botões da tela."""
        if hasattr(self, 'action') and self.action:
            self.iface.unregisterMainWindowAction(self.action)

        self.limpar_clones_preview()

        # Desconecta os Sinais Globais para não causar Crash (Memory Leak) com o QGIS
        try:
            QgsProject.instance().layersAdded.disconnect(self._filtrar_camadas_da_combo)
            QgsProject.instance().layersRemoved.disconnect(self._filtrar_camadas_da_combo)
            QgsProject.instance().mapThemeCollection().mapThemesChanged.disconnect(self.atualizar_combo_temas)
        except Exception: pass # Ignora se não estivesse conectado

        # Remove os ícones
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

        if hasattr(self, 'toolbar') and self.toolbar:
            if not sip.isdeleted(self.toolbar):
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.hide()
                self.toolbar.setParent(None)
                self.toolbar.deleteLater()
            del self.toolbar

        if hasattr(self, 'dlg') and self.dlg:
            if not sip.isdeleted(self.dlg):
                self.dlg.close()
                self.dlg.setParent(None)
                self.dlg.deleteLater()
            del self.dlg

        gc.collect() # Força o Python a esvaziar a RAM

    def _verificar_consentimento_sentry(self):
        """Pergunta ao usuário se ele aceita o rastreio de erros."""
        settings = QgsSettings()
        ja_perguntou = settings.value("/VectorToMap/sentry_ja_perguntou", False, type=bool)

        if not ja_perguntou:
            dialog = BoasVindasDialog(self.iface.mainWindow())
            # Compatibilidade QGIS 3 e 4
            if hasattr(dialog, 'exec'): aceitou = (dialog.exec() == 1)
            else: aceitou = (dialog.exec_() == 1)

            settings.setValue("/VectorToMap/enviar_erros_sentry", aceitou)
            settings.setValue("/VectorToMap/sentry_ja_perguntou", True)

        return settings.value("/VectorToMap/enviar_erros_sentry", False, type=bool)

    def inicializar_sentry(self):
        """Liga o Sentry filtrando rigorosamente qualquer dado pessoal (PII)."""
        self.sentry_ativo = False
        SENTRY_DSN_PROD = "INSERIR_DSN_VIA_CI_AQUI" # Será injetado pelo GitHub Actions

        def filtro_sentry(event, hint):
            log_msg = event.get('logentry', {}).get('message', '')
            if 'VectorToMap' not in log_msg:
                # Garante que só mandamos o erro pro Sentry se a culpa foi do nosso plugin
                is_our_bug = False
                try:
                    frames = event.get('exception', {}).get('values', [])[0].get('stacktrace', {}).get('frames', [])
                    for frame in frames:
                        if 'vector_to_map' in frame.get('filename', '').lower():
                            is_our_bug = True
                            break
                except Exception: pass
                if not is_our_bug: return None

            # Limpeza de Segurança: Mascara CPFs e E-mails
            try:
                frames = event.get('exception', {}).get('values', [])[0].get('stacktrace', {}).get('frames', [])
                for frame in frames:
                    if 'vars' in frame:
                        for key, value in frame['vars'].items():
                            val_str = str(value)
                            val_str = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b', '[CPF_OMITIDO]', val_str)
                            val_str = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_OMITIDO]', val_str)
                            frame['vars'][key] = val_str
            except Exception: pass

            return event

        try:
            if SENTRY_DSN_PROD != "INSERIR_DSN_VIA_CI_AQUI":
                sentry_sdk.init(
                    dsn=SENTRY_DSN_PROD,
                    send_default_pii=False,
                    release="vectortomap@3.9.0",
                    before_send=filtro_sentry
                )
                self.sentry_ativo = True
        except ImportError: pass
        except Exception: pass

    # ================================================================================
    # 2. RUN E MONTAGEM DA INTERFACE (Mestre da UI)
    # ================================================================================
    def run(self):
        """Maestro da Interface: Ocorre cada vez que o usuário clica no botão do plugin."""
        if self.first_start:
            self.first_start = False
            aceitou_sentry = self._verificar_consentimento_sentry()
            if aceitou_sentry:
                self.inicializar_sentry()

        ja_estava_aberta = hasattr(self, 'dlg') and self.dlg and not sip.isdeleted(self.dlg)

        if not ja_estava_aberta:
            # --- FASE 1: CONSTRUÇÃO E FIAÇÃO (Acontece APENAS na 1ª vez) ---
            self.dlg = VectorToMapDialog()
            self.dlg.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)

            # Conecta sinais globais do QGIS de forma segura
            try:
                QgsProject.instance().layersAdded.disconnect(self._filtrar_camadas_da_combo)
                QgsProject.instance().layersRemoved.disconnect(self._filtrar_camadas_da_combo)
            except TypeError: pass

            QgsProject.instance().layersAdded.connect(self._filtrar_camadas_da_combo)
            QgsProject.instance().layersRemoved.connect(self._filtrar_camadas_da_combo)

            self.dlg.setWindowFlags(self.dlg.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

            self._configurar_widgets_iniciais()
            self._conectar_sinais()
            self._configurar_janela()
            self.setup_ui_strings()

        # --- FASE 2: ATUALIZAÇÃO GERAL (Acontece TODA VEZ que reabre) ---
        self.colunas_atuais = []
        self.ultimo_id_camada_ativa = None

        self._filtrar_camadas_da_combo()
        self._aplicar_estilos()
        self.atualizar_textos_interface()

        if hasattr(self.dlg, 'tabWidget'):
            self.dlg.tabWidget.setCurrentIndex(0)

        if hasattr(self, 'atualizar_combo_temas'):
            self.atualizar_combo_temas()

        # Sincroniza a camada ativa do painel do QGIS com a ComboBox do Plugin
        camada_ativa = self.iface.activeLayer()
        if camada_ativa and isinstance(camada_ativa, QgsVectorLayer):
            self.dlg.mMapLayerComboBox.setLayer(camada_ativa)
            if hasattr(self.dlg, 'combo_camada_loc'):
                self.dlg.combo_camada_loc.setLayer(camada_ativa)
            self.atualizar_lista_atributos()

        # Desminimiza se estiver oculta
        if self.dlg.isMinimized():
            self.dlg.showNormal()

        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

        # Dispara a primeira Preview automaticamente
        QTimer.singleShot(200, self.atualizar_preview)

    def _aplicar_estilos(self):
        """Injeta o CSS consolidado (Azul Profissional & Clean) e aplica a sombra de folha."""
        self.dlg.setStyleSheet(CSS_INTERFACE)
        self.dlg.previewProgressBar.hide()
        self.dlg.progressBar.hide()
        self.dlg.lbl_preview.setFrameShape(QFrame.Shape.StyledPanel)

        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20); sombra.setXOffset(5); sombra.setYOffset(5); sombra.setColor(QColor(0, 0, 0, 80))
        if hasattr(self.dlg, 'lbl_preview'):
            self.dlg.lbl_preview.setGraphicsEffect(sombra)

    def setup_ui_strings(self):
        """Centraliza todos os Tooltips (Balões de dica) da interface para tradução limpa."""
        self.dlg.chk_modo_formulario.setToolTip(self.tr("Exibe todos os atributos em um bloco único de texto (HTML)."))
        self.dlg.chk_modo_individual.setToolTip(self.tr("Cria uma linha horizontal para cada feição (evita sobreposições)."))
        self.dlg.chk_selecionar_todos.setToolTip(self.tr("Marca ou desmarca todos os campos da lista de uma vez."))
        self.dlg.combo_presets.setToolTip(self.tr("Define o tamanho do mapa na folha (ex: 75% da página ou Quadrado)."))
        self.btn_render.setToolTip(self.tr("Gera uma prévia do layout com as configurações atuais."))
        self.btn_export.setToolTip(self.tr("Exporta os mapas diretamente como PDF, PNG ou JPG."))
        if hasattr(self.dlg, 'group_mapa_loc'):
            self.dlg.group_mapa_loc.setToolTip(self.tr("Adiciona um mapa de enquadramento geral no canto da folha."))

    def atualizar_textos_interface(self):
        """Força a tradução de widgets dinâmicos criados no Python (que o QtDesigner não vê)."""
        try:
            # ESCUDO CONTRA CRASH: Se a janela estiver morta, aborta silenciosamente.
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return

            if hasattr(self, 'btn_apoiar'): self.btn_apoiar.setText(self.tr("☕ Apoiar Desenvolvimento"))
            if hasattr(self, 'btn_bugreport'): self.btn_bugreport.setText(self.tr("🐞 Relatar Bug (GitHub)"))
            if hasattr(self, 'btn_tutorial'): self.btn_tutorial.setText(self.tr("▶ Assistir Tutorial"))

            self.dlg.combo_presets.blockSignals(True)
            try:
                idx_atual = self.dlg.combo_presets.currentIndex()
                self.dlg.combo_presets.clear()
                self.dlg.combo_presets.addItem(self.tr("Mapa Quadrado (Básico)"), "quadrado")
                self.dlg.combo_presets.addItem(self.tr("Mapa Horizontal (Básico)"), "horizontal")
                self.dlg.combo_presets.addItem(self.tr("Mapa Vertical (Básico)"), "vertical")

                # =================================================================
                # LÊ A PASTA DE TEMPLATES FÍSICA PARA POPULAR A COMBO
                # =================================================================
                locale = QgsSettings().value('locale/userLocale', 'en')[0:2]
                pasta_base_templates = os.path.join(self.plugin_dir, 'templates')

                if locale == 'pt': pasta_alvo = pasta_base_templates
                else:
                    pasta_alvo = os.path.join(pasta_base_templates, locale)
                    if not os.path.exists(pasta_alvo):
                        pasta_alvo_en = os.path.join(pasta_base_templates, 'en')
                        pasta_alvo = pasta_alvo_en if os.path.exists(pasta_alvo_en) else pasta_base_templates

                if os.path.exists(pasta_alvo):
                    for arquivo in os.listdir(pasta_alvo):
                        if arquivo.lower().endswith('.qpt'):
                            nome_amigavel = arquivo.replace('.qpt', '').replace('_', ' ').title()
                            nome_traduzido = self.tr(nome_amigavel)
                            caminho_completo = os.path.join(pasta_alvo, arquivo)
                            self.dlg.combo_presets.addItem(f"📄 {nome_traduzido}", caminho_completo)

                self.dlg.combo_presets.insertSeparator(self.dlg.combo_presets.count())
                self.dlg.combo_presets.addItem(self.tr("📂 Carregar Template Personalizado..."), "carregar_template")
                self.dlg.combo_presets.setCurrentIndex(idx_atual if idx_atual >= 0 else 0)
            finally:
                self.dlg.combo_presets.blockSignals(False)

            if hasattr(self, 'edit_busca_atributos') and not sip.isdeleted(self.edit_busca_atributos):
                self.edit_busca_atributos.setPlaceholderText(self.tr("🔍 Filtrar colunas..."))
        except RuntimeError: pass

    def _configurar_widgets_iniciais(self):
        """Popula todas as ComboBoxes, recria botões e define variáveis de estado inicial."""
        if hasattr(self.dlg, 'chk_preview_auto'):
            self.dlg.chk_preview_auto.setChecked(True)

        if hasattr(self.dlg, 'btn_cor_pagina'):
            self.dlg.btn_cor_pagina.setColor(QColor(255, 255, 255, 255))
            self.dlg.btn_cor_pagina.setAllowOpacity(True)
            self.dlg.btn_cor_pagina.colorChanged.connect(self.disparar_preview_se_autorizado)

        # Isolamento dos Radio Buttons de Orientação e Escala (Apenas 1 por vez)
        self.grupo_orientacao = QButtonGroup(self.dlg)
        self.grupo_orientacao.addButton(self.dlg.rb_retrato)
        self.grupo_orientacao.addButton(self.dlg.rb_paisagem)

        self.grupo_escala = QButtonGroup(self.dlg)
        self.grupo_escala.addButton(self.dlg.rb_escala_auto)
        self.grupo_escala.addButton(self.dlg.rb_escala_fixa)

        if hasattr(self.dlg, 'rb_atlas_nenhum'):
            self.grupo_atlas = QButtonGroup(self.dlg)
            self.grupo_atlas.addButton(self.dlg.rb_atlas_nenhum)
            self.grupo_atlas.addButton(self.dlg.rb_atlas_geral)
            self.grupo_atlas.addButton(self.dlg.rb_atlas_agrupar)

        # Setup Tamanhos de Página
        self.dlg.combo_tamanho_pagina.clear()
        tamanhos_disponiveis = [
            ("A5 (148 x 210 mm)", (148.0, 210.0)), ("A4 (210 x 297 mm)", (210.0, 297.0)),
            ("Letter (215.9 x 279.4 mm)", (215.9, 279.4)),
            ("A3 (297 x 420 mm)", (297.0, 420.0)), ("A2 (420 x 594 mm)", (420.0, 594.0)),
            ("A1 (594 x 841 mm)", (594.0, 841.0)), ("A0 (841 x 1189 mm)", (841.0, 1189.0))
        ]
        for texto, dimensoes in tamanhos_disponiveis:
            self.dlg.combo_tamanho_pagina.addItem(texto, dimensoes)
        self.dlg.combo_tamanho_pagina.setCurrentIndex(1) # Força o A4 como Padrão

        # Setup Escala
        self.dlg.combo_escala_fixa.clear()
        escalas = [
            ("1:1.000", 1000), ("1:5.000", 5000), ("1:10.000", 10000), ("1:25.000", 25000),
            ("1:50.000", 50000), ("1:100.000", 100000), ("1:250.000", 250000), ("1:500.000", 500000), ("1:1.000.000", 1000000)
        ]
        for texto, valor in escalas:
            self.dlg.combo_escala_fixa.addItem(texto, valor)
        self.dlg.combo_escala_fixa.insertSeparator(self.dlg.combo_escala_fixa.count())
        self.dlg.combo_escala_fixa.addItem(self.tr("Usar Coluna ou Expressão (ε)"), "expressao")
        self.dlg.combo_escala_fixa.setCurrentIndex(3)

        if hasattr(self.dlg, 'comboZoomOut'):
            self.dlg.comboZoomOut.clear()
            self.dlg.comboZoomOut.addItem(self.tr("0% (Justo)"), 0.0)
            self.dlg.comboZoomOut.addItem(self.tr("15%"), 15.0)
            self.dlg.comboZoomOut.addItem(self.tr("25% (Padrão)"), 25.0)
            self.dlg.comboZoomOut.addItem(self.tr("35%"), 35.0)
            self.dlg.comboZoomOut.addItem(self.tr("50%"), 50.0)
            self.dlg.comboZoomOut.addItem(self.tr("65%"), 65.0)
            self.dlg.comboZoomOut.addItem(self.tr("75%"), 75.0)
            self.dlg.comboZoomOut.addItem(self.tr("100% (Dobro)"), 100.0)
            self.dlg.comboZoomOut.insertSeparator(self.dlg.comboZoomOut.count())
            self.dlg.comboZoomOut.addItem(self.tr("Usar Coluna ou Expressão (ε)"), "expressao")
            self.dlg.comboZoomOut.setCurrentIndex(2)

        self.dlg.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        if hasattr(self.dlg, 'combo_camada_loc'):
            self.dlg.combo_camada_loc.setFilters(QgsMapLayerProxyModel.VectorLayer)

        if hasattr(self.dlg, 'rb_local_zoomout') and hasattr(self.dlg, 'rb_local_camada'):
            self.grupo_localizacao = QButtonGroup(self.dlg)
            self.grupo_localizacao.addButton(self.dlg.rb_local_zoomout)
            self.grupo_localizacao.addButton(self.dlg.rb_local_camada)
            self.dlg.rb_local_camada.setChecked(True)

        if hasattr(self.dlg, 'combo_local_zoomout'):
            self.dlg.combo_local_zoomout.clear()
            self.dlg.combo_local_zoomout.addItem(self.tr("2 x"), 2.0)
            self.dlg.combo_local_zoomout.addItem(self.tr("5 x"), 5.0)
            self.dlg.combo_local_zoomout.addItem(self.tr("10 x"), 10.0)
            self.dlg.combo_local_zoomout.addItem(self.tr("15 x"), 15.0)
            self.dlg.combo_local_zoomout.addItem(self.tr("20 x"), 20.0)
            self.dlg.combo_local_zoomout.addItem(self.tr("25 x"), 25.0)
            self.dlg.combo_local_zoomout.setCurrentIndex(1)

        opcoes_posicao = [
            (self.tr("Superior Esquerdo"), "SE"), (self.tr("Superior Direito"), "SD"),
            (self.tr("Inferior Esquerdo"), "IE"), (self.tr("Inferior Direito"), "ID")
        ]

        # Injeta as posições Nativas para as Decorações
        for combo_name in ['comboLegenda', 'comboEscala', 'comboNorte', 'comboPosLoc']:
            if hasattr(self.dlg, combo_name):
                combo = getattr(self.dlg, combo_name)
                combo.clear()
                for texto, dado in opcoes_posicao: combo.addItem(texto, dado)

        # Predefinições Estéticas
        if hasattr(self.dlg, 'comboLegenda'): self.dlg.comboLegenda.setCurrentIndex(2)
        if hasattr(self.dlg, 'comboEscala'): self.dlg.comboEscala.setCurrentIndex(0)
        if hasattr(self.dlg, 'comboNorte'): self.dlg.comboNorte.setCurrentIndex(1)
        if hasattr(self.dlg, 'comboPosLoc'): self.dlg.comboPosLoc.setCurrentIndex(3)

        if hasattr(self.dlg, 'combo_estilo_norte'):
            self.dlg.combo_estilo_norte.clear()
            self.dlg.combo_estilo_norte.addItem(self.tr("Minimalista"), "NorthArrow_02.svg")
            self.dlg.combo_estilo_norte.addItem(self.tr("Clássica (Seta N)"), "NorthArrow_01.svg")
            self.dlg.combo_estilo_norte.addItem(self.tr("Rosa dos Ventos"), "NorthArrow_04.svg")
            self.dlg.combo_estilo_norte.setCurrentIndex(0)
            self.dlg.combo_estilo_norte.currentIndexChanged.connect(self.disparar_preview_se_autorizado)

        if hasattr(self.dlg, 'comboGrid'):
            self.dlg.comboGrid.clear()
            self.dlg.comboGrid.addItem(self.tr("Linhas Sólidas + Zebra"), "solido")
            self.dlg.comboGrid.addItem(self.tr("Apenas Cruzes"), "cruz")

        if hasattr(self.dlg, 'btn_cor_fundo'):
            self.dlg.btn_cor_fundo.setColor(QColor(255, 255, 255, 255))
            self.dlg.btn_cor_fundo.setAllowOpacity(True)
            self.dlg.btn_cor_fundo.setToolTip(self.tr("Escolha a cor de fundo do mapa. Reduza a Opacidade para 0% para exportar transparente."))

        # Botões de Ação Inferiores (Rodapé)
        try:
            self.dlg.button_box.accepted.disconnect()
            self.dlg.button_box.rejected.disconnect()
        except Exception: pass

        self.dlg.button_box.clear()

        # Criação do Botão Redondo 'i' de Ajuda Flutuante
        self.btn_suporte_ajuda = QPushButton("i")
        self.btn_suporte_ajuda.setObjectName("btn_info_python")
        self.btn_suporte_ajuda.setFixedSize(22, 22)
        self.btn_suporte_ajuda.setToolTip(self.tr("Ajuda do VectorToMap"))

        self.dlg.button_box.addButton(self.btn_suporte_ajuda, QDialogButtonBox.ButtonRole.ActionRole)
        self.btn_export = QPushButton(self.tr("Exportar"))
        self.btn_render = QPushButton(self.tr("Preview"))
        self.btn_ok = QPushButton(self.tr("OK"))
        self.btn_cancel = QPushButton(self.tr("Cancelar"))

        self.dlg.button_box.addButton(self.btn_export, QDialogButtonBox.ButtonRole.ActionRole)
        self.dlg.button_box.addButton(self.btn_render, QDialogButtonBox.ButtonRole.ActionRole)
        self.dlg.button_box.addButton(self.btn_ok, QDialogButtonBox.ButtonRole.ActionRole)
        self.dlg.button_box.addButton(self.btn_cancel, QDialogButtonBox.ButtonRole.ActionRole)

        self.fonte_titulo = QFont("Arial", 20, QFont.Weight.Bold)

        # Adiciona evento de mudança ao título dinâmico (híbrido)
        if hasattr(self.dlg, 'lineEdit_titulo'):
            self.dlg.lineEdit_titulo.textChanged.connect(self.disparar_preview_se_autorizado)
        if hasattr(self.dlg, 'btn_fonte_titulo'):
            self.dlg.btn_fonte_titulo.clicked.connect(self.escolher_fonte_titulo)

        if hasattr(self.dlg, 'combo_alinhamento_titulo'):
            self.dlg.combo_alinhamento_titulo.clear()
            self.dlg.combo_alinhamento_titulo.addItem(self.tr("Esquerda"), Qt.AlignmentFlag.AlignLeft)
            self.dlg.combo_alinhamento_titulo.addItem(self.tr("Centro"), Qt.AlignmentFlag.AlignHCenter)
            self.dlg.combo_alinhamento_titulo.addItem(self.tr("Direita"), Qt.AlignmentFlag.AlignRight)
            self.dlg.combo_alinhamento_titulo.setCurrentIndex(1)
            self.dlg.combo_alinhamento_titulo.currentIndexChanged.connect(self.disparar_preview_se_autorizado)

        self.export_info = None
        self.abort_processing = False
        self.is_rendering = False

        self.timer_preview = QTimer()
        self.timer_preview.setSingleShot(True)

        self._adicionar_aba_sobre()

        if hasattr(self.dlg, 'tabWidget'):
            self.dlg.tabWidget.setCurrentIndex(0)

    def abrir_construtor_titulo(self, *args, **kwargs):
        """Abre o Construtor de Expressões do QGIS e injeta o resultado no título."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return

            camada = self.dlg.mMapLayerComboBox.currentLayer()
            if not camada: return

            # Abre a janela oficial do QGIS de Construção de Expressões
            dlg = QgsExpressionBuilderDialog(camada, "")
            dlg.setWindowTitle(self.tr("Inserir Expressão Dinâmica no Título"))

            # Carrega o contexto (Colunas e Variáveis do Projeto) para a janela
            contexto = QgsExpressionContext()
            contexto.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(camada))
            dlg.setExpressionContext(contexto)

            # Se o usuário clicar em "OK" na janela do QGIS
            if dlg.exec() == 1:
                expressao = dlg.expressionText()

                if expressao.strip():
                    texto_atual = self.dlg.lineEdit_titulo.text()

                    # Garante um espaço bonito se já tiver texto antes
                    separador = " " if texto_atual and not texto_atual.endswith(" ") else ""

                    # Injeta a fórmula do usuário cercada pelas chaves nativas do QGIS [% %]
                    novo_texto = f"{texto_atual}{separador}[% {expressao} %]"

                    self.dlg.lineEdit_titulo.setText(novo_texto)
                    self.disparar_preview_se_autorizado()

        except RuntimeError: pass

    def _conectar_sinais(self):
        """O cérebro das conexões Event-Driven: Tudo o que o usuário clica dispara as lógicas aqui."""
        self.btn_suporte_ajuda.clicked.connect(self.mostrar_tela_sobre)
        self.btn_export.clicked.connect(self.preparar_exportacao)
        self.btn_render.clicked.connect(self.atualizar_preview)
        self.btn_ok.clicked.connect(self.processar_clique_ok)
        self.btn_cancel.clicked.connect(self.cancelar_e_fechar)

        if hasattr(self.dlg, 'pushButton_ir_suporte'):
            self.dlg.pushButton_ir_suporte.clicked.connect(self.ir_para_suporte)

        self.timer_preview.timeout.connect(self.atualizar_preview)
        if hasattr(self.dlg, 'chk_preview_auto'):
            self.dlg.chk_preview_auto.stateChanged.connect(lambda state: self.timer_preview.start(250) if state == Qt.CheckState.Checked else None)

        self.dlg.mMapLayerComboBox.layerChanged.connect(self.configurar_escala_ao_mudar_camada)
        self.dlg.rb_escala_auto.toggled.connect(self.validar_geometria_escala)
        self.dlg.rb_escala_fixa.toggled.connect(self.validar_geometria_escala)

        # 👉 CONEXÃO DO NOVO BOTÃO EPSILON (TÍTULO DINÂMICO)
        if hasattr(self.dlg, 'btn_exp_titulo'):
            self.dlg.btn_exp_titulo.clicked.connect(self.abrir_construtor_titulo)

        if hasattr(self.dlg, 'combo_escala_fixa'):
            self.dlg.combo_escala_fixa.currentIndexChanged.connect(self.validar_geometria_escala)

        if hasattr(self.dlg, 'comboZoomOut'):
            self.dlg.comboZoomOut.currentIndexChanged.connect(self.validar_geometria_escala)

        self.dlg.chk_filtrar_feicoes.stateChanged.connect(self.atualizar_hierarquia_camadas)
        self.dlg.chk_exibir_so_camada_atual.stateChanged.connect(self.atualizar_hierarquia_camadas)
        self.dlg.chk_travar_camadas.stateChanged.connect(self.atualizar_estado_travar_estilos)

        self.dlg.chk_selecionar_todos.stateChanged.connect(self.marcar_desmarcar_todos)
        self.dlg.chk_numeracao.toggled.connect(self.disparar_preview_se_autorizado)

        if hasattr(self.dlg, 'chk_apenas_mapa'): self.dlg.chk_apenas_mapa.stateChanged.connect(self.disparar_preview_se_autorizado)
        if hasattr(self.dlg, 'btn_cor_fundo'): self.dlg.btn_cor_fundo.colorChanged.connect(self.disparar_preview_se_autorizado)
        if hasattr(self.dlg, 'chk_map_fundo_transp'): self.dlg.chk_map_fundo_transp.stateChanged.connect(self.disparar_preview_se_autorizado)
        if hasattr(self.dlg, 'chk_pag_fundo_transp'): self.dlg.chk_pag_fundo_transp.stateChanged.connect(self.disparar_preview_se_autorizado)

        for btn, topico in [('btn_presets', 'presets'), ('btn_info_ddo_auto', 'ddo_auto'), ('btn_info_ddo_fixa', 'ddo_fixa'), ('btn_info_agrupar', 'agrupar')]:
            if hasattr(self.dlg, btn): getattr(self.dlg, btn).clicked.connect(lambda _, t=topico, b=btn: self.mostrar_info(t, getattr(self.dlg, b)))

        # A LIXEIRA DE SINAIS (*args): Absorve parâmetros extras que o PyQt envia silenciosamente (como int do CheckBox) para não dar TypeError.
        def _ao_mudar_decoracao_principal(*args):
            self.atualizar_estado_decoracoes()
            self.disparar_preview_se_autorizado()

        for chk_name in ['chk_legenda', 'chk_escala', 'chk_norte', 'chk_grid']:
            if hasattr(self.dlg, chk_name): getattr(self.dlg, chk_name).stateChanged.connect(_ao_mudar_decoracao_principal)

        if hasattr(self.dlg, 'group_mapa_loc'): self.dlg.group_mapa_loc.toggled.connect(_ao_mudar_decoracao_principal)

        for chk_name in ['chk_add_raster', 'chk_incluir_raster']:
            if hasattr(self.dlg, chk_name): getattr(self.dlg, chk_name).stateChanged.connect(self.disparar_preview_se_autorizado)

        if hasattr(self.dlg, 'rb_local_zoomout'):
            self.dlg.rb_local_zoomout.toggled.connect(self.atualizar_estado_decoracoes)
            self.dlg.rb_local_zoomout.toggled.connect(self.disparar_preview_se_autorizado)

        if hasattr(self.dlg, 'combo_local_zoomout'): self.dlg.combo_local_zoomout.currentIndexChanged.connect(self.disparar_preview_se_autorizado)

        for combo_name in ['comboLegenda', 'comboEscala', 'comboNorte', 'comboPosLoc', 'comboGrid']:
            if hasattr(self.dlg, combo_name): getattr(self.dlg, combo_name).currentIndexChanged.connect(self.disparar_preview_se_autorizado)

        if hasattr(self.dlg, 'combo_camada_loc'): self.dlg.combo_camada_loc.layerChanged.connect(self.disparar_preview_se_autorizado)

        self.dlg.combo_presets.currentIndexChanged.connect(self._verificar_selecao_template)

        # Adiciona dezenas de gatilhos automáticos para disparar a Live Preview na tela
        widgets_preview = [
            self.dlg.combo_tamanho_pagina, self.dlg.rb_retrato, self.dlg.rb_paisagem,
            self.dlg.chk_modo_formulario, self.dlg.chk_modo_individual, self.dlg.chk_exibir_atributos
        ]

        if hasattr(self.dlg, 'rb_atlas_nenhum'):
            widgets_preview.extend([self.dlg.rb_atlas_nenhum, self.dlg.rb_atlas_geral, self.dlg.rb_atlas_agrupar])
            self.dlg.rb_atlas_nenhum.toggled.connect(self.atualizar_estado_filtro_feicoes)
            self.dlg.rb_atlas_geral.toggled.connect(self.atualizar_estado_filtro_feicoes)
            self.dlg.rb_atlas_agrupar.toggled.connect(self.atualizar_estado_filtro_feicoes)

        if hasattr(self.dlg, 'exp_atlas_agrupar'): self.dlg.exp_atlas_agrupar.fieldChanged.connect(self.disparar_preview_se_autorizado)
        if hasattr(self.dlg, 'exp_ddo_auto'): self.dlg.exp_ddo_auto.fieldChanged.connect(self.disparar_preview_se_autorizado)
        if hasattr(self.dlg, 'exp_ddo_fixa'): self.dlg.exp_ddo_fixa.fieldChanged.connect(self.disparar_preview_se_autorizado)

        for w in widgets_preview:
            if hasattr(w, 'currentIndexChanged'): w.currentIndexChanged.connect(self.disparar_preview_se_autorizado)
            elif hasattr(w, 'stateChanged'): w.stateChanged.connect(self.disparar_preview_se_autorizado)
            elif hasattr(w, 'toggled'): w.toggled.connect(self.disparar_preview_se_autorizado)

        # Remove e Re-conecta para evitar que o QGIS chame a função duas vezes em caso de reloads do plugin
        try:
            QgsProject.instance().mapThemeCollection().mapThemesChanged.disconnect(self.atualizar_combo_temas)
        except TypeError: pass
        QgsProject.instance().mapThemeCollection().mapThemesChanged.connect(self.atualizar_combo_temas)

        if hasattr(self.dlg, 'chk_usar_tema'):
            self.dlg.chk_usar_tema.toggled.connect(lambda estado: self.dlg.combo_temas.setEnabled(estado))
            self.dlg.chk_usar_tema.toggled.connect(self.atualizar_hierarquia_camadas)

        if hasattr(self.dlg, 'combo_temas'): self.dlg.combo_temas.currentIndexChanged.connect(self.disparar_preview_se_autorizado)

        # Sobrescreve o Resize nativo do QT para disparar preview quando a tela é aumentada com o mouse
        original_resize = self.dlg.resizeEvent
        def novo_resize_event(event):
            self.disparar_preview_se_autorizado()
            original_resize(event)
        self.dlg.resizeEvent = novo_resize_event

        self.configurar_escala_ao_mudar_camada()
        self.atualizar_hierarquia_camadas()
        self.atualizar_estado_decoracoes()

    def _configurar_janela(self):
        """Define o comportamento da janela com o Sistema Operacional e restaura tamanho salvo."""
        self.dlg.setWindowIcon(QIcon(':/plugins/vector_to_map/icon.png'))
        self.dlg.setWindowTitle("VectorToMap")

        self.dlg.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        if hasattr(self.dlg, 'lbl_aviso_feicoes'): self.dlg.lbl_aviso_feicoes.hide()

        settings = QgsSettings()
        geometria = settings.value("/VectorToMap/geometry")
        if geometria: self.dlg.restoreGeometry(geometria)
        else: self.dlg.resize(1100, 750)

        if hasattr(self.dlg, 'splitter'): self.dlg.splitter.setSizes([600, 500])

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        centro_tela = screen_geometry.center()
        geometria_janela = self.dlg.frameGeometry()
        geometria_janela.moveCenter(centro_tela)
        self.dlg.move(geometria_janela.topLeft())


    # ====================================================================================
    # --- 3. GESTÃO DE ESTADO DA INTERFACE (A LÓGICA DE TRAVAS RESTAURADA) ---
    # ====================================================================================

    def atualizar_hierarquia_camadas(self, *args, **kwargs):
        """Gerencia travas de interface e exibe avisos sobre camadas temporárias.
        Envolvido em try/except como escudo contra Crash do C++ se a janela for morta."""
        try:
            if self.is_rendering: return
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return

            usar_tema = hasattr(self.dlg, 'chk_usar_tema') and self.dlg.chk_usar_tema.isChecked()

            # A REGRA DE AUTORIDADE DO TEMA
            if usar_tema:
                self.dlg.chk_exibir_so_camada_atual.blockSignals(True)
                self.dlg.chk_exibir_so_camada_atual.setChecked(False)
                self.dlg.chk_exibir_so_camada_atual.setEnabled(False)
                self.dlg.chk_exibir_so_camada_atual.blockSignals(False)
            else:
                self.dlg.chk_exibir_so_camada_atual.setEnabled(True)

            self.atualizar_estado_filtro_feicoes()

            filtrar = self.dlg.chk_filtrar_feicoes.isChecked()
            exibir_atual = self.dlg.chk_exibir_so_camada_atual.isChecked()

            self.dlg.chk_travar_camadas.blockSignals(True)
            self.dlg.chk_travar_estilos.blockSignals(True)

            # Lógica de Dependência: Se for filtrar, a trava de camadas PRECISA estar ativa.
            try:
                if filtrar or exibir_atual:
                    self.dlg.chk_travar_camadas.setChecked(True)
                    self.dlg.chk_travar_camadas.setEnabled(False)
                else:
                    self.dlg.chk_travar_camadas.setEnabled(True)

                travado = self.dlg.chk_travar_camadas.isChecked()
                self.dlg.chk_travar_estilos.setEnabled(travado)

                if not travado:
                    self.dlg.chk_travar_estilos.setChecked(False)
            finally:
                self.dlg.chk_travar_camadas.blockSignals(False)
                self.dlg.chk_travar_estilos.blockSignals(False)

            # Exibe o aviso se o filtro de feições estiver ativo
            if hasattr(self.dlg, 'lbl_aviso_feicoes'):
                if filtrar:
                    self.dlg.lbl_aviso_feicoes.show()
                    self.dlg.lbl_aviso_feicoes.setText(self.tr("⚠️ O filtro de feições gera camadas temporárias internas para o layout."))
                else:
                    self.dlg.lbl_aviso_feicoes.hide()

            self.disparar_preview_se_autorizado()
        except RuntimeError: pass

    def atualizar_estado_filtro_feicoes(self, *args, **kwargs):
        """Bloqueia os filtros e o widget Epsilon dependendo do Radio Button escolhido."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            if not hasattr(self.dlg, 'rb_atlas_geral'): return

            is_geral = self.dlg.rb_atlas_geral.isChecked()
            is_agrupar = self.dlg.rb_atlas_agrupar.isChecked()
            usar_tema = hasattr(self.dlg, 'chk_usar_tema') and self.dlg.chk_usar_tema.isChecked()

            if is_geral:
                self.dlg.chk_filtrar_feicoes.blockSignals(True)
                self.dlg.chk_filtrar_feicoes.setChecked(False)
                self.dlg.chk_filtrar_feicoes.setEnabled(False)
                self.dlg.chk_filtrar_feicoes.blockSignals(False)
                if hasattr(self.dlg, 'groupAtributos'): self.dlg.groupAtributos.setEnabled(False)
            else:
                if usar_tema:
                    self.dlg.chk_filtrar_feicoes.blockSignals(True)
                    self.dlg.chk_filtrar_feicoes.setChecked(False)
                    self.dlg.chk_filtrar_feicoes.setEnabled(False)
                    self.dlg.chk_filtrar_feicoes.blockSignals(False)
                else:
                    self.dlg.chk_filtrar_feicoes.setEnabled(True)

                if hasattr(self.dlg, 'groupAtributos'): self.dlg.groupAtributos.setEnabled(True)

            if hasattr(self.dlg, 'exp_atlas_agrupar'):
                self.dlg.exp_atlas_agrupar.setEnabled(is_agrupar)
        except RuntimeError: pass

    def atualizar_estado_travar_estilos(self, *args, **kwargs):
        """Habilita o 'Travar Estilos' apenas se o 'Travar Camadas' estiver marcado."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            travado = self.dlg.chk_travar_camadas.isChecked()
            self.dlg.chk_travar_estilos.setEnabled(travado)

            if not travado:
                self.dlg.chk_travar_estilos.blockSignals(True)
                self.dlg.chk_travar_estilos.setChecked(False)
                self.dlg.chk_travar_estilos.blockSignals(False)
        except RuntimeError: pass

    def atualizar_estado_decoracoes(self, *args, **kwargs):
        """Habilita ou desabilita os controles das decorações com base nas checkboxes principais."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return

            # Controles do Mapa de Localização
            if hasattr(self.dlg, 'group_mapa_loc'):
                is_loc_ativo = self.dlg.group_mapa_loc.isChecked()
                if hasattr(self.dlg, 'rb_local_zoomout'):
                    is_modo_zoom = self.dlg.rb_local_zoomout.isChecked()
                    if hasattr(self.dlg, 'combo_local_zoomout'): self.dlg.combo_local_zoomout.setEnabled(is_loc_ativo and is_modo_zoom)
                    if hasattr(self.dlg, 'combo_camada_loc'): self.dlg.combo_camada_loc.setEnabled(is_loc_ativo and not is_modo_zoom)

            # TRAVA DE TEMPLATES (O Freio)
            if hasattr(self.dlg, 'combo_presets'):
                is_template = str(self.dlg.combo_presets.currentData()).endswith('.qpt')
                if is_template: return

            # Controles de Legenda e demais Decorações
            if hasattr(self.dlg, 'chk_legenda'):
                is_legenda_ativa = self.dlg.chk_legenda.isChecked()
                if hasattr(self.dlg, 'chk_add_raster'): self.dlg.chk_add_raster.setEnabled(is_legenda_ativa)
                if hasattr(self.dlg, 'comboLegenda'): self.dlg.comboLegenda.setEnabled(is_legenda_ativa)

            if hasattr(self.dlg, 'chk_norte'):
                is_norte_ativo = self.dlg.chk_norte.isChecked()
                if hasattr(self.dlg, 'comboNorte'): self.dlg.comboNorte.setEnabled(is_norte_ativo)
                if hasattr(self.dlg, 'combo_estilo_norte'): self.dlg.combo_estilo_norte.setEnabled(is_norte_ativo)

            if hasattr(self.dlg, 'chk_escala'):
                is_escala_ativa = self.dlg.chk_escala.isChecked()
                if hasattr(self.dlg, 'comboEscala'): self.dlg.comboEscala.setEnabled(is_escala_ativa)

            if hasattr(self.dlg, 'chk_grid'):
                is_grid_ativo = self.dlg.chk_grid.isChecked()
                if hasattr(self.dlg, 'comboGrid'): self.dlg.comboGrid.setEnabled(is_grid_ativo)
        except RuntimeError: pass

    def validar_geometria_escala(self, *args, **kwargs):
        """Gerencia a liberação dos botões de escala e as caixas de expressão (ε)."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            camada = self.dlg.mMapLayerComboBox.currentLayer()
            if not camada: return

            self.dlg.combo_escala_fixa.blockSignals(True)
            try:
                is_auto = self.dlg.rb_escala_auto.isChecked()
                is_fixa = self.dlg.rb_escala_fixa.isChecked()

                self.dlg.rb_escala_auto.setEnabled(True)

                # Lógica do Zoom Automático (comboZoomOut e exp_ddo_auto)
                if hasattr(self.dlg, 'comboZoomOut'):
                    self.dlg.comboZoomOut.setEnabled(is_auto)
                    usar_exp_auto = (self.dlg.comboZoomOut.currentData() == "expressao")
                else:
                    usar_exp_auto = True

                if hasattr(self.dlg, 'exp_ddo_auto'):
                    self.dlg.exp_ddo_auto.setEnabled(is_auto and usar_exp_auto)

                # Lógica da Escala Fixa (combo_escala_fixa e exp_ddo_fixa)
                usar_exp_fixa = False
                if hasattr(self.dlg, 'combo_escala_fixa'):
                    self.dlg.combo_escala_fixa.setEnabled(is_fixa)
                    usar_exp_fixa = (self.dlg.combo_escala_fixa.currentData() == "expressao")

                if hasattr(self.dlg, 'exp_ddo_fixa'):
                    self.dlg.exp_ddo_fixa.setEnabled(is_fixa and usar_exp_fixa)

            finally:
                self.dlg.combo_escala_fixa.blockSignals(False)

            self.disparar_preview_se_autorizado()
        except RuntimeError: pass

    def _verificar_selecao_template(self, *args, **kwargs):
        """Abre o seletor de arquivos se o usuário escolher carregar um template .qpt externo e tranca a interface."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg) or not hasattr(self.dlg, 'combo_presets'): return
            dados_atuais = self.dlg.combo_presets.currentData()

            if dados_atuais == "carregar_template":
                self.dlg.combo_presets.blockSignals(True)
                try:
                    caminho, _ = QFileDialog.getOpenFileName(self.dlg, self.tr("Selecionar Layout do QGIS"), "", "QGIS Template (*.qpt)")
                    if caminho:
                        nome_arquivo = os.path.basename(caminho).replace('.qpt', '').replace('_', ' ').title()
                        nome_amigavel = f"📂 {nome_arquivo}"
                        idx_insercao = self.dlg.combo_presets.count() - 2
                        self.dlg.combo_presets.insertItem(idx_insercao, nome_amigavel, caminho)
                        self.dlg.combo_presets.setCurrentIndex(idx_insercao)
                        dados_atuais = caminho
                    else:
                        self.dlg.combo_presets.setCurrentIndex(0)
                        dados_atuais = self.dlg.combo_presets.currentData()
                finally:
                    self.dlg.combo_presets.blockSignals(False)

            is_template = str(dados_atuais).endswith('.qpt') or str(dados_atuais) == "template"
            widgets_visiveis = (QComboBox, QCheckBox, QRadioButton, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QLabel)

            # Trava itens no groupBox_2 (Papel e Fundo)
            if hasattr(self.dlg, 'groupBox_2'):
                for child in self.dlg.groupBox_2.findChildren(widgets_visiveis):
                    nome = child.objectName()
                    if 'preset' in nome or nome == 'label': continue
                    child.setEnabled(not is_template)

            # Trava todo o groupAtributos
            if hasattr(self.dlg, 'groupAtributos'):
                self.dlg.groupAtributos.setEnabled(not is_template)
                if not is_template:
                    self.atualizar_estado_filtro_feicoes()

            # Trava itens no groupBox_5 (Decorações)
            if hasattr(self.dlg, 'groupBox_5'):
                for child in self.dlg.groupBox_5.findChildren(widgets_visiveis):
                    child.setEnabled(not is_template)

            self.disparar_preview_se_autorizado()
        except RuntimeError: pass


    # ====================================================================================
    # --- 4. GESTÃO DE ATRIBUTOS E COLUNAS ---
    # ====================================================================================

    def atualizar_lista_atributos(self):
        """Reconstrói a grade de colunas (Checkboxes) com base na camada escolhida."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            camada = self.dlg.mMapLayerComboBox.currentLayer()
            if not camada:
                self.dlg.tableWidget.setRowCount(0)
                return

            if camada.id() == self.ultimo_id_camada_ativa: return
            self.ultimo_id_camada_ativa = camada.id()

            marcados_antes = [cb.text() for cb in self.colunas_atuais if not sip.isdeleted(cb) and cb.isChecked()]

            if not hasattr(self, 'edit_busca_atributos') or sip.isdeleted(self.edit_busca_atributos):
                self.edit_busca_atributos = QLineEdit(self.dlg)
                self.edit_busca_atributos.setPlaceholderText(self.tr("🔍 Filtrar colunas..."))
                self.edit_busca_atributos.setClearButtonEnabled(True)
                self.edit_busca_atributos.textChanged.connect(self.filtrar_widgets_atributos)

                if hasattr(self.dlg, 'groupAtributos') and self.dlg.groupAtributos.layout():
                    self.dlg.groupAtributos.layout().insertWidget(0, self.edit_busca_atributos)

            self.atualizar_lista_colunas(camada)

            # RESTAURA A SELEÇÃO: Não deixa os filtros de feição desmarcarem as colunas sem querer
            for cb in self.colunas_atuais:
                if cb.text() in marcados_antes:
                    cb.blockSignals(True)
                    cb.setChecked(True)
                    cb.blockSignals(False)

            self.verificar_estado_selecionar_todos()
            self.atualizar_estado_modos_exibicao()
            self.atualizar_estado_filtro_feicoes()
        except RuntimeError: pass

    def atualizar_lista_colunas(self, camada):
        """Deleta os quadradinhos antigos e empilha os novos usando QGridLayout."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            container = self.dlg.scrollAreaWidgetContents

            # Garante que o layout seja Grid (conforme o TypeError evitado)
            if container.layout() and not isinstance(container.layout(), QGridLayout):
                QWidget().setLayout(container.layout())

            if not container.layout():
                layout = QGridLayout(container)
                container.setLayout(layout)
            else:
                layout = container.layout()

            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.colunas_atuais = []
            campos = list(camada.fields())

            for idx, campo in enumerate(campos):
                nome = campo.name()
                cb = QCheckBox(nome)
                cb.stateChanged.connect(self.atualizar_tabela_por_selecao)
                cb.stateChanged.connect(self.verificar_estado_selecionar_todos)
                cb.stateChanged.connect(self.atualizar_estado_modos_exibicao)
                cb.stateChanged.connect(self.disparar_preview_se_autorizado)

                self.colunas_atuais.append(cb)
                layout.addWidget(cb, idx // 3, idx % 3)
        except RuntimeError: pass

    def _organizar_grid_atributos(self):
        """Re-distribui os widgets visíveis no grid (após um filtro da barra de pesquisa)."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            container = self.dlg.scrollAreaWidgetContents
            layout = container.layout()
            if not layout: return

            for i in reversed(range(layout.count())): layout.takeAt(i)
            visiveis = [cb for cb in self.colunas_atuais if not cb.isHidden()]

            for idx, cb in enumerate(visiveis):
                row = idx // 3
                col = idx % 3
                layout.addWidget(cb, row, col)
        except RuntimeError: pass

    def filtrar_widgets_atributos(self, texto):
        """Esconde os CheckBoxes que não batem com a busca."""
        try:
            if not hasattr(self, 'colunas_atuais'): return
            texto = texto.lower().strip()
            for cb in self.colunas_atuais:
                cb.setVisible(texto in cb.text().lower() if texto else True)
            self._organizar_grid_atributos()
        except RuntimeError: pass

    def marcar_desmarcar_todos(self, state=None, *args, **kwargs):
        """Marca ou desmarca todas as colunas de uma vez e reseta o Cache da tabela."""
        try:
            check = (state == Qt.CheckState.Checked)
            if not self.colunas_atuais: return

            self.is_rendering = True
            for cb in self.colunas_atuais:
                cb.blockSignals(True)
                cb.setChecked(check)
                cb.blockSignals(False)
            self.is_rendering = False

            self.atualizar_tabela_por_selecao()
            self.atualizar_estado_modos_exibicao()

            self.preview_data_cache = None
            self.ultimo_id_camada = None
            self.disparar_preview_se_autorizado()
        except RuntimeError: pass

    def verificar_estado_selecionar_todos(self, *args, **kwargs):
        """O Checkbox mestre só fica marcado se 100% dos quadradinhos filhos estiverem marcados."""
        try:
            if not hasattr(self, 'colunas_atuais') or not self.colunas_atuais: return
            total = len(self.colunas_atuais)
            marcados = sum(1 for cb in self.colunas_atuais if cb.isChecked())

            self.dlg.chk_selecionar_todos.blockSignals(True)
            self.dlg.chk_selecionar_todos.setChecked(total > 0 and marcados == total)
            self.dlg.chk_selecionar_todos.blockSignals(False)
        except RuntimeError: pass

    def atualizar_estado_modos_exibicao(self, *args, **kwargs):
        """Ativa os botões de Formato de Tabela apenas se existir alguma coluna selecionada."""
        try:
            tem_selecao = any(cb.isChecked() for cb in self.colunas_atuais)

            self.dlg.chk_modo_formulario.setEnabled(tem_selecao)
            self.dlg.chk_modo_individual.setEnabled(tem_selecao)

            if tem_selecao:
                if not self.dlg.chk_modo_formulario.isChecked() and not self.dlg.chk_modo_individual.isChecked():
                    self.dlg.chk_modo_formulario.blockSignals(True)
                    try: self.dlg.chk_modo_formulario.setChecked(True)
                    finally: self.dlg.chk_modo_formulario.blockSignals(False)
            else:
                self.dlg.chk_modo_formulario.blockSignals(True)
                self.dlg.chk_modo_individual.blockSignals(True)
                try:
                    self.dlg.chk_modo_formulario.setChecked(False)
                    self.dlg.chk_modo_individual.setChecked(False)
                finally:
                    self.dlg.chk_modo_formulario.blockSignals(False)
                    self.dlg.chk_modo_individual.blockSignals(False)
        except RuntimeError: pass

    def atualizar_tabela_por_selecao(self, *args, **kwargs):
        """Lê o estado da UI e preenche as 5 primeiras linhas da Tabela Visual no plugin."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            camada = self.dlg.mMapLayerComboBox.currentLayer()
            tabela = self.dlg.tableWidget
            if not camada: return

            colunas = [cb.text() for cb in self.colunas_atuais if cb.isChecked()]
            tabela.clear()
            tabela.setColumnCount(len(colunas))
            tabela.setHorizontalHeaderLabels(colunas)

            if not colunas:
                tabela.setRowCount(0)
                return

            num_linhas = min(5, camada.featureCount())
            tabela.setRowCount(num_linhas)
            for i, feicao in enumerate(camada.getFeatures(QgsFeatureRequest().setLimit(num_linhas))):
                for j, col in enumerate(colunas):
                    tabela.setItem(i, j, QTableWidgetItem(str(feicao[col] if feicao[col] != NULL else "")))
            tabela.resizeColumnsToContents()
        except RuntimeError: pass


    # ====================================================================================
    # --- 5. RENDERIZAÇÃO E LAYOUT (Geração de DTO e Config) ---
    # ====================================================================================

    def configurar_escala_ao_mudar_camada(self, *args, **kwargs):
        """Comunica aos painéis de Expressão (SQL) qual é a camada fonte para autocompletar fórmulas."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            camada = self.dlg.mMapLayerComboBox.currentLayer()
            if not camada: return

            if hasattr(self.dlg, 'exp_ddo_auto'): self.dlg.exp_ddo_auto.setLayer(camada)
            if hasattr(self.dlg, 'exp_ddo_fixa'): self.dlg.exp_ddo_fixa.setLayer(camada)
            if hasattr(self.dlg, 'exp_atlas_agrupar'): self.dlg.exp_atlas_agrupar.setLayer(camada)

            if camada.id() != self.ultimo_id_camada_ativa:
                if hasattr(self.dlg, 'combo_camada_loc'):
                    self.dlg.combo_camada_loc.blockSignals(True)
                    self.dlg.combo_camada_loc.setLayer(camada)
                    self.dlg.combo_camada_loc.blockSignals(False)

                if hasattr(self.dlg, 'exp_atlas_agrupar') and camada.fields().count() > 0:
                    primeira_coluna = camada.fields().at(0).name()
                    try:
                        self.dlg.exp_atlas_agrupar.blockSignals(True)
                        self.dlg.exp_atlas_agrupar.setField(primeira_coluna)
                    finally:
                        self.dlg.exp_atlas_agrupar.blockSignals(False)

                self.dlg.tableWidget.setRowCount(0)
                self.dlg.tableWidget.setColumnCount(0)
                self.dlg.tableWidget.clear()

                self.dlg.rb_escala_auto.setChecked(True)
                self.atualizar_lista_atributos()
                self.validar_geometria_escala()
        except RuntimeError: pass

    def obter_dados_preview(self):
        """Processa a expressão do Atlas para puxar a amostra que formará a Live Preview."""
        if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return None
        camada = self.dlg.mMapLayerComboBox.currentLayer()
        if not camada:
            self.preview_data_cache = None
            return None

        config = self._gerar_config_atual()
        campo_atlas = config.get('campo_atlas')

        # Se o cache está vazio OU o usuário trocou a camada/fórmula, calculamos de novo
        if (self.preview_data_cache is None or self.ultimo_id_camada != camada.id() or self.cache_val_atlas != campo_atlas):
            self.ultimo_id_camada = camada.id()
            self.cache_val_atlas = campo_atlas

            request_amostra = QgsFeatureRequest().setLimit(1)
            sample_f = next(camada.getFeatures(request_amostra), None)

            if sample_f:
                if campo_atlas is None:
                    self.preview_data_cache = [sample_f]
                elif campo_atlas == "__ALL_FEATURES__":
                    self.preview_data_cache = ["ALL"]
                else:
                    # MAGIA: Lê e executa a expressão matemática para a feição de amostra
                    exp = QgsExpression(campo_atlas)
                    contexto = QgsExpressionContext()
                    contexto.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(camada))
                    exp.prepare(contexto)
                    contexto.setFeature(sample_f)
                    val_amostra = exp.evaluate(contexto)

                    if val_amostra is None or val_amostra == NULL:
                        filtro = f'({campo_atlas}) IS NULL'
                    else:
                        filtro = f'({campo_atlas}) = {QgsExpression.quotedValue(val_amostra)}'

                    request_filtrado = QgsFeatureRequest().setFilterExpression(filtro)
                    self.preview_data_cache = list(camada.getFeatures(request_filtrado))
            else:
                self.preview_data_cache = None

        return self.preview_data_cache

    def _gerar_config_atual(self, feicoes_amostra=None):
        """
        A CAIXA PRETA SEGURO: Coleta todos os estados visuais em um DTO (Dicionário).
        Usa getattr e hasattr originais protegendo contra o Memory Leak do C++ no QGIS,
        pois nunca invoca default widgets (ex: QComboBox()) como argumento de escape.
        """
        if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return {}

        container = self.dlg.scrollAreaWidgetContents
        colunas_selecionadas = [cb.text() for cb in container.findChildren(QCheckBox) if cb.isChecked()]

        campo_atlas = None
        if hasattr(self.dlg, 'rb_atlas_geral') and self.dlg.rb_atlas_geral.isChecked():
            campo_atlas = "__ALL_FEATURES__"
        elif hasattr(self.dlg, 'rb_atlas_agrupar') and self.dlg.rb_atlas_agrupar.isChecked():
            campo_atlas = self.dlg.exp_atlas_agrupar.asExpression()

        return {
            'preset': self.dlg.combo_presets.currentData() if hasattr(self.dlg, 'combo_presets') else None,
            'orientacao': "Retrato" if (hasattr(self.dlg, 'rb_retrato') and self.dlg.rb_retrato.isChecked()) else "Paisagem",
            'tamanho_pg': self.dlg.combo_tamanho_pagina.currentData() if hasattr(self.dlg, 'combo_tamanho_pagina') else None,
            'campo_atlas': campo_atlas,
            'cor_pagina': self.dlg.btn_cor_pagina.color() if hasattr(self.dlg, 'btn_cor_pagina') else QColor(255, 255, 255),
            'cor_fundo': self.dlg.btn_cor_fundo.color() if hasattr(self.dlg, 'btn_cor_fundo') else QColor(255, 255, 255),
            'apenas_mapa': self.dlg.chk_apenas_mapa.isChecked() if hasattr(self.dlg, 'chk_apenas_mapa') else False,
            'texto_titulo': self.dlg.lineEdit_titulo.text() if hasattr(self.dlg, 'lineEdit_titulo') else '',
            'fonte_titulo': getattr(self, 'fonte_titulo', QFont()),
            'alinhamento_titulo': self.dlg.combo_alinhamento_titulo.currentData() if hasattr(self.dlg, 'combo_alinhamento_titulo') else Qt.AlignmentFlag.AlignHCenter,

            # --- SEÇÃO DE ESCALA E FILTROS ---
            'escala_fixa': self.dlg.rb_escala_fixa.isChecked() if hasattr(self.dlg, 'rb_escala_fixa') else False,
            'escala_val': self.dlg.combo_escala_fixa.currentData() if hasattr(self.dlg, 'combo_escala_fixa') else 10000.0,
            'filtrar_feicoes': self.dlg.chk_filtrar_feicoes.isChecked() if hasattr(self.dlg, 'chk_filtrar_feicoes') else False,
            'exibir_so_camada_atual': self.dlg.chk_exibir_so_camada_atual.isChecked() if hasattr(self.dlg, 'chk_exibir_so_camada_atual') else False,
            'travar_camadas': self.dlg.chk_travar_camadas.isChecked() if hasattr(self.dlg, 'chk_travar_camadas') else False,
            'travar_estilos': self.dlg.chk_travar_estilos.isChecked() if hasattr(self.dlg, 'chk_travar_estilos') else False,

            # --- SEÇÃO DE ATRIBUTOS E EXPRESSÕES (DDO) ---
            'colunas': colunas_selecionadas,
            'exibir_atributos': self.dlg.chk_exibir_atributos.isChecked() if hasattr(self.dlg, 'chk_exibir_atributos') else True,
            'modo_formulario': self.dlg.chk_modo_formulario.isChecked() if hasattr(self.dlg, 'chk_modo_formulario') else False,
            'modo_individual': self.dlg.chk_modo_individual.isChecked() if hasattr(self.dlg, 'chk_modo_individual') else False,
            'numeracao': self.dlg.chk_numeracao.isChecked() if hasattr(self.dlg, 'chk_numeracao') else False,
            'escala_auto_exp': self.dlg.exp_ddo_auto.asExpression() if hasattr(self.dlg, 'exp_ddo_auto') and getattr(self.dlg, 'rb_escala_auto', None) and self.dlg.rb_escala_auto.isChecked() else "",
            'escala_fixa_exp': self.dlg.exp_ddo_fixa.asExpression() if hasattr(self.dlg, 'exp_ddo_fixa') and getattr(self.dlg, 'rb_escala_fixa', None) and self.dlg.rb_escala_fixa.isChecked() else "",

            # --- SEÇÃO DE DECORAÇÕES E MAPA LOCATOR ---
            'map_fundo_transp': self.dlg.chk_map_fundo_transp.isChecked() if hasattr(self.dlg, 'chk_map_fundo_transp') else False,
            'pag_fundo_transp': self.dlg.chk_pag_fundo_transp.isChecked() if hasattr(self.dlg, 'chk_pag_fundo_transp') else False,
            'inserir_escala': self.dlg.chk_escala.isChecked() if hasattr(self.dlg, 'chk_escala') else False,
            'inserir_norte': self.dlg.chk_norte.isChecked() if hasattr(self.dlg, 'chk_norte') else False,
            'inserir_legenda': self.dlg.chk_legenda.isChecked() if hasattr(self.dlg, 'chk_legenda') else False,
            'add_raster_legend': self.dlg.chk_add_raster.isChecked() if hasattr(self.dlg, 'chk_add_raster') else False,
            'pos_legenda': self.dlg.comboLegenda.currentData() if hasattr(self.dlg, 'comboLegenda') else "IE",
            'pos_escala': self.dlg.comboEscala.currentData() if hasattr(self.dlg, 'comboEscala') else "SE",
            'pos_norte': self.dlg.comboNorte.currentData() if hasattr(self.dlg, 'comboNorte') else "SD",
            'inserir_grade': self.dlg.chk_grid.isChecked() if hasattr(self.dlg, 'chk_grid') else False,
            'estilo_grade': self.dlg.comboGrid.currentData() if hasattr(self.dlg, 'comboGrid') else "solido",

            'inserir_mapa_loc': self.dlg.group_mapa_loc.isChecked() if hasattr(self.dlg, 'group_mapa_loc') else False,
            'add_raster_loc': self.dlg.chk_incluir_raster.isChecked() if hasattr(self.dlg, 'chk_incluir_raster') else False,
            'camada_loc': self.dlg.combo_camada_loc.currentLayer() if hasattr(self.dlg, 'combo_camada_loc') else None,
            'pos_mapa_loc': self.dlg.comboPosLoc.currentData() if hasattr(self.dlg, 'comboPosLoc') else "ID",
            'zoom_out_auto': self.dlg.comboZoomOut.currentData() if hasattr(self.dlg, 'comboZoomOut') else 25.0,

            'estilo_norte': self.dlg.combo_estilo_norte.currentData() if hasattr(self.dlg, 'combo_estilo_norte') else "NorthArrow_02.svg",
            'modo_local': "zoom" if (hasattr(self.dlg, 'rb_local_zoomout') and self.dlg.rb_local_zoomout.isChecked()) else "camada",
            'fator_zoom_local': self.dlg.combo_local_zoomout.currentData() if hasattr(self.dlg, 'combo_local_zoomout') else 10.0,
            'usar_tema': self.dlg.chk_usar_tema.isChecked() if hasattr(self.dlg, 'chk_usar_tema') else False,
            'tema_selecionado': self.dlg.combo_temas.currentText() if hasattr(self.dlg, 'combo_temas') else ""
        }

    def disparar_preview_se_autorizado(self, *args, **kwargs):
        """Liga o timer da Live Preview apenas se a janelinha existir e estiver visível na tela."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg) or not self.dlg.isVisible() or self.is_rendering:
                return
            if hasattr(self.dlg, 'chk_preview_auto') and self.dlg.chk_preview_auto.isChecked():
                if hasattr(self, 'timer_preview'):
                    self.timer_preview.start(300)
        except RuntimeError: pass

    def atualizar_preview(self, *args, **kwargs):
        """A Mágica da Visualização: Cria um Layout Cego (Nativo) na RAM, bate a foto e injeta na nossa Janela."""
        try:
            if self.is_rendering or not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg) or not self.dlg.isVisible(): return

            self.is_rendering = True
            layout = None
            try:
                self.dlg.previewProgressBar.show()
                self.dlg.previewProgressBar.setRange(0, 0)
                QCoreApplication.processEvents() # Dá chance ao Windows/Mac desenharem a barra

                self.dlg.mMapLayerComboBox.blockSignals(True)
                self.limpar_clones_preview()

                feicoes = self.obter_dados_preview()
                camada = self.dlg.mMapLayerComboBox.currentLayer()

                if feicoes and camada:
                    layout = QgsPrintLayout(QgsProject.instance())
                    layout.initializeDefaults()
                    config = self._gerar_config_atual()

                    campo_atlas = config.get('campo_atlas')
                    nome_sufixo_preview = "Geral" if campo_atlas == "__ALL_FEATURES__" else ("Filtro" if campo_atlas else "Preview")

                    # Delega o esforço pesado para a classe especialista (LayoutEngine)
                    self.engine.montar_design_da_pagina(layout, camada, feicoes, config['preset'], config['orientacao'], config, pagina_index=0, is_preview=True, nome_sufixo=nome_sufixo_preview)

                    layout.refresh()

                    # Exporta a foto cega numa resolução levíssima (72 DPI) para ser instantâneo
                    exporter = QgsLayoutExporter(layout)
                    image = exporter.renderPageToImage(0, QSize(), 72.0)
                    if not image.isNull():
                        self.dlg.lbl_preview.setPixmap(QPixmap.fromImage(image).scaled(self.dlg.lbl_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.dlg.lbl_preview.clear()

            except Exception as e:
                QgsMessageLog.logMessage(f"Erro na Preview: {str(e)}", "VectorToMap", Qgis.MessageLevel.Warning)

            finally:
                self.dlg.mMapLayerComboBox.blockSignals(False)

                if layout:
                    layout.pageCollection().clear()
                    sip.delete(layout) # Destrói o Layout da RAM completamente

                self.limpar_clones_preview()
                QTimer.singleShot(200, self._liberar_render)
        except RuntimeError: pass

    def _liberar_render(self):
        """Desmarca a trava permitindo novos cliques sem causar enfileiramento (Stack Overflow)."""
        self.is_rendering = False
        try:
            if hasattr(self, 'dlg') and self.dlg and not sip.isdeleted(self.dlg) and hasattr(self.dlg, 'previewProgressBar') and not sip.isdeleted(self.dlg.previewProgressBar):
                self.dlg.previewProgressBar.hide()
                self.dlg.previewProgressBar.setRange(0, 100)
        except RuntimeError: pass

    def limpar_clones_preview(self):
        """Percorre a árvore de camadas procurando o carimbo secreto do plugin e deleta o lixo da Memory Layer."""
        camadas_para_deletar = []
        for layer_id, layer in QgsProject.instance().mapLayers().items():
            if layer.customProperty("vtm_is_preview_temp"):
                camadas_para_deletar.append(layer_id)

        if camadas_para_deletar:
            QgsProject.instance().removeMapLayers(camadas_para_deletar)

        if hasattr(self, 'clones_preview') and self.clones_preview: self.clones_preview.clear()
        if hasattr(self, 'engine') and self.engine.clones_preview: self.engine.clones_preview.clear()


    # ====================================================================================
    # --- 6. EXPORTAÇÃO E GERAÇÃO DE LOTE (Batch Processing) ---
    # ====================================================================================

    def preparar_exportacao(self, *args, **kwargs):
        """Mostra o painel 'Salvar Como...' interceptando e armazenando a extensão desejada (PNG, PDF, SVG, etc)."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            camada = self.dlg.mMapLayerComboBox.currentLayer()
            if not camada: return

            settings = QgsSettings()
            ultimo_dir = settings.value("/VectorToMap/ultimo_diretorio_exportacao", os.path.expanduser("~"))
            nome_sugerido = os.path.join(ultimo_dir, f"Mapas_{camada.name()}")
            filtros = "PDF (*.pdf);;SVG (*.svg);;PNG (*.png);;JPEG (*.jpg)"

            caminho_arquivo, filtro_selecionado = QFileDialog.getSaveFileName(self.dlg, self.tr("Exportar Mapas"), nome_sugerido, filtros)

            if caminho_arquivo:
                diretorio_escolhido = os.path.dirname(caminho_arquivo)
                settings.setValue("/VectorToMap/ultimo_diretorio_exportacao", diretorio_escolhido)

                ext = ".pdf"
                if "PNG" in filtro_selecionado: ext = ".png"
                elif "JPEG" in filtro_selecionado: ext = ".jpg"
                elif "SVG" in filtro_selecionado: ext = ".svg"

                if not caminho_arquivo.lower().endswith(ext): caminho_arquivo += ext

                # Formatos de Imagem e SVG forçam a exportação individual obrigatoriamente
                is_individual = self.dlg.chk_export_individual.isChecked() if hasattr(self.dlg, 'chk_export_individual') else (ext in [".png", ".jpg", ".svg"])

                self.export_info = {'path': caminho_arquivo, 'ext': ext, 'individual': is_individual}
                self.processar_clique_ok() # Engata a primeira marcha da exportação de verdade
        except RuntimeError: pass

    def processar_clique_ok(self, *args, **kwargs):
        """O Operador Logístico: Executa a equação SQL de Atlas para montar a lista de Lotes."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            camada = self.dlg.mMapLayerComboBox.currentLayer()
            if not camada: return

            self.abort_processing = False

            try:
                config = self._gerar_config_atual()
                campo_atlas = config.get('campo_atlas')
                paginas_dados = []

                # Categoria 1: Cada feição é um mapa sozinho
                if campo_atlas is None:
                    request = QgsFeatureRequest()
                    for f in camada.getFeatures(request): paginas_dados.append({'feicoes': [f], 'valor_grupo': None})
                # Categoria 2: Mapa grandão com todas as feições
                elif campo_atlas == "__ALL_FEATURES__":
                    paginas_dados.append({'feicoes': ["ALL"], 'valor_grupo': "Geral"})
                # Categoria 3: DDO Atlas Inteligente (Agrupa por valores idênticos)
                else:
                    exp = QgsExpression(campo_atlas)
                    contexto = QgsExpressionContext()
                    contexto.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(camada))
                    exp.prepare(contexto)

                    grupos = {}
                    for f in camada.getFeatures():
                        contexto.setFeature(f)
                        val = exp.evaluate(contexto)
                        val_chave = "Null" if val is None or val == NULL else str(val).strip()
                        if val_chave not in grupos: grupos[val_chave] = []
                        grupos[val_chave].append(f) # Reúne toda a família na mesma casa

                    chaves_ordenadas = sorted(grupos.keys())
                    for chave in chaves_ordenadas: paginas_dados.append({'feicoes': grupos[chave], 'valor_grupo': chave})

                if paginas_dados:
                    # Entrega a lista de lotes organizados para a Máquina de Escrever Central
                    self.criar_layout_multi_paginas(camada, paginas_dados, export_info=getattr(self, 'export_info', None))

            except RuntimeError as e:
                self.iface.messageBar().pushMessage(self.tr("Aviso"), str(e), level=Qgis.MessageLevel.Warning)

            except Exception as e:
                erro_detalhado = traceback.format_exc()
                if getattr(self, 'sentry_ativo', False):
                    try: sentry_sdk.capture_exception(e); sentry_sdk.flush(timeout=2.0)
                    except Exception: pass
                self.iface.messageBar().pushMessage(self.tr("Erro"), f"{str(e)}. {self.tr('Veja o console para detalhes.')}", level=Qgis.MessageLevel.Critical)
                QgsMessageLog.logMessage(erro_detalhado, "VectorToMap", Qgis.MessageLevel.Critical)

            finally:
                self.export_info = None
        except RuntimeError: pass

    def criar_layout_multi_paginas(self, camada, paginas_dados, export_info=None):
        """O Chefe da Linha de Produção: Tranca a tela, varre a lista, salva os arquivos e avisa que acabou."""
        self.is_rendering = True
        self.engine.abort_processing = False
        self.set_ui_enabled(False)

        try:
            project = QgsProject.instance()
            manager = project.layoutManager()

            is_individual = export_info.get('individual', False) if export_info else False
            base_path = export_info.get('path', '') if export_info else ''
            ext = export_info.get('ext', '') if export_info else ''
            base_sem_ext = base_path[:-len(ext)] if ext else base_path

            config = self._gerar_config_atual()

            if export_info:
                config['ext'] = ext
                config['base_sem_ext'] = base_sem_ext
                # Verifica no HD se não vamos destruir sem querer arquivos antigos do usuário
                pode_continuar = self._verificar_sobrescrita_arquivos(base_sem_ext, ext, paginas_dados, is_individual)
                if not pode_continuar:
                    self.is_rendering = False
                    self.engine.abort_processing = True
                    return

            self.dlg.progressBar.show()
            self.dlg.progressBar.setRange(0, len(paginas_dados))
            self.dlg.progressBar.setValue(0)

            def atualizar_progresso(valor): self.dlg.progressBar.setValue(valor)

            layout_persistente = None

            if is_individual:
                self.engine.exportar_paginas_individuais(project, camada, paginas_dados, config, progress_callback=atualizar_progresso)
            else:
                layout_persistente = self.engine.montar_layout_persistente(project, manager, camada, paginas_dados, config, progress_callback=atualizar_progresso)

            if not self.engine.abort_processing:
                if export_info:
                    # Geração do Arquivo PDF unificado de dezenas de páginas
                    if not is_individual and ext == ".pdf" and layout_persistente:
                        layout_persistente.refresh()
                        exporter = QgsLayoutExporter(layout_persistente)
                        settings = QgsLayoutExporter.PdfExportSettings()
                        settings.dpi = 300
                        exporter.exportToPdf(base_path, settings)

                        # QUEBRA DOS ELOS VITAIS: Impede o Segfault do C++ ao fechar o projeto QGIS depois da exportação.
                        for item in layout_persistente.items():
                            if isinstance(item, QgsLayoutItemMap):
                                item.setKeepLayerSet(False)
                                item.setLayers([])

                        layout_persistente.pageCollection().clear()
                        layout_persistente.deleteLater()
                        layout_persistente = None

                    dir_path = os.path.dirname(base_path)
                    url_pasta = QUrl.fromLocalFile(dir_path).toString()
                    texto_sucesso = self.tr("Layout exportado com sucesso para")
                    mensagem_html = f"{texto_sucesso} <a href='{url_pasta}' style='color: #005e00; text-decoration: underline;'>{dir_path}</a>"

                    self.iface.messageBar().pushMessage(self.tr("Exportar layout"), mensagem_html, level=Qgis.MessageLevel.Success, duration=0)

                    # Automação de UX: Abre o navegador de arquivos se o usuário marcou a opção
                    if hasattr(self.dlg, 'chk_abrir_arquivo') and self.dlg.chk_abrir_arquivo.isChecked():
                        url_pasta = QUrl.fromLocalFile(dir_path)
                        QDesktopServices.openUrl(url_pasta)
                        if not is_individual and ext == ".pdf":
                            url_arquivo = QUrl.fromLocalFile(base_path)
                            QDesktopServices.openUrl(url_arquivo)
                else:
                    # Se não passou 'export_info', é apenas o Botão "OK" de visualização no LayoutDesigner do QGIS
                    if layout_persistente:
                        layout_persistente.refresh()
                        manager.addLayout(layout_persistente)
                        self.iface.openLayoutDesigner(layout_persistente)
            else:
                self.iface.messageBar().pushMessage(self.tr("Cancelado"), self.tr("O processamento foi interrompido."), level=Qgis.MessageLevel.Warning)

        except Exception as e:
            erro_detalhado = traceback.format_exc()
            if getattr(self, 'sentry_ativo', False):
                try: sentry_sdk.capture_exception(e); sentry_sdk.flush(timeout=2.0)
                except Exception: pass
            self.iface.messageBar().pushMessage(self.tr("Erro"), f"{str(e)}. {self.tr('Veja o console para detalhes.')}", level=Qgis.MessageLevel.Critical)
            QgsMessageLog.logMessage(erro_detalhado, "VectorToMap", Qgis.MessageLevel.Critical)

        finally:
            self.is_rendering = False
            self.set_ui_enabled(True)
            try:
                self.dlg.progressBar.hide()
            except Exception: pass
            gc.collect()

    def cancelar_e_fechar(self, *args, **kwargs):
        """Roteia o botão cancelar dependendo se o Motor (Engine) está rodando pesado ou não."""
        try:
            self.limpar_clones_preview()
            if self.is_rendering:
                self.engine.abort_processing = True # Bandeira vermelha, a Engine vai parar no próximo passo de loop
                self.iface.messageBar().pushMessage(self.tr("Aviso"), self.tr("Cancelando..."), level=Qgis.MessageLevel.Success, duration=3)
            else:
                self.dlg.reject()
        except RuntimeError: pass

    def _verificar_sobrescrita_arquivos(self, base_sem_ext, ext, paginas_dados, is_individual):
        """Impede que centenas de arquivos JPG/PNG sobreponham uns aos outros por colisão de nomes."""
        arquivos_existentes = False
        config = self._gerar_config_atual()
        campo_atlas = config.get('campo_atlas')

        if is_individual:
            for i, dados in enumerate(paginas_dados):
                nome_teste = self.engine._gerar_nome_arquivo_pagina(dados, i, campo_atlas)
                if os.path.exists(f"{base_sem_ext}_{nome_teste}{ext}"):
                    arquivos_existentes = True
                    break
        else:
            if os.path.exists(f"{base_sem_ext}{ext}"): arquivos_existentes = True

        if arquivos_existentes:
            resposta = QMessageBox.question(self.dlg, self.tr("Confirmar"), self.tr("Arquivos existentes. Sobrescrever?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            return resposta == QMessageBox.StandardButton.Yes
        return True

    def set_ui_enabled(self, enabled):
        """Muda o cursor para Ampulheta de forma global e desativa botões de clique."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return

            self.btn_export.setEnabled(enabled)
            self.btn_render.setEnabled(enabled)
            self.btn_ok.setEnabled(enabled)

            if not enabled:
                self.btn_cancel.setText(self.tr("Parar Processo"))
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            else:
                self.btn_cancel.setText(self.tr("Cancelar"))
                QApplication.restoreOverrideCursor()

            self.dlg.mMapLayerComboBox.setEnabled(enabled)
        except RuntimeError: pass

    def escolher_fonte_titulo(self, *args, **kwargs):
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            fonte, ok = QFontDialog.getFont(getattr(self, 'fonte_titulo', QFont()), self.dlg, self.tr("Fonte"))
            if ok: self.fonte_titulo = fonte; self.disparar_preview_se_autorizado()
        except RuntimeError: pass

    def atualizar_combo_temas(self, *args, **kwargs):
        """Puxa os "Map Themes" (Temas) salvos na janela principal do QGIS direto pro Plugin."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            if not hasattr(self.dlg, 'combo_temas') or sip.isdeleted(self.dlg.combo_temas): return
            self.dlg.combo_temas.blockSignals(True)
            self.dlg.combo_temas.clear()
            temas = QgsProject.instance().mapThemeCollection().mapThemes()
            if not temas:
                if hasattr(self.dlg, 'chk_usar_tema') and not sip.isdeleted(self.dlg.chk_usar_tema):
                    self.dlg.chk_usar_tema.setChecked(False)
                    self.dlg.chk_usar_tema.setEnabled(False)
                self.dlg.combo_temas.setEnabled(False)
            else:
                if hasattr(self.dlg, 'chk_usar_tema') and not sip.isdeleted(self.dlg.chk_usar_tema):
                    self.dlg.chk_usar_tema.setEnabled(True)
                    self.dlg.combo_temas.setEnabled(self.dlg.chk_usar_tema.isChecked())
                self.dlg.combo_temas.addItems(temas)
            self.dlg.combo_temas.blockSignals(False)
        except RuntimeError: pass

    def _filtrar_camadas_da_combo(self, *args, **kwargs):
        """Oculta as camadas invisíveis (Memory Layers de Filtro) das ComboBoxes de escolha."""
        try:
            if not hasattr(self, 'dlg') or not self.dlg or sip.isdeleted(self.dlg): return
            if hasattr(self.dlg, 'mMapLayerComboBox') and not sip.isdeleted(self.dlg.mMapLayerComboBox):
                excluidas = []
                for layer in QgsProject.instance().mapLayers().values():
                    if layer.customProperty("vtm_is_preview_temp"): excluidas.append(layer)
                self.dlg.mMapLayerComboBox.setExceptedLayerList(excluidas)
                if hasattr(self.dlg, 'combo_camada_loc') and not sip.isdeleted(self.dlg.combo_camada_loc):
                    self.dlg.combo_camada_loc.setExceptedLayerList(excluidas)
        except RuntimeError: pass


    # ====================================================================================
    # --- 7. LINKS, AJUDA E WIDGETS FLUTUANTES ---
    # ====================================================================================

    def abrir_link_externo(self, tipo):
        urls = {"gumroad": "https://buymeacoffee.com/matheusdurso", "github": "https://github.com/matheusdurso/VectorToMap/issues", "tutorial": "https://www.youtube.com/watch?v=AIITugHD-_o"}
        QDesktopServices.openUrl(QUrl(urls.get(tipo, "")))

    def ir_para_suporte(self, *args, **kwargs):
        try:
            if hasattr(self.dlg, 'tabWidget'): self.dlg.tabWidget.setCurrentIndex(1)
        except RuntimeError: pass

    def mostrar_tela_sobre(self, *args, **kwargs):
        """Tela Nativa de Ajuda do Algoritmo (usando QgsMessageLog)."""
        try:
            msg_box = QMessageBox(self.dlg)
            msg_box.setWindowTitle(self.tr("Ajuda do Algoritmo"))
            msg_box.setIcon(QMessageBox.Icon.NoIcon)

            texto_corrido = self.tr(
                "VectorToMap<br><br>"
                "O VectorToMap automatiza a geração de layouts de impressão para cartografia técnica. "
                "Este algoritmo transforma os dados da camada vetorial em pranchas prontas, "
                "com enquadramento e escala calculados dinamicamente.<br><br>"
                "O parâmetro de agrupamento funciona de forma semelhante a um Atlas, permitindo gerar um mapa individual para cada feição "
                "ou agrupar várias feições que compartilham o mesmo valor em uma coluna específica da tabela.<br><br>"
                "O parâmetro de escala controla o nível de zoom do mapa. Pode ser definido para centralização "
                "automática ou fixado em valores absolutos. O uso de expressões (ε) permite que a margem de respiro ou "
                "a escala exata sejam lidas e aplicadas diretamente a partir dos atributos da feição atual.<br><br>"
                "A opção de filtrar geometrias controla a visibilidade dos elementos no layout final. "
                "Quando ativada, ela isola e exibe apenas as feições que pertencem à página que está sendo gerada, "
                "ocultando automaticamente o restante dos dados do mapa.<br><br>"
                "<ul><li><i>Utilize o botão de Preview para validar o enquadramento, os estilos e a renderização das "
                "informações na tela antes de executar a exportação em lote para arquivos finais.</i></li></ul>"
            )
            msg_box.setText(texto_corrido)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            if hasattr(msg_box, 'exec'): msg_box.exec()
            else: msg_box.exec_()
        except RuntimeError: pass

    def _adicionar_aba_sobre(self):
        """Injeta a aba de créditos e licenciamento INPI com formatação rica."""
        try:
            if not hasattr(self.dlg, 'tab_2'): return

            aba_sobre = self.dlg.tab_2
            # O "Dummy Widget": Transfere o layout de dono para não dar crash na remontagem
            if aba_sobre.layout() is not None: QWidget().setLayout(aba_sobre.layout())

            layout = QVBoxLayout(aba_sobre)
            layout.setContentsMargins(20, 20, 20, 20)

            t_title = self.tr("VectorToMap")
            t_sub = self.tr("Motor de Renderização Cartográfica Automatizada")

            lbl_header = QLabel(f"<span style='font-size:16pt; font-weight:bold; color:#2c3e50;'>{t_title}</span><br><span style='font-size:11pt; color:#7f8c8d;'>{t_sub}</span>")
            layout.addWidget(lbl_header)
            layout.addSpacing(10)

            layout_botoes = QHBoxLayout()
            layout_botoes.setSpacing(10)

            self.btn_apoiar = QPushButton(self.tr("☕ Apoiar Desenvolvimento"), aba_sobre)
            self.btn_bugreport = QPushButton(self.tr("🐞 Relatar Bug (GitHub)"), aba_sobre)
            self.btn_tutorial = QPushButton(self.tr("▶ Assistir Tutorial"), aba_sobre)

            self.btn_apoiar.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_bugreport.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_tutorial.setCursor(Qt.CursorShape.PointingHandCursor)

            self.btn_apoiar.setObjectName("pushButton_apoiar")
            self.btn_bugreport.setObjectName("pushButton_bugreport")
            self.btn_tutorial.setObjectName("pushButton_tutorial")

            self.btn_apoiar.clicked.connect(lambda: self.abrir_link_externo('gumroad'))
            self.btn_bugreport.clicked.connect(lambda: self.abrir_link_externo('github'))
            self.btn_tutorial.clicked.connect(lambda: self.abrir_link_externo('tutorial'))

            layout_botoes.addWidget(self.btn_apoiar)
            layout_botoes.addWidget(self.btn_bugreport)
            layout_botoes.addWidget(self.btn_tutorial)
            layout_botoes.addStretch()

            layout.addLayout(layout_botoes)
            layout.addSpacing(10)

            linha = QFrame()
            linha.setFrameShape(QFrame.Shape.HLine)
            linha.setStyleSheet("border: 1px solid #eaeaea; background-color: transparent;")
            layout.addWidget(linha)
            layout.addSpacing(5)

            txt_browser = QTextBrowser(aba_sobre)
            txt_browser.setOpenExternalLinks(True)
            txt_browser.setStyleSheet("border: none; background-color: transparent;")

            t_h1 = self.tr("Visão Geral do Sistema")
            t_p1_pt1 = self.tr("O VectorToMap é uma solução avançada de automação em software livre para Sistemas de Informação Geográfica (SIG), criada para otimizar a sua cartografia técnica. Projetado para lidar com rotinas de alta demanda cartográfica, o complemento atua diretamente sobre a API de layouts nativa do QGIS (QgsPrintLayout), permitindo a renderização em lote de feições espaciais com parâmetros de enquadramento escaláveis.")
            t_p1_pt2 = self.tr("Todo esse projeto se mantém vivo e em constante evolução graças ao apoio da comunidade. Ao apoiar o nosso desenvolvimento contínuo, você garante que a ferramenta continue recebendo melhorias e se mantenha sempre funcional.")
            t_h2 = self.tr("Aplicações Técnicas")
            t_li1 = self.tr("<b>Engenharia e Licenciamento:</b> Geração massiva de plantas de situação, croquis de acesso e anexos cartográficos padronizados para estudos ambientais.")
            t_li2 = self.tr("<b>Gestão Fundiária:</b> Automatização de pranchas para o Cadastro Ambiental Rural (CAR), regularização fundiária e cadastros técnicos multifinalitários urbanos.")
            t_li3 = self.tr("<b>Inspeção e Laudos:</b> Padronização visual e geração rápida de encartes de mapas para relatórios de vistoria em campo.")
            t_h3 = self.tr("Arquitetura e Funcionalidades Core")
            t_li4 = self.tr("<b>Integração QGIS Expressions:</b> Suporte nativo a Data-Defined Overrides (DDO). O motor lê funções SQL inseridas pelo usuário para calcular dinamicamente margens e escalas com base no contexto geométrico.")
            t_li5 = self.tr("<b>Isolamento em Memória:</b> Utiliza rotinas de instanciamento de camadas transitórias (Memory Layers) e filtros de visibilidade sem afetar a Layer Tree principal do projeto.")
            t_li6 = self.tr("<b>Engine de Exportação:</b> Suporte multi-thread e multi-formato dinâmico perfeitamente ajustado para lotes de impressão.")
            t_dev = self.tr("Desenvolvido por:")
            t_inpi = self.tr("Registro INPI:")
            t_contato = self.tr("Contato:")
            t_linkedin = self.tr("LinkedIn:")
            t_licenca = self.tr("Licença:")

            html_content = f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li {{ white-space: pre-wrap; }}</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:11pt; font-weight:400; font-style:normal; color: #333333;">
<p style=" margin-top:0px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; color:#2c3e50;">{t_h1}</span></p>
<p style=" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-align: justify;">{t_p1_pt1}</p>
<p style=" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-align: justify;">{t_p1_pt2}</p>
<p style=" margin-top:0px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; color:#2c3e50;">{t_h2}</span></p>
<ul style="margin-top: 0px; margin-bottom: 15px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
<li style=" margin-top:0px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{t_li1}</li>
<li style=" margin-top:0px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{t_li2}</li>
<li style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{t_li3}</li></ul>
<p style=" margin-top:0px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600; color:#2c3e50;">{t_h3}</span></p>
<ul style="margin-top: 0px; margin-bottom: 15px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
<li style=" margin-top:0px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{t_li4}</li>
<li style=" margin-top:0px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{t_li5}</li>
<li style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{t_li6}</li></ul>
<hr style="border: 1px solid #eaeaea; margin-top:10px; margin-bottom:10px;" />
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt; color:#555555;">
<span style=" font-weight:600;">{t_dev}</span> Matheus Durso Neves Caetano<br />
<span style=" font-weight:600;">{t_inpi}</span> BR 51 2026 001755-6<br />
<span style=" font-weight:600;">{t_contato}</span> <a href="mailto:matheusdursonc@gmail.com"><span style=" text-decoration: underline; color:#3498db;">matheusdursonc@gmail.com</span></a><br />
<span style=" font-weight:600;">{t_linkedin}</span> <a href="https://www.linkedin.com/in/matheus-durso-neves-caetano"><span style=" text-decoration: underline; color:#3498db;">Conectar no LinkedIn</span></a><br />
<span style=" font-weight:600;">{t_licenca}</span> GNU GPLv2
</span></p></body></html>"""

            txt_browser.setHtml(html_content)
            layout.addWidget(txt_browser)

            if hasattr(self.dlg, 'tabWidget'):
                idx = self.dlg.tabWidget.indexOf(aba_sobre)
                if idx != -1: self.dlg.tabWidget.setTabText(idx, self.tr("Sobre o Plugin"))
        except RuntimeError: pass

    def mostrar_info(self, topico, widget_ancora):
        """As caixas flutuantes modernas de sombra para as dicas dos botões 'i'."""
        try:
            texto_ajuda = ""

            # Usamos HTML básico para deixar o texto bonito dentro da caixa (Texto 100% Original)
            if topico == "ddo_auto":
                t_titulo = self.tr("Escala Automática Dinâmica")
                t_desc = self.tr("Use o botão 'ε' para definir a margem de zoom dinamicamente com base na sua tabela de atributos.")
                t_ex_lbl = self.tr("Exemplo:")
                t_ex_txt = self.tr("Uma coluna com o número '15' aplicará 15% de margem no enquadramento.")
                t_sql_lbl = self.tr("Expressão SQL:")
                t_sql_txt = "if(\"Tipo\" = 'Urbano', 10, 25)"
                t_obs = self.tr("Se o cálculo falhar ou a célula estiver vazia, o plugin usará a margem padrão (25%).")

                texto_ajuda = (
                    f"<b style='color: #2980b9; font-size: 14px;'>{t_titulo}</b><br><br>"
                    f"{t_desc}<br><br>"
                    f"<b>{t_ex_lbl}</b> {t_ex_txt}<br>"
                    f"<b>{t_sql_lbl}</b> <i>{t_sql_txt}</i><br><br>"
                    f"<span style='color: #555;'>{t_obs}</span>"
                )

            elif topico == "ddo_fixa":
                t_titulo = self.tr("Escala Fixa Dinâmica")
                t_desc = self.tr("Use o botão 'ε' para definir a escala absoluta dinamicamente com base na sua tabela de atributos.")
                t_ex_lbl = self.tr("Exemplo:")
                t_ex_txt = self.tr("Uma coluna com o número '5000' forçará o mapa para a escala 1:5000.")
                t_sql_lbl = self.tr("Expressão SQL:")
                t_sql_txt = "\"Minha_Coluna\" * 1000"
                t_obs = self.tr("Se o cálculo falhar ou a célula for nula, o plugin usará a escala padrão.")

                texto_ajuda = (
                    f"<b style='color: #2980b9; font-size: 14px;'>{t_titulo}</b><br><br>"
                    f"{t_desc}<br><br>"
                    f"<b>{t_ex_lbl}</b> {t_ex_txt}<br>"
                    f"<b>{t_sql_lbl}</b> <i>{t_sql_txt}</i><br><br>"
                    f"<span style='color: #555;'>{t_obs}</span>"
                )

            elif topico == "presets":
                t_titulo = self.tr("Formatos e Templates")
                t_desc = self.tr("Define a estrutura visual da prancha de impressão.")
                t_mod_lbl = self.tr("Modelos Básicos (Matemáticos):")
                t_mod_txt = self.tr("O plugin constrói o layout do zero, dividindo a folha geometricamente entre o mapa, tabela de atributos e decorações nativas.")
                t_tpl_lbl = self.tr("📄 Templates:")
                t_tpl_txt = self.tr("Modelos profissionais e otimizados que acompanham a versão. Eles mantêm o design, as margens e as decorações originais, ajustando apenas o mapa dinamicamente.")
                t_cus_lbl = self.tr("📂 Template Personalizado (.qpt):")
                t_cus_txt = self.tr("Permite importar um layout desenhado por você no QGIS com a identidade visual da sua empresa (logos, selos e carimbos). O motor preserva o seu design e injeta o mapa atualizado direto no seu quadro principal.")

                texto_ajuda = (
                    f"<b style='color: #2980b9; font-size: 14px;'>{t_titulo}</b><br><br>"
                    f"{t_desc}<br><br>"
                    f"<b>{t_mod_lbl}</b><br>{t_mod_txt}<br><br>"
                    f"<b>{t_tpl_lbl}</b><br>{t_tpl_txt}<br><br>"
                    f"<b>{t_cus_lbl}</b><br>{t_cus_txt}"
                )

            elif topico == "agrupar":
                t_titulo = self.tr("Agrupamento Avançado (Atlas)")
                t_desc = self.tr("Agrupe feições no mesmo mapa usando uma coluna da tabela ou uma expressão matemática (ε).")
                t_ex_lbl = self.tr("Exemplo Simples:")
                t_ex_txt = self.tr("Escolher a coluna 'Bairro' gerará um mapa para cada bairro, unindo todos os lotes que pertencem a ele na mesma prancha.")
                t_sql_lbl = self.tr("Expressão SQL:")
                t_sql_txt = "concat(\"Municipio\", ' - ', \"Gleba\")"
                t_obs = self.tr("O motor calculará a fórmula para todas as geometrias. Feições com o mesmo resultado exato serão desenhadas juntas.")

                texto_ajuda = (
                    f"<b style='color: #2980b9; font-size: 14px;'>{t_titulo}</b><br><br>"
                    f"{t_desc}<br><br>"
                    f"<b>{t_ex_lbl}</b> {t_ex_txt}<br>"
                    f"<b>{t_sql_lbl}</b> <i>{t_sql_txt}</i><br><br>"
                    f"<span style='color: #555;'>{t_obs}</span>"
                )

            if not texto_ajuda: return

            self.info_popup = QWidget(self.dlg)
            self.info_popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
            self.info_popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            layout_principal = QVBoxLayout(self.info_popup)
            layout_principal.setContentsMargins(10, 10, 10, 10)

            container_externo = QFrame()
            container_externo.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #dcdcdc; border-radius: 6px; }")

            layout_container_externo = QVBoxLayout(container_externo)
            layout_container_externo.setContentsMargins(2, 2, 2, 2)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            scroll_area.setStyleSheet("background-color: transparent;")

            conteudo_interno = QWidget()
            layout_interno = QVBoxLayout(conteudo_interno)
            layout_interno.setContentsMargins(15, 15, 15, 15)

            lbl = QLabel(texto_ajuda)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("QLabel { color: #333333; font-size: 12px; border: none; }")
            lbl.setFixedWidth(280)

            layout_interno.addWidget(lbl)
            layout_interno.addStretch()

            scroll_area.setWidget(conteudo_interno)
            layout_container_externo.addWidget(scroll_area)
            layout_principal.addWidget(container_externo)

            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setColor(QColor(0, 0, 0, 40))
            sombra.setOffset(2, 4)
            container_externo.setGraphicsEffect(sombra)

            ponto_ancora = widget_ancora.mapToGlobal(widget_ancora.rect().bottomLeft())
            altura_janela = self.dlg.height()
            y_relativo_botao = self.dlg.mapFromGlobal(ponto_ancora).y()
            espaco_disponivel = altura_janela - y_relativo_botao - 30
            altura_maxima = min(350, max(150, espaco_disponivel))

            self.info_popup.setFixedWidth(330)
            self.info_popup.setFixedHeight(int(altura_maxima))
            self.info_popup.move(ponto_ancora.x(), ponto_ancora.y() + 2)
            self.info_popup.show()
        except RuntimeError: pass