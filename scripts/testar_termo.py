from curl_cffi import requests

def search(termo):
    payload = {
        "query": {
            "termo": [termo] if termo else [],
            "atividade_principal": [],
            "natureza_juridica": [],
            "uf": [],
            "municipio": [],
            "bairro": [],
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
    r = s.post("https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", json=payload, timeout=30)
    d = r.json()
    print("termo=", repr(termo), "total=", d.get("total"))
    for c in d.get("cnpjs", [])[:5]:
        print(" ", c.get("cnpj"), c.get("razao_social", "")[:60])

search("condominio")
search("")
search("ITAU")
