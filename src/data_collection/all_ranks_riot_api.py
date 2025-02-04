import requests
import sqlite3
from pathlib import Path
from config import API_KEY

# Configuração 
queue = 'RANKED_SOLO_5x5'
server = 'br1'

# Diretório para armazenar o banco de dados
db_path = Path(__file__).resolve().parent.parent.parent / 'data' / 'lol_ranked.db'

# Headers para a requisição
headers = {"X-Riot-Token": API_KEY}

# Lista de ranks e divisões
high_tiers = ["challengerleagues", "grandmasterleagues", "masterleagues"]
lower_tiers = ["DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
divisions = ["I", "II", "III", "IV"]  

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
    veteran BOOLEAN,
    inactive BOOLEAN,
    fresh_blood BOOLEAN,
    hot_streak BOOLEAN
)
""")

conn.commit()

# Função para inserir dados no banco de dados
def insert_player(summoner_id, summoner_name, rank, division, lp, wins, losses, veteran, inactive, fresh_blood, hot_streak):
    cursor.execute("""
    INSERT OR IGNORE INTO players 
    (summoner_id, summoner_name, rank, division, lp, wins, losses, veteran, inactive, fresh_blood, hot_streak) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (summoner_id, summoner_name, rank, division, lp, wins, losses, veteran, inactive, fresh_blood, hot_streak))
    conn.commit()

# Função para coletar dados de cada rank
def fetch_rank_data(rank, division=None):
    if division:
        url = f"https://{server}.api.riotgames.com/lol/league/v4/entries/{queue}/{rank}/{division}?page=1"
    else:
        url = f"https://{server}.api.riotgames.com/lol/league/v4/{rank}/by-queue/{queue}"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar {rank} {division if division else ''}: {response.status_code}")
        return None

# Coletando Challenger, Grandmaster e Master
for tier in high_tiers:
    data = fetch_rank_data(tier)
    if data:
        for player in data.get("entries", []):
            insert_player(
                player["summonerId"], 
                player.get("summonerName", "Desconhecido"),
                tier.replace("leagues", "").upper(),
                None,  # Sem divisão nesses ranks
                player["leaguePoints"],
                player["wins"],
                player["losses"],
                player["veteran"],
                player["inactive"],
                player["freshBlood"],
                player["hotStreak"]
            )

# Coletando Diamond até Iron
for tier in lower_tiers:
    for division in divisions:
        data = fetch_rank_data(tier, division)
        if data:
            for player in data:
                insert_player(
                    player["summonerId"], 
                    player.get("summonerName", "Desconhecido"),
                    tier,
                    division,
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
