import json
from dataclasses import fields
from pathlib import Path
from typing import Optional

from models import FiltroPesquisa

BASE_DIR = Path(__file__).resolve().parent.parent
CAMINHO_PADRAO = BASE_DIR / "config" / "filtros.json"


def carregar_filtros(caminho: Optional[Path] = None) -> FiltroPesquisa:
    """Le os filtros a partir do JSON e retorna um FiltroPesquisa."""
    caminho = Path(caminho) if caminho else CAMINHO_PADRAO
    dados = {}
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

    campos_validos = {f.name for f in fields(FiltroPesquisa)}
    filtrados = {k: v for k, v in dados.items() if k in campos_validos}
    return FiltroPesquisa(**filtrados)
