import json
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
s.get("https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada", timeout=60)
s.headers.update(
    {
        "Content-Type": "application/json",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
    }
)

payloads = [
    {
        "busca_textual": ["condominio"],
        "situacao_cadastral": ["ATIVA"],
        "uf": ["SP"],
        "municipio": ["SAO PAULO"],
        "bairro": ["VILA CARRAO"],
        "limite": 20,
        "pagina": 1,
    },
    {
        "busca_textual": ["condominio"],
        "situacao_cadastral": ["ATIVA"],
        "uf": ["SP"],
        "municipio": ["3550308"],
        "bairro": ["VILA CARRAO"],
        "limite": 20,
        "pagina": 1,
    },
    {
        "busca_textual": ["condominio"],
        "situacao_cadastral": ["ATIVA"],
        "uf": ["SP"],
        "municipio": ["SAO PAULO"],
        "bairro": ["VILA CARRAO"],
        "limite": 20,
        "pagina": 1,
        "mais_filtros": {},
    },
]

for i, payload in enumerate(payloads, 1):
    r = s.post("https://api.casadosdados.com.br/v5/public/cnpj/pesquisa", json=payload, timeout=30)
    print("payload", i, "status", r.status_code, "len", len(r.text))
    if r.status_code == 200:
        d = r.json()
        print(" total", d.get("total"))
        for c in d.get("cnpjs", [])[:3]:
            print(" ", c.get("cnpj"), c.get("razao_social", "")[:50])
    else:
        print(" body", repr(r.text[:300]))
    print()
