"""Grava os dados em arquivo .txt separado por virgula (compativel com Excel)."""

import csv
from pathlib import Path
from typing import List, Optional, Set

from loguru import logger

from config import BASE_DIR
from models import EmpresaCnpj, FiltroPesquisa


class CsvTxtWriter:
    ARQUIVO_PADRAO = "pesquisa.txt"

    def __init__(self, delimitador: str = ","):
        self.delimitador = delimitador
        self.pasta_saida = BASE_DIR / "saida"
        self.pasta_saida.mkdir(exist_ok=True)

    def caminho_padrao(self) -> Path:
        return self.pasta_saida / self.ARQUIVO_PADRAO

    def ler_cnpjs_existentes(self, caminho: Path) -> Set[str]:
        caminho = Path(caminho)
        if not caminho.exists() or caminho.stat().st_size == 0:
            return set()
        cnpjs: Set[str] = set()
        with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
            reader = csv.reader(arquivo, delimiter=self.delimitador)
            next(reader, None)
            for linha in reader:
                if not linha:
                    continue
                cnpj = "".join(ch for ch in linha[0] if ch.isdigit())
                if len(cnpj) == 14:
                    cnpjs.add(cnpj)
        return cnpjs

    def iniciar_arquivo(self, caminho: Path, sobrescrever: bool = False) -> None:
        caminho = Path(caminho)
        if caminho.exists() and not sobrescrever:
            return
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
            writer = csv.writer(arquivo, delimiter=self.delimitador, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(EmpresaCnpj.nomes_campos())

    def anexar(self, empresa: EmpresaCnpj, caminho: Path) -> None:
        caminho = Path(caminho)
        with open(caminho, "a", encoding="utf-8-sig", newline="") as arquivo:
            writer = csv.writer(arquivo, delimiter=self.delimitador, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(empresa.to_linha())

    def gravar(
        self,
        empresas: List[EmpresaCnpj],
        filtro: FiltroPesquisa,
        caminho: Optional[Path] = None,
    ) -> Path:
        caminho = Path(caminho) if caminho else self.caminho_padrao()

        with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
            writer = csv.writer(arquivo, delimiter=self.delimitador, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(EmpresaCnpj.nomes_campos())
            for empresa in empresas:
                writer.writerow(empresa.to_linha())

        logger.info("Arquivo salvo em: {}", caminho)
        return caminho
