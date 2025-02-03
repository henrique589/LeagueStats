import requests
import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent.parent / 'data' 
json_filename = 'challenger_data.json' 
file_path = data_dir / json_filename

# Configuração
api_key = 'XXXXXXXX'
queue = 'RANKED_SOLO_5x5'
server = 'br1' 

# URL correta da API da Riot Games
url = f'https://{server}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}'
headers = {"X-Riot-Token": api_key}

# Fazendo a requisição
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  
    data = response.json()

    # Criando a pasta 'data/' caso não exista
    data_dir.mkdir(parents=True, exist_ok=True)

    # Salvando os dados em um arquivo JSON
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Dados salvos com sucesso em {file_path}")

except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar a API: {e}")
