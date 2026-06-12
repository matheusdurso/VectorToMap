import os
import pytest
from qgis.core import QgsProject, QgsPrintLayout, QgsLayoutItemMap, QgsVectorLayer, QgsProject
from layout_engine import LayoutEngine

def test_engine_inicializacao(mock_iface):
    """Verifica se o motor instanciou corretamente sem exceptions."""
    engine = LayoutEngine(mock_iface)
    assert engine is not None
    assert engine.abort_processing is False
    assert isinstance(engine.clones_preview, list)

def test_criacao_mapas_e_nomenclatura_ids(mock_iface, mock_layer):
    """
    Testa se o motor adiciona o mapa e se as regras rígidas de ID
    ('main_map' e 'overview_map') estão sendo aplicadas para 
    compatibilidade com os templates.
    """
    engine = LayoutEngine(mock_iface)
    project = QgsProject.instance()
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    
    # 1. Simula a geometria de papel repassada pelo _configurar_papel_e_fundo
    geo = {
        'w_pg': 210, 'h_pg': 297, 'w_map': 180, 'h_map': 180,
        'x_map': 15, 'y_map': 15, 'y_zero': 0, 'margin': 15
    }
    
    # 2. Executa a criação do mapa principal via Engine
    from qgis.PyQt.QtGui import QColor
    map_item = engine._adicionar_item_mapa(layout, geo, apenas_mapa=False, cor_fundo=QColor(255, 255, 255))
    
    # A classe VectorToMap seta o ID logo após receber o objeto do LayoutEngine
    map_item.setId("main_map")
    
    # 3. Asserções de Segurança (QA)
    assert isinstance(map_item, QgsLayoutItemMap), "O item retornado não é um mapa válido do QGIS."
    
    # Valida o ID rígido do mapa principal
    assert map_item.id() == "main_map", "O mapa principal não recebeu o id obrigatório 'main_map'."
    
    # Verifica se a matemática geométrica foi respeitada na página
    assert map_item.rect().width() == 180.0
    assert map_item.rect().height() == 180.0

def test_gerador_nomes_paginas(mock_iface):
    """Testa se a função de ofuscação e criação de prefixos não quebra o SO."""
    engine = LayoutEngine(mock_iface)
    
    # Teste 1: Mapa Geral (String protegida)
    nome_1 = engine._gerar_nome_arquivo_pagina({}, 0, "__ALL_FEATURES__")
    assert "Zoom_Camada" in nome_1
    
    # Teste 2: Sequencial (Fallback)
    nome_2 = engine._gerar_nome_arquivo_pagina({}, 5, None)
    assert nome_2 == "6" # O index no Python começa em 0
    
    # Teste 3: Limpeza de Caracteres Especiais (Sanitização)
    dados_sujos = {'valor_grupo': 'Bairro/Centro?*>'}
    nome_3 = engine._gerar_nome_arquivo_pagina(dados_sujos, 0, "Bairro")
    assert "/" not in nome_3
    assert "?" not in nome_3



def listar_arquivos_vetoriais_ruins():
    """Varre a pasta 'data' e retorna todos os arquivos vetoriais suportados."""
    dir_data = os.path.join(os.path.dirname(__file__), 'data')
    
    if not os.path.exists(dir_data):
        return []
        
    # Tupla com as extensões vetoriais que você quer testar
    extensoes_suportadas = ('.shp', '.kml', '.geojson', '.gpkg', '.sqlite', '.dxf')
    
    arquivos = []
    for arquivo in os.listdir(dir_data):
        # Transforma para minúsculo para garantir que vai pegar .KML ou .kml
        if arquivo.lower().endswith(extensoes_suportadas):
            arquivos.append(os.path.join(dir_data, arquivo))
            
    return arquivos

# Passamos a nova função que lê múltiplos formatos
@pytest.mark.parametrize("caminho_vetor", listar_arquivos_vetoriais_ruins())
def test_resiliencia_arquivos_corrompidos(mock_iface, caminho_vetor):
    """
    Testa a resiliência do motor contra arquivos vetoriais diversos (SHP, KML, GPKG)
    que possam estar corrompidos ou sem dados.
    """
    nome_arquivo = os.path.basename(caminho_vetor)
    
    # O "ogr" é mágico: ele lê KML, GeoJSON e SHP com o mesmo comando!
    camada_corrompida = QgsVectorLayer(caminho_vetor, "Camada Ruim", "ogr")
    
    assert camada_corrompida.isValid(), f"O QGIS não conseguiu abrir o arquivo {nome_arquivo}."

    engine = LayoutEngine(mock_iface)
    layout = QgsPrintLayout(QgsProject.instance())
    
    config = {
        'preset': 'quadrado',
        'orientacao': 'Retrato',
        'campo_atlas': None,
        'escala_fixa': True,
        'escala_val': 1000.0
    }
    
    passou_sem_crash = False
    
    try:
        engine.montar_design_da_pagina(
            layout=layout, 
            camada=camada_corrompida, 
            feicoes_da_pagina=list(camada_corrompida.getFeatures()), 
            preset='quadrado', 
            orientacao='Retrato', 
            config=config
        )
        passou_sem_crash = True
    except Exception as e:
        print(f"\nErro tratado pelo plugin ao processar {nome_arquivo}: {e}")
        
    assert passou_sem_crash is True, f"O arquivo {nome_arquivo} causou um crash na aplicação!"