import requests
import sqlite3
from pathlib import Path
from config import API_KEY

# Diretório e caminho do banco de dados
data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
data_dir.mkdir(parents=True, exist_ok=True)  
db_path = data_dir / 'challenger.db'  

# Configuração
queue = 'RANKED_SOLO_5x5'
server = 'br1'

# URL da API da Riot Games
url = f'https://{server}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}'
headers = {"X-Riot-Token": API_KEY}

# Criar conexão com o banco de dados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criar tabela caso não exista
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summoner_id TEXT UNIQUE,
    summoner_name TEXT,
    rank TEXT,
    division TEXT,
    lp INTEGER,
    wins INTEGER,
    losses INTEGER,
    veteran INTEGER,
    inactive INTEGER,
    fresh_blood INTEGER,
    hot_streak INTEGER
)
""")
conn.commit()

# Função para inserir dados no banco de dados
def insert_player(summoner_id, summoner_name, rank, division, lp, wins, losses, veteran, inactive, fresh_blood, hot_streak):
    cursor.execute("""
    INSERT OR IGNORE INTO players 
    (summoner_id, summoner_name, rank, division, lp, wins, losses, veteran, inactive, fresh_blood, hot_streak) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (summoner_id, summoner_name, rank, division, lp, wins, losses, int(veteran), int(inactive), int(fresh_blood), int(hot_streak)))
    conn.commit()

# Fazendo a requisição
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  
    data = response.json()
    
    if data:
        rank_tier = data.get("tier", "UNKNOWN") 
        
        for player in data.get("entries", []):
            insert_player(
                player["summonerId"], 
                player.get("summonerName", "Desconhecido"),
                rank_tier,  # Pegamos o tier corretamente
                None,  # Sem divisão nesses ranks
                player["leaguePoints"],
                player["wins"],
                player["losses"],
                player["veteran"],
                player["inactive"],
                player["freshBlood"],
                player["hotStreak"]
            )

    # Fechando conexão com o banco
    conn.close()
    print(f"Banco de dados atualizado e salvo em {db_path}")

except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar a API: {e}")
