import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class Settings:
    """Configuracoes lidas do arquivo .env."""

    fonte: str = "gratuita"
    api_key: str = ""
    portal_email: str = ""
    portal_senha: str = ""
    pesquisa_id: str = ""
    limite_pagina_plataforma: int = 1000
    cf_clearance: str = ""
    user_agent: str = ""
    delay_entre_requisicoes: float = 4.0
    impersonate: str = "chrome120"
    delimitador: str = ","
    max_paginas: int = 100
    max_resultados: int = 0
    max_erros_consecutivos: int = 5


def _to_float(valor, padrao: float) -> float:
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return padrao


def carregar_settings() -> Settings:
    """Carrega as configuracoes a partir do .env (se existir)."""
    load_dotenv(BASE_DIR / ".env")

    return Settings(
        fonte=os.getenv("FONTE", "gratuita").strip().lower(),
        api_key=os.getenv("API_KEY", "").strip(),
        cf_clearance=os.getenv("CF_CLEARANCE", "").strip(),
        user_agent=os.getenv("USER_AGENT", "").strip(),
        delay_entre_requisicoes=_to_float(os.getenv("DELAY_ENTRE_REQUISICOES"), 4.0),
        impersonate=os.getenv("IMPERSONATE", "chrome120").strip() or "chrome120",
        delimitador=os.getenv("DELIMITADOR", ",").strip() or ",",
        max_paginas=int(os.getenv("MAX_PAGINAS", "100") or 100),
        max_resultados=int(os.getenv("MAX_RESULTADOS", "0") or 0),
        max_erros_consecutivos=int(os.getenv("MAX_ERROS_CONSECUTIVOS", "5") or 5),
        portal_email=os.getenv("PORTAL_EMAIL", "").strip(),
        portal_senha=os.getenv("PORTAL_SENHA", "").strip(),
        pesquisa_id=os.getenv("PESQUISA_ID", "").strip(),
        limite_pagina_plataforma=int(os.getenv("LIMITE_PAGINA_PLATAFORMA", "1000") or 1000),
    )
