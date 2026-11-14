import os
import requests

# 1. Credenciais seguras
usuario = "hackathon_nasa_space_apps_almeidamundundi_garcia"
senha = os.environ["METEOMATICS_SENHA"]

# 2. Local (Huambo - Planalto Central) e período (últimos 12 meses)
lat, lon = -12.7761, 15.7392
periodo = "2025-11-01T00:00:00Z--2026-11-01T00:00:00Z:P1M"

# 3. Indicadores: Temperatura máx, Chuva e Umidade do solo
parametros = "t_max_2m_24h:C,precip_24h:mm,soil_moisture_index_-5cm:idx"

url = f"https://api.meteomatics.com/{periodo}/{parametros}/{lat},{lon}/csv"

resposta = requests.get(url, auth=(usuario, senha))

if resposta.status_code == 200:
    with open("cache_huambo.csv", "w", encoding="utf-8") as arquivo:
        arquivo.write(resposta.text)
    print("Sucesso! Arquivo 'cache_huambo.csv' criado.")
else:
    print(f"Erro {resposta.status_code}: {resposta.text}")
