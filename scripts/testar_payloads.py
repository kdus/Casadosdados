import json
from curl_cffi import requests

OLD_PAYLOAD = {
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

V5_PAYLOAD = {
    "cnpj": [],
    "busca_textual": ["condominio"],
    "codigo_atividade_principal": [],
    "incluir_atividade_secundaria": False,
    "codigo_atividade_secundaria": [],
    "codigo_natureza_juridica": [],
    "situacao_cadastral": ["ATIVA"],
    "uf": ["SP"],
    "municipio": ["SAO PAULO"],
    "bairro": ["VILA CARRAO"],
    "cep": [],
    "ddd": [],
    "limite": 20,
    "pagina": 1,
}

s = requests.Session(impersonate="chrome")
s.headers.update(
    {
        "Content-Type": "application/json",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
    }
)

tests = [
    ("POST v5/public/cnpj/pesquisa OLD", "https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", OLD_PAYLOAD),
    ("POST v5/public/cnpj/pesquisa V5", "https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", V5_PAYLOAD),
    ("POST v1/rf/public/cnpj/query/search OLD", "https://api.casadosdados.com.br/v1/rf/public/cnpj/query/search", OLD_PAYLOAD),
]

for label, url, payload in tests:
    r = s.post(url, json=payload, timeout=30)
    print(label, "->", r.status_code)
    try:
        d = r.json()
        total = d.get("total")
        cnpjs = d.get("cnpjs") or d.get("data") or []
        print("  total:", total, "items:", len(cnpjs) if isinstance(cnpjs, list) else type(cnpjs))
        if isinstance(cnpjs, list) and cnpjs:
            first = cnpjs[0]
            if isinstance(first, dict):
                print("  first:", first.get("cnpj"), first.get("razao_social", "")[:50])
    except Exception as exc:
        print("  err:", exc, r.text[:200])
    print()

cnpj = "96512355000139"
for url in [
    f"https://api.casadosdados.com.br/v4/public/cnpj/{cnpj}",
    f"https://api.casadosdados.com.br/v4/public/cnpj/{cnpj}/",
]:
    r = s.get(url, timeout=30)
    print("GET", url, "->", r.status_code, r.text[:300])
