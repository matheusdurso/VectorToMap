# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QCoreApplication

class TextosTemplates:
    """
    ARQUIVO FANTASMA: Este arquivo não é importado em lugar nenhum.
    Ele serve apenas para o pylupdate5 ler as strings dos arquivos .qpt
    e jogá-las no arquivo .ts para tradução no Qt Linguist.
    
    A classe e a função tr() abaixo garantem que o contexto no Qt Linguist
    fique registrado como 'VectorToMap' ou 'TextosTemplates', mas que o 
    QGIS consiga parear a tradução.
    """
    def __init__(self):
        # =================================================================
        # TEXTOS DOS TEMPLATES (EXATAMENTE COMO ESTÃO NOS ARQUIVOS .QPT)
        # =================================================================
        
        # Textos do Modelo A4 Paisagem
        self.tr("CROQUI DE VISTORIA / FISCALIZAÇÃO")
        self.tr("DADOS DE CAMPO")
        self.tr("Alvo:")
        self.tr("Coordenada Central:")
        self.tr("Data da Vistoria:")
        self.tr("Constatações / Descrição Ambiental:")
        self.tr("Croqui Vistoria A4 Coordenadas Geograficas")
        self.tr("Assinatura do Agente / Fiscal:")
        self.tr("Assinatura do Autuado / Vistoriado:")

        # Textos do Modelo Planta de Situação
        self.tr("Planta Situacao A4 Coordenadas Geograficas")
        self.tr("PLANTA DE SITUAÇÃO E LOCALIZAÇÃO")
        self.tr("LEGENDA")
        self.tr("SELO TÉCNICO")
        self.tr("Projeto:")
        self.tr("Requerente:")
        self.tr("Resp. Técnico:")
        self.tr("CREA/CAU:")
        self.tr("Área (ha):")
        self.tr("Data:")

        # Textos do Modelo Uso e Ocupação do Solo
        self.tr("Uso Ocupacao Solo A3 Coordenadas Geograficas")
        self.tr("MAPA DE USO E OCUPAÇÃO DO SOLO - DIAGNÓSTICO")
        self.tr("QUADRO DE ÁREAS (ha)")
        self.tr("LEGENDA DE CLASSES")
        self.tr("VectorToMap - Relatório Gerado Automaticamente")
        
        # =================================================================
        # OS NOMES DOS ARQUIVOS NA COMBOBOX (O PULO DO GATO)
        # O nome do arquivo passado pelo .title() no vector_to_map.py
        # =================================================================
        self.tr("Croqui Vistoria A4 Coordenadas Geograficas")
        self.tr("Planta Situacao A4 Coordenadas Geograficas")
        self.tr("Uso Ocupacao Solo A3 Coordenadas Geograficas")

    def tr(self, message):
        """
        O truque Mestre: Força o contexto de tradução para a classe principal.
        Isso garante que, quando o vector_to_map.py chamar a tradução, 
        o QGIS encontre a string no mesmo "bolso".
        """
        return QCoreApplication.translate('VectorToMap', message)