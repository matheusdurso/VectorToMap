import os
import zipfile
import configparser

def criar_pacote():
    # 1. Ler metadados para pegar nome e versão
    config = configparser.ConfigParser()
    config.read('metadata.txt', encoding='utf-8')
    nome_plugin = "vector_to_map"  # Nome da pasta oficial
    versao = config.get('general', 'version')
    zip_name = f"{nome_plugin}_v{versao}.zip"

    print(f"--- Iniciando Build do {nome_plugin} v{versao} ---")

    # 2. Listas de Exclusão unificadas
    pastas_ignorar = ['__pycache__', '.git', '.vscode', 'build_output', '.github']
    
    # Lista de arquivos exatos ou extensões para ignorar
    itens_ignorar = [
        '.gitignore', 'pb_tool.cfg', 'resources.qrc', 'build.py', 
        '.ts', '.pyc', '.zip', '.vscode'
    ]

    if os.path.exists(zip_name):
        os.remove(zip_name)
        print(f"Regerando arquivo: {zip_name}")

    # 3. Criar o ZIP com a estrutura correta para o QGIS
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Filtra pastas indesejadas
            dirs[:] = [d for d in dirs if d not in pastas_ignorar]
            
            for file in files:
                # Lógica de filtro corrigida: ignora se o nome está na lista ou se termina com a extensão
                deve_ignorar = any(file == item or file.endswith(item) for item in itens_ignorar)
                
                if deve_ignorar:
                    continue
                
                caminho_completo = os.path.join(root, file)
                # Define o caminho dentro do ZIP (dentro da pasta vector_to_map/)
                caminho_no_zip = os.path.join(nome_plugin, os.path.relpath(caminho_completo, '.'))
                
                zipf.write(caminho_completo, caminho_no_zip)
                print(f"Adicionado: {caminho_no_zip}")

    print(f"\n✅ Sucesso! Plugin empacotado em: {zip_name}")

if __name__ == "__main__":
    criar_pacote()