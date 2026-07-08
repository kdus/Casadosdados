"""Ponto de entrada do robo CNPJ - Casa dos Dados."""

import argparse
import re
import sys
from pathlib import Path

from loguru import logger

from config import carregar_filtros, carregar_settings
from controllers import RoboController
from models import FiltroPesquisa
from services import criar_cliente
from views import CsvTxtWriter


def _extrair_pesquisa_id(valor: str) -> str:
    """Extrai UUID de pesquisaId=... ou retorna o proprio valor."""
    if not valor:
        return ""
    match = re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        valor,
        flags=re.I,
    )
    return match.group(0) if match else valor.strip()


def _configurar_log() -> None:
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/robo_cnpj.log", rotation="1 MB", retention=5, encoding="utf-8")


def _aplicar_cli(filtro: FiltroPesquisa, args: argparse.Namespace) -> FiltroPesquisa:
    """Sobrescreve filtros do JSON com parametros da linha de comando."""
    if args.termo:
        filtro.termo = [t.strip() for t in args.termo.split(",") if t.strip()]
    if args.uf:
        filtro.uf = [u.strip().upper() for u in args.uf.split(",") if u.strip()]
    if args.municipio:
        filtro.municipio = [m.strip().upper() for m in args.municipio.split(",") if m.strip()]
    if args.bairro:
        filtro.bairro = [b.strip().upper() for b in args.bairro.split(",") if b.strip()]
    if args.situacao:
        filtro.situacao_cadastral = args.situacao.strip().upper()
    if args.data_abertura_de:
        filtro.data_abertura_gte = args.data_abertura_de.strip()
    if args.data_abertura_ate:
        filtro.data_abertura_lte = args.data_abertura_ate.strip()
    return filtro


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robo de coleta de CNPJs - Casa dos Dados")
    parser.add_argument("--termo", help="Termo de busca (razao social/nome fantasia). Ex: condominio")
    parser.add_argument("--uf", help="UF separadas por virgula. Ex: SP")
    parser.add_argument("--municipio", help="Municipio separados por virgula. Ex: SAO PAULO")
    parser.add_argument("--bairro", help="Bairro separados por virgula. Ex: VILA CARRAO")
    parser.add_argument("--situacao", help="Situacao cadastral. Ex: ATIVA")
    parser.add_argument(
        "--data-abertura-de",
        help="Data de abertura minima (a partir de). Ex: 2022-01-01 ou 01/01/2022",
    )
    parser.add_argument(
        "--data-abertura-ate",
        help="Data de abertura maxima (ate). Ex: 2024-12-31",
    )
    parser.add_argument("--filtros", help="Caminho para arquivo JSON de filtros (padrao: config/filtros.json)")
    parser.add_argument(
        "--saida",
        default="saida/pesquisa.txt",
        help="Caminho do arquivo .txt de saida (padrao: saida/pesquisa.txt)",
    )
    parser.add_argument("--fonte", choices=["gratuita", "plataforma", "oficial"], help="Sobrescreve FONTE do .env")
    parser.add_argument(
        "--pesquisa-id",
        help="UUID ou URL da pesquisa salva na plataforma (ex.: pesquisaId=5407171b-...)",
    )
    parser.add_argument("--max-paginas", type=int, help="Numero maximo de paginas da pesquisa")
    parser.add_argument("--max-resultados", type=int, help="Para apos encontrar N CNPJs (0=ilimitado)")
    parser.add_argument(
        "--cnpjs",
        help="Lista de CNPJs separados por virgula (pula a pesquisa, busca apenas detalhes)",
    )
    parser.add_argument(
        "--cnpjs-arquivo",
        help="Arquivo .txt com um CNPJ por linha (pula a pesquisa, busca apenas detalhes)",
    )
    parser.add_argument(
        "--continuar",
        action="store_true",
        help="Retoma extracao ignorando CNPJs ja gravados no arquivo de saida",
    )
    return parser.parse_args()


def main() -> int:
    _configurar_log()
    args = _parse_args()

    settings = carregar_settings()
    if args.fonte:
        settings.fonte = args.fonte
    if args.pesquisa_id:
        settings.pesquisa_id = _extrair_pesquisa_id(args.pesquisa_id)
        if settings.fonte == "gratuita":
            settings.fonte = "plataforma"
    if args.max_paginas:
        settings.max_paginas = args.max_paginas
    if args.max_resultados is not None:
        settings.max_resultados = args.max_resultados

    caminho_filtros = Path(args.filtros) if args.filtros else None
    filtro = carregar_filtros(caminho_filtros)
    filtro = _aplicar_cli(filtro, args)

    cliente = criar_cliente(settings)
    writer = CsvTxtWriter(delimitador=settings.delimitador)
    controller = RoboController(cliente, settings, writer)

    cnpjs_diretos = None
    if args.cnpjs_arquivo:
        texto = Path(args.cnpjs_arquivo).read_text(encoding="utf-8")
        cnpjs_diretos = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    elif args.cnpjs:
        cnpjs_diretos = [c.strip() for c in args.cnpjs.split(",") if c.strip()]

    caminho_saida = Path(args.saida)
    controller.executar(
        filtro,
        caminho_saida,
        cnpjs_diretos=cnpjs_diretos,
        continuar=args.continuar,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
