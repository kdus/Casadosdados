import json
from curl_cffi import requests

cnpj = "96512355000139"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://casadosdados.com.br",
    "Referer": f"https://casadosdados.com.br/solucao/cnpj/condominio-edificio-matisse-{cnpj}",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

s = requests.Session(impersonate="chrome120")
s.get("https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada", timeout=60)

for url in [
    f"https://api.casadosdados.com.br/v4/public/cnpj/{cnpj}",
    f"https://api.casadosdados.com.br/v4/public/cnpj/{cnpj}/",
]:
    r = s.get(url, headers=headers, timeout=30)
    print(url, r.status_code, r.text[:300])
