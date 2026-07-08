"""Testa formatos de filtro data_abertura na API publica."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import carregar_settings
from curl_cffi import requests as cf

settings = carregar_settings()
s = cf.Session(impersonate="chrome120")
if settings.cf_clearance:
    s.cookies.set("cf_clearance", settings.cf_clearance, domain=".casadosdados.com.br")
s.headers.update(
    {
        "User-Agent": settings.user_agent or "Mozilla/5.0",
        "Origin": "https://casadosdados.com.br",
        "Referer": "https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
)
url = "https://api.casadosdados.com.br/v5/public/cnpj/pesquisa"

base_flat = {
    "termo": ["condominio"],
    "uf": ["SP"],
    "municipio": ["SAO PAULO"],
    "bairro": ["VILA CARRAO"],
    "situacao_cadastral": ["ATIVA"],
    "page": 1,
    "limite": 20,
}

tests = [
    ("flat sem data", base_flat),
    (
        "flat + range_query",
        {
            **base_flat,
            "range_query": {"data_abertura": {"gte": "2022-01-01", "lte": None}},
        },
    ),
    (
        "v5 official-like + range",
        {
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
            "range_query": {"data_abertura": {"gte": "2022-01-01", "lte": None}},
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
    ),
    (
        "v5 data_abertura top",
        {
            **base_flat,
            "data_abertura": {"gte": "2022-01-01", "lte": None},
        },
    ),
    (
        "v5 data_abertura_inicio",
        {
            **base_flat,
            "data_abertura_inicio": "2022-01-01",
        },
    ),
    (
        "flat + query nested + range",
        {
            "termo": ["condominio"],
            "uf": ["SP"],
            "municipio": ["SAO PAULO"],
            "bairro": ["VILA CARRAO"],
            "situacao_cadastral": ["ATIVA"],
            "query": {
                "termo": ["condominio"],
                "uf": ["SP"],
                "municipio": ["SAO PAULO"],
                "bairro": ["VILA CARRAO"],
                "situacao_cadastral": "ATIVA",
            },
            "range_query": {
                "data_abertura": {"gte": "2022-01-01", "lte": None},
                "capital_social": {"gte": None, "lte": None},
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
            "limite": 20,
        },
    ),
]

for name, body in tests:
    r = s.post(url, json=body, timeout=30)
    d = r.json() if r.status_code == 200 else {}
    cnpjs = d.get("cnpjs", [])
    first = cnpjs[0].get("cnpj") if cnpjs else None
    print(f"{name}: status={r.status_code} total={d.get('total')} first={first}")
