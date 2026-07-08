from curl_cffi import requests

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
r = s.post("https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", json=V5_PAYLOAD, timeout=30)
print("status", r.status_code)
print("body", r.text[:1000])
