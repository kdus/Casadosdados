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
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
    }
)

# Visita a pagina antes para obter cookies de sessao
s.get("https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada", timeout=60)
r = s.post("https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", json=payload, timeout=60)
print("status", r.status_code)
d = r.json()
print("total", d.get("total"))
for c in d.get("cnpjs", [])[:5]:
    print(c.get("cnpj"), c.get("razao_social"))
