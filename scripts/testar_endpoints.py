import json
from curl_cffi import requests

payload = {
    "query": {
        "termo": ["condominio"],
        "atividade_principal": [],
        "natureza_juridica": [],
        "uf": ["SP"],
        "municipio": ["SAO PAULO"],
        "bairro": ["VILA CARRAO"],
        "situacao_cadastral": "ATIVA",
        "cep": [],
        "ddd": [],
    },
    "range_query": {
        "data_abertura": {"lte": None, "gte": None},
        "capital_social": {"lte": None, "gte": None},
    },
    "extras": {
        "somente_mei": False,
        "excluir_mei": False,
        "com_email": False,
        "incluir_atividade_secundaria": False,
        "com_contato_telefonico": False,
        "somente_fixo": False,
        "somente_celular": False,
        "somente_matriz": False,
        "somente_filial": False,
    },
    "page": 1,
}

s = requests.Session(impersonate="chrome")
s.headers.update(
    {
        "Content-Type": "application/json",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
    }
)

search_urls = [
    "https://api.casadosdados.com.br/v1/rf/public/cnpj/query/",
    "https://api.casadosdados.com.br/v5/public/cnpj/pesquisa",
    "https://api.casadosdados.com.br/v5/public/cnpj/pesquisa/",
    "https://api.casadosdados.com.br/v4/public/cnpj/pesquisa",
    "https://api.casadosdados.com.br/v4/public/cnpj/pesquisa/",
]

for url in search_urls:
    r = s.post(url, json=payload, timeout=30)
    print("POST", url, "->", r.status_code)
    print(r.text[:400])
    print("---")

cnpj = "96512355000139"
detail_urls = [
    f"https://api.casadosdados.com.br/v2/public/cnpj/{cnpj}",
    f"https://api.casadosdados.com.br/v4/public/cnpj/{cnpj}",
    f"https://api.casadosdados.com.br/v1/rf/public/cnpj/{cnpj}",
]

for url in detail_urls:
    r = s.get(url, timeout=30)
    print("GET", url, "->", r.status_code)
    print(r.text[:400])
    print("---")
