import json
from curl_cffi import requests

payloads = [
    {
        "name": "OLD",
        "body": {
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
        },
    },
    {
        "name": "OLD ibge municipio",
        "body": {
            "query": {
                "termo": ["condominio"],
                "atividade_principal": [],
                "natureza_juridica": [],
                "uf": ["SP"],
                "municipio": ["3550308"],
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
        },
    },
    {
        "name": "V5 official-like",
        "body": {
            "cnpj": [],
            "busca_textual": ["condominio"],
            "codigo_atividade_principal": [],
            "incluir_atividade_secundaria": False,
            "codigo_atividade_secundaria": [],
            "codigo_natureza_juridica": [],
            "situacao_cadastral": ["ATIVA"],
            "uf": ["SP"],
            "municipio": ["3550308"],
            "bairro": ["VILA CARRAO"],
            "cep": [],
            "ddd": [],
            "mais_filtros": {
                "somente_mei": False,
                "excluir_mei": False,
                "com_email": False,
                "com_telefone": False,
                "somente_fixo": False,
                "somente_celular": False,
                "somente_matriz": False,
                "somente_filial": False,
            },
            "limite": 20,
            "pagina": 1,
        },
    },
]

s = requests.Session(impersonate="chrome")
s.headers.update(
    {
        "Content-Type": "application/json",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
    }
)

for item in payloads:
    r = s.post("https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", json=item["body"], timeout=30)
    print(item["name"], r.status_code)
    if r.status_code == 200:
        d = r.json()
        cnpjs = d.get("cnpjs", [])
        print(" total", d.get("total"), "returned", len(cnpjs))
        for c in cnpjs[:3]:
            print(" ", c.get("cnpj"), c.get("razao_social", "")[:40])
    else:
        print(" ", r.text[:200])
    print()
