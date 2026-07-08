"""Orquestracao do robo: pesquisa, detalhe e gravacao."""

import time
from pathlib import Path
from typing import List, Set

from loguru import logger

from config import Settings
from models import EmpresaCnpj, FiltroPesquisa
from services import CasaDadosClient
from views import CsvTxtWriter


class RoboController:
    def __init__(self, cliente: CasaDadosClient, settings: Settings, writer: CsvTxtWriter):
        self.cliente = cliente
        self.settings = settings
        self.writer = writer

    def executar(
        self,
        filtro: FiltroPesquisa,
        arquivo_saida: Path = None,
        cnpjs_diretos: List[str] = None,
        continuar: bool = False,
    ) -> Path:
        caminho_saida = Path(arquivo_saida) if arquivo_saida else self.writer.caminho_padrao()
        cnpjs_ja_gravados: Set[str] = set()
        gravacao_incremental = self.settings.fonte == "plataforma"

        if continuar and caminho_saida.exists():
            cnpjs_ja_gravados = self.writer.ler_cnpjs_existentes(caminho_saida)
            if cnpjs_ja_gravados:
                logger.info(
                    "Continuando extracao: {} CNPJ(s) ja gravados em {}.",
                    len(cnpjs_ja_gravados),
                    caminho_saida,
                )

        if gravacao_incremental:
            self.writer.iniciar_arquivo(caminho_saida, sobrescrever=not continuar)
        if cnpjs_diretos:
            cnpjs = ["".join(ch for ch in c if ch.isdigit()) for c in cnpjs_diretos]
            cnpjs = [c for c in cnpjs if len(c) == 14]
            logger.info("Modo direto: {} CNPJ(s) informado(s)", len(cnpjs))
        else:
            if self.settings.fonte == "plataforma":
                logger.info(
                    "Modo plataforma: pesquisa salva {} (extracao completa paginada).",
                    self.settings.pesquisa_id or "(nao definida)",
                )
            else:
                logger.info("Iniciando pesquisa com filtros: {}", filtro.descricao_curta())
            cnpjs = self.cliente.pesquisar_todos(filtro)
            logger.info("Total de CNPJs encontrados na pesquisa: {}", len(cnpjs))

        if not cnpjs:
            logger.warning("Nenhum CNPJ encontrado. Verifique os filtros ou o acesso ao site.")
            if not gravacao_incremental:
                return self.writer.gravar([], filtro, caminho_saida)
            return caminho_saida

        if cnpjs_ja_gravados:
            cnpjs = [c for c in cnpjs if c not in cnpjs_ja_gravados]
            logger.info("CNPJs restantes para processar: {}", len(cnpjs))

        empresas: List[EmpresaCnpj] = []
        cache = getattr(self.cliente, "_cache_detalhes", {})
        erros_consecutivos = 0
        for indice, cnpj in enumerate(cnpjs, start=1):
            cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())
            ja_em_cache = cnpj_limpo in cache

            logger.info("[{}/{}] Obtendo detalhe do CNPJ {}...", indice, len(cnpjs), cnpj)
            try:
                empresa = self.cliente.obter_detalhe(cnpj)
                if (
                    self.settings.fonte != "plataforma"
                    and not filtro.atende_empresa(empresa)
                ):
                    logger.info(
                        "  -> Ignorado (nao atende filtros): {} | abertura: {}",
                        empresa.razao_social or cnpj,
                        empresa.data_abertura or "N/A",
                    )
                    continue
                empresas.append(empresa)
                if gravacao_incremental:
                    self.writer.anexar(empresa, caminho_saida)
                logger.info("  -> {}", empresa.razao_social or cnpj)
                erros_consecutivos = 0
            except Exception as exc:
                erros_consecutivos += 1
                logger.error("  -> Erro ao obter detalhe de {}: {}", cnpj, exc)
                if erros_consecutivos >= self.settings.max_erros_consecutivos:
                    logger.error(
                        "Interrompendo apos {} erros consecutivos. "
                        "Use --continuar para retomar depois.",
                        erros_consecutivos,
                    )
                    break

            if indice < len(cnpjs) and not ja_em_cache:
                time.sleep(self.settings.delay_entre_requisicoes)

        if gravacao_incremental:
            total = len(cnpjs_ja_gravados) + len(empresas)
            logger.success("Arquivo atualizado: {} ({} registros no total)", caminho_saida, total)
            return caminho_saida

        caminho = self.writer.gravar(empresas, filtro, caminho_saida)
        logger.success("Arquivo gerado: {} ({} registros)", caminho, len(empresas))
        return caminho
