import requests
import pandas as pd

def carregar_dados_com_fallback(lat, lon):
    try:
        # Tenta a chamada em tempo real à API da NASA/Meteomatics (exemplo conceitual)
        url = f"https://api.meteomatics.com/.../t_max:C,precip:mm/json?lat={lat}&lon={lon}"
        # resposta = requests.get(url, timeout=5)
        # if resposta.status_code == 200:
        #     return processar_api(resposta.json()), "API ao Vivo"
        
        # Simulando uma falha de rede propositada para testar o fallback:
        raise ConnectionError("Rede instável ou API indisponível")

    except Exception as e:
        # Se falhar por falta de internet ou erro na API, recorre ao cache local guardado!
        df_cache = pd.read_csv("cache_huambo.csv", sep=";")
        return df_cache, "Cache Local (Modo Resiliente)"
