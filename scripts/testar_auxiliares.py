import json
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
s.headers.update(
    {
        "Content-Type": "application/json",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
    }
)

tests = [
    ("GET municipio SP", "GET", "https://api.casadosdados.com.br/v4/public/cnpj/busca/municipio/SP", None),
    ("GET municipio query", "GET", "https://api.casadosdados.com.br/v4/public/cnpj/busca/municipio/SP?q=SAO%20PAULO", None),
    ("POST aggs municipio", "POST", "https://api.casadosdados.com.br/v2/public/cnpj/search/aggs/municipio", {"uf": ["SP"]}),
]

for label, method, url, body in tests:
    if method == "GET":
        r = s.get(url, timeout=30)
    else:
        r = s.post(url, json=body, timeout=30)
    print(label, r.status_code, r.text[:300])
    print()
