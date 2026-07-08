"""Cliente HTTP para a API da Casa dos Dados (fonte gratuita e oficial)."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from curl_cffi import requests as cf_requests
from loguru import logger

from config import Settings
from models import EmpresaCnpj, FiltroPesquisa
from services.mapeador import extrair_cnpjs_da_pesquisa, mapear_json_para_empresa
from services.nuxt_parser import montar_url_detalhe, mapear_html_para_empresa

BASE_URL = "https://api.casadosdados.com.br"
SITE_URL = "https://casadosdados.com.br"
URL_SEARCH_PUBLIC = f"{BASE_URL}/v5/public/cnpj/pesquisa"
URL_SEARCH_OFICIAL = f"{BASE_URL}/v5/cnpj/pesquisa"
URL_LOGIN = f"{BASE_URL}/v4/usuario/login"
URL_PESQUISA_SALVA = f"{BASE_URL}/v4/cnpj/pesquisas-salvas"
PORTAL_URL = "https://portal.casadosdados.com.br"
LIMITE_PESQUISA_GRATUITA = 20
URL_DETALHE_OFICIAL = f"{BASE_URL}/v4/cnpj/{{cnpj}}"

USER_AGENT_PADRAO = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class CasaDadosClient(ABC):
    @abstractmethod
    def pesquisar_todos(self, filtro: FiltroPesquisa) -> List[str]:
        pass

    @abstractmethod
    def obter_detalhe(self, cnpj: str) -> EmpresaCnpj:
        pass


class _ClienteHttpBase:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._cache_detalhes: Dict[str, EmpresaCnpj] = {}
        self._cnpj_razao: Dict[str, str] = {}
        self.session = cf_requests.Session(impersonate=settings.impersonate)
        self._configurar_sessao()
        self._aquecer_sessao()

    def _configurar_sessao(self) -> None:
        user_agent = self.settings.user_agent or USER_AGENT_PADRAO
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Origin": SITE_URL,
                "Referer": f"{SITE_URL}/solucao/cnpj/pesquisa-avancada",
            }
        )
        if self.settings.cf_clearance:
            self.session.cookies.set(
                "cf_clearance", self.settings.cf_clearance, domain=".casadosdados.com.br"
            )

    def _aquecer_sessao(self) -> None:
        try:
            self.session.get(f"{SITE_URL}/solucao/cnpj/pesquisa-avancada", timeout=60)
        except Exception as exc:
            logger.warning("Nao foi possivel aquecer sessao: {}", exc)

    def _request_json(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        resposta = self.session.request(method, url, timeout=60, **kwargs)
        if resposta.status_code == 403 and "Just a moment" in resposta.text:
            raise RuntimeError(
                "Bloqueio Cloudflare (403). Defina CF_CLEARANCE e USER_AGENT no .env."
            )
        resposta.raise_for_status()
        try:
            return resposta.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Resposta nao e JSON valido de {url}") from exc

    def _request_html(self, url: str, tentativas: int = 3) -> str:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": f"{SITE_URL}/solucao/cnpj/pesquisa-avancada",
        }
        ultimo_erro = None
        for tentativa in range(1, tentativas + 1):
            resposta = self.session.get(url, headers=headers, timeout=60)
            bloqueado = (
                resposta.status_code in (403, 429)
                or "Just a moment" in resposta.text
            )
            if bloqueado:
                ultimo_erro = (
                    "Bloqueio Cloudflare ao acessar pagina de detalhe. "
                    "Defina CF_CLEARANCE e USER_AGENT no .env ou aumente DELAY_ENTRE_REQUISICOES."
                )
                pausa = self.settings.delay_entre_requisicoes * tentativa * 3
                logger.debug("Cloudflare detectado, aguardando {:.1f}s antes de retry...", pausa)
                time.sleep(pausa)
                if tentativa == 2:
                    self._aquecer_sessao()
                continue
            resposta.raise_for_status()
            if "__NUXT_DATA__" not in resposta.text:
                ultimo_erro = "Pagina de detalhe sem dados (__NUXT_DATA__ ausente)."
                time.sleep(self.settings.delay_entre_requisicoes * tentativa)
                continue
            return resposta.text

        raise RuntimeError(ultimo_erro or "Falha ao obter pagina de detalhe.")

    def _cnpj_atende_filtro(self, empresa: EmpresaCnpj, filtro: FiltroPesquisa) -> bool:
        if filtro.situacao_cadastral:
            if empresa.situacao_cadastral.upper() != filtro.situacao_cadastral.upper():
                return False
        if filtro.uf:
            ufs = {u.upper() for u in filtro.uf}
            if empresa.uf.upper() not in ufs:
                return False
        if filtro.municipio:
            municipios = {m.upper() for m in filtro.municipio}
            if empresa.municipio.upper() not in municipios:
                return False
        if filtro.bairro:
            bairros = {b.upper() for b in filtro.bairro}
            if empresa.bairro.upper() not in bairros:
                return False
        if filtro.termo:
            termos = [t.upper() for t in filtro.termo]
            texto = f"{empresa.razao_social} {empresa.nome_fantasia}".upper()
            if not any(termo in texto for termo in termos):
                return False
        return True

    def _obter_detalhe_html(self, cnpj: str, razao_social: str = "") -> EmpresaCnpj:
        cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())
        if cnpj_limpo in self._cache_detalhes:
            return self._cache_detalhes[cnpj_limpo]

        razao = razao_social or self._cnpj_razao.get(cnpj_limpo, "")
        url = montar_url_detalhe(cnpj_limpo, razao)
        html = self._request_html(url)
        empresa = mapear_html_para_empresa(html)
        self._cache_detalhes[cnpj_limpo] = empresa
        return empresa

    def _atingiu_limite(self, total: int) -> bool:
        limite = self.settings.max_resultados
        return limite > 0 and total >= limite


class FonteGratuita(CasaDadosClient, _ClienteHttpBase):
    """Fonte gratuita: pesquisa avancada publica (20 resultados) + detalhe via HTML."""

    def __init__(self, settings: Settings):
        _ClienteHttpBase.__init__(self, settings)

    def _extrair_cnpjs_pesquisa_publica(self, dados: Dict[str, Any]) -> List[str]:
        cnpjs: List[str] = []
        for item in dados.get("cnpjs") or []:
            if not isinstance(item, dict):
                continue
            cnpj = "".join(ch for ch in str(item.get("cnpj", "")) if ch.isdigit())
            if len(cnpj) != 14:
                continue
            razao = item.get("razao_social", "")
            if razao:
                self._cnpj_razao[cnpj] = razao
            cnpjs.append(cnpj)
        return list(dict.fromkeys(cnpjs))

    def pesquisar_todos(self, filtro: FiltroPesquisa) -> List[str]:
        payload = filtro.to_payload_publico(page=1, limite=LIMITE_PESQUISA_GRATUITA)

        logger.info(
            "Pesquisa avancada gratuita (pagina 1, ate {} resultados)...",
            LIMITE_PESQUISA_GRATUITA,
        )
        logger.info("Filtros aplicados: {}", filtro.resumo_filtros())
        logger.debug("Payload da pesquisa: {}", payload)

        dados = self._request_json("POST", URL_SEARCH_PUBLIC, json=payload)
        total = dados.get("total", 0)
        cnpjs = self._extrair_cnpjs_pesquisa_publica(dados)

        logger.info(
            "Pesquisa retornou {} CNPJ(s) de {} encontrados (limite gratuito: {})",
            len(cnpjs),
            total,
            LIMITE_PESQUISA_GRATUITA,
        )

        for cnpj in cnpjs:
            razao = self._cnpj_razao.get(cnpj, cnpj)
            logger.info("  -> {} - {}", cnpj, razao)

        if self.settings.max_resultados > 0:
            return cnpjs[: self.settings.max_resultados]
        return cnpjs

    def obter_detalhe(self, cnpj: str) -> EmpresaCnpj:
        return self._obter_detalhe_html(cnpj)


class FontePlataforma(CasaDadosClient):
    """Plataforma logada: pesquisa salva paginada + detalhe via API (/v4/cnpj)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._cache_detalhes: Dict[str, EmpresaCnpj] = {}
        self._cnpj_razao: Dict[str, str] = {}
        self.session = cf_requests.Session(impersonate=settings.impersonate)
        self._configurar_sessao()
        self._api_key = settings.api_key or self._login()
        self.session.headers["api-key"] = self._api_key

    def _configurar_sessao(self) -> None:
        user_agent = self.settings.user_agent or USER_AGENT_PADRAO
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/json",
                "Origin": PORTAL_URL,
                "Referer": f"{PORTAL_URL}/plataforma/pesquisa",
            }
        )

    def _login(self) -> str:
        if not self.settings.portal_email or not self.settings.portal_senha:
            raise ValueError(
                "PORTAL_EMAIL e PORTAL_SENHA sao obrigatorios quando FONTE=plataforma. "
                "Configure no .env."
            )
        logger.info("Autenticando na plataforma ({})...", self.settings.portal_email)
        dados = self._request_json(
            "POST",
            URL_LOGIN,
            json={
                "email": self.settings.portal_email,
                "password": self.settings.portal_senha,
            },
        )
        api_key = dados.get("apiKey") or dados.get("api_key")
        if not api_key:
            raise RuntimeError("Login na plataforma nao retornou apiKey.")
        logger.info("Login realizado com sucesso.")
        return api_key

    def _carregar_pesquisa_salva(self) -> Dict[str, Any]:
        pesquisa_id = self.settings.pesquisa_id
        if not pesquisa_id:
            raise ValueError(
                "PESQUISA_ID e obrigatorio quando FONTE=plataforma. "
                "Use o UUID do link salvo (ex.: pesquisaId=...)."
            )
        url = f"{URL_PESQUISA_SALVA}/{pesquisa_id}"
        logger.info("Carregando pesquisa salva {}...", pesquisa_id)
        dados = self._request_json("GET", url)
        nome = dados.get("nome", pesquisa_id)
        pesquisa = dados.get("pesquisa")
        if not isinstance(pesquisa, dict):
            raise RuntimeError(f"Pesquisa salva invalida: {pesquisa_id}")
        logger.info("Pesquisa salva carregada: {}", nome)
        return pesquisa

    def _extrair_cnpjs_resposta(self, dados: Dict[str, Any]) -> List[str]:
        cnpjs: List[str] = []
        for item in dados.get("cnpjs") or []:
            if not isinstance(item, dict):
                continue
            cnpj = "".join(ch for ch in str(item.get("cnpj", "")) if ch.isdigit())
            if len(cnpj) != 14:
                continue
            razao = item.get("razao_social", "")
            if razao:
                self._cnpj_razao[cnpj] = razao
            cnpjs.append(cnpj)
        return cnpjs

    def pesquisar_todos(self, filtro: FiltroPesquisa) -> List[str]:
        pesquisa_base = self._carregar_pesquisa_salva()
        limite_pagina = self.settings.limite_pagina_plataforma or 1000
        pagina = 1
        todos_cnpjs: List[str] = []
        total_esperado = 0

        while pagina <= self.settings.max_paginas:
            payload = dict(pesquisa_base)
            payload["pagina"] = pagina
            payload["limite"] = limite_pagina

            logger.info("Pesquisando pagina {} (limite {} por pagina)...", pagina, limite_pagina)
            dados = self._request_json("POST", URL_SEARCH_OFICIAL, json=payload)
            total_esperado = dados.get("total", total_esperado)
            cnpjs = self._extrair_cnpjs_resposta(dados)

            if not cnpjs:
                break

            todos_cnpjs.extend(cnpjs)
            logger.info(
                "Pagina {}: {} CNPJ(s) (acumulado: {}/{}).",
                pagina,
                len(cnpjs),
                len(todos_cnpjs),
                total_esperado,
            )

            if self._atingiu_limite(len(todos_cnpjs)):
                todos_cnpjs = todos_cnpjs[: self.settings.max_resultados]
                break

            if len(todos_cnpjs) >= total_esperado:
                break

            if len(cnpjs) < limite_pagina:
                break

            pagina += 1
            time.sleep(self.settings.delay_entre_requisicoes)

        todos_cnpjs = list(dict.fromkeys(todos_cnpjs))
        logger.info("Total de CNPJs coletados na pesquisa: {}", len(todos_cnpjs))
        if total_esperado and len(todos_cnpjs) >= total_esperado:
            self._salvar_lista_cnpjs(todos_cnpjs)
        return todos_cnpjs

    def _salvar_lista_cnpjs(self, cnpjs: List[str]) -> None:
        from config import BASE_DIR

        caminho = BASE_DIR / "saida" / "cnpjs_pesquisa.txt"
        caminho.parent.mkdir(exist_ok=True)
        caminho.write_text("\n".join(cnpjs) + "\n", encoding="utf-8")
        logger.info("Lista de CNPJs salva em {} (retome com --cnpjs-arquivo).", caminho)

    def obter_detalhe(self, cnpj: str) -> EmpresaCnpj:
        cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())
        if cnpj_limpo in self._cache_detalhes:
            return self._cache_detalhes[cnpj_limpo]

        url = URL_DETALHE_OFICIAL.format(cnpj=cnpj_limpo)
        dados = self._request_json("GET", url)
        empresa = mapear_json_para_empresa(dados)
        self._cache_detalhes[cnpj_limpo] = empresa
        return empresa

    def _request_json(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        max_tentativas = 5
        espera_base = 60

        for tentativa in range(1, max_tentativas + 1):
            resposta = self.session.request(method, url, timeout=120, **kwargs)
            if resposta.status_code == 403 and "Just a moment" in resposta.text:
                raise RuntimeError("Bloqueio Cloudflare (403) na API da plataforma.")

            if resposta.status_code in (403, 429):
                espera = espera_base * tentativa
                logger.warning(
                    "HTTP {} em {} (tentativa {}/{}). Aguardando {}s...",
                    resposta.status_code,
                    url,
                    tentativa,
                    max_tentativas,
                    espera,
                )
                if tentativa == 2:
                    logger.info("Renovando sessao (re-login)...")
                    self._api_key = self._login()
                    self.session.headers["api-key"] = self._api_key
                time.sleep(espera)
                continue

            resposta.raise_for_status()
            try:
                return resposta.json()
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Resposta nao e JSON valido de {url}") from exc

        raise RuntimeError(f"Falha apos {max_tentativas} tentativas em {url}")

    def _atingiu_limite(self, total: int) -> bool:
        limite = self.settings.max_resultados
        return limite > 0 and total >= limite


class FonteOficial(CasaDadosClient, _ClienteHttpBase):
    """Usa a API paga com api-key (/v4 e /v5)."""

    def __init__(self, settings: Settings):
        _ClienteHttpBase.__init__(self, settings)
        if not settings.api_key:
            raise ValueError("API_KEY e obrigatoria quando FONTE=oficial. Configure no .env.")
        self.session.headers["api-key"] = settings.api_key

    def _filtro_para_oficial(self, filtro: FiltroPesquisa, pagina: int) -> Dict[str, Any]:
        return {
            "busca_textual": filtro.termo,
            "codigo_atividade_principal": filtro.atividade_principal,
            "codigo_natureza_juridica": filtro.natureza_juridica,
            "situacao_cadastral": [filtro.situacao_cadastral] if filtro.situacao_cadastral else [],
            "uf": filtro.uf,
            "municipio": filtro.municipio,
            "bairro": filtro.bairro,
            "cep": filtro.cep,
            "ddd": filtro.ddd,
            "limite": 1000,
            "pagina": pagina,
        }

    def pesquisar_todos(self, filtro: FiltroPesquisa) -> List[str]:
        todos_cnpjs: List[str] = []
        pagina = 1

        while True:
            payload = self._filtro_para_oficial(filtro, pagina)
            logger.info("Pesquisando pagina {} (fonte oficial)...", pagina)
            dados = self._request_json("POST", URL_SEARCH_OFICIAL, json=payload)
            cnpjs = extrair_cnpjs_da_pesquisa(dados)

            if not cnpjs:
                break

            todos_cnpjs.extend(cnpjs)
            logger.info("Pagina {}: {} CNPJs (total: {})", pagina, len(cnpjs), len(todos_cnpjs))

            if self._atingiu_limite(len(todos_cnpjs)):
                todos_cnpjs = todos_cnpjs[: self.settings.max_resultados]
                break

            if len(cnpjs) < payload["limite"]:
                break

            pagina += 1
            time.sleep(self.settings.delay_entre_requisicoes)

        return list(dict.fromkeys(todos_cnpjs))

    def obter_detalhe(self, cnpj: str) -> EmpresaCnpj:
        cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())
        url = URL_DETALHE_OFICIAL.format(cnpj=cnpj_limpo)
        dados = self._request_json("GET", url)
        return mapear_json_para_empresa(dados)


def criar_cliente(settings: Settings) -> CasaDadosClient:
    if settings.fonte == "plataforma":
        return FontePlataforma(settings)
    if settings.fonte == "oficial":
        return FonteOficial(settings)
    return FonteGratuita(settings)
