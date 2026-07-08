import json
from curl_cffi import requests

OLD = {
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

urls = [
    "https://api.casadosdados.com.br/v1/rf/public/cnpj/query/search",
    "https://api.casadosdados.com.br/v2/public/cnpj/search/local",
    "https://api.casadosdados.com.br/v2/public/cnpj/search/local/",
    "https://api.casadosdados.com.br/v4/public/cnpj/search/local",
]

for url in urls:
    r = s.post(url, json=OLD, timeout=30)
    print("POST", url, r.status_code, r.text[:250])
    print()
