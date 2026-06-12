import os
import sys
import pytest
from qgis.core import QgsApplication, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY

# Adiciona a raiz do plugin ao sys.path para o Python achar o vector_to_map
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session", autouse=True)
def qgis_app():
    """
    Inicializa a aplicação QGIS 3 em modo Headless (sem tela).
    Roda apenas uma vez para toda a bateria de testes.
    """
    # No Docker oficial do QGIS, os binários ficam em /usr
    QgsApplication.setPrefixPath("/usr", True)
    
    # O 'False' aqui é o que garante o modo Headless (sem GUI)
    app = QgsApplication([], False)
    app.initQgis()
    
    yield app  # Pausa aqui e roda os testes
    
    # Desliga o QGIS e limpa a memória após os testes
    app.exitQgis()

@pytest.fixture
def mock_layer():
    """
    Cria uma camada vetorial de memória (Point) com 2 feições simuladas.
    Ideal para testar o DDO (Data-Defined Overrides) e agrupamentos.
    """
    layer = QgsVectorLayer("Point?crs=epsg:4326&field=id:integer&field=tipo:string", "Lotes", "memory")
    provider = layer.dataProvider()
    
    f1 = QgsFeature(layer.fields())
    f1.setAttributes([1, "Urbano"])
    f1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-41.9, -18.8))) # Simulando uma coordenada
    
    f2 = QgsFeature(layer.fields())
    f2.setAttributes([2, "Rural"])
    f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-41.95, -18.85)))
    
    provider.addFeatures([f1, f2])
    layer.updateExtents()
    return layer

@pytest.fixture
def mock_iface():
    """Cria um objeto falso para simular o iface do QGIS que seu plugin pede."""
    class MockIface:
        pass
    return MockIface()