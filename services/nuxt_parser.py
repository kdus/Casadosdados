"""Extrai dados de CNPJ do payload __NUXT_DATA__ embutido nas paginas HTML."""

import json
import re
import unicodedata
from typing import Any, Dict, List, Optional

from models import EmpresaCnpj
from services.mapeador import mapear_json_para_empresa


def slugify_razao_social(razao_social: str) -> str:
    """Gera slug usado na URL de detalhe do site."""
    texto = unicodedata.normalize("NFKD", razao_social or "")
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-zA-Z0-9\s-]", "", texto)
    texto = re.sub(r"\s+", "-", texto.strip())
    return texto.lower()


def montar_url_detalhe(cnpj: str, razao_social: str = "") -> str:
    cnpj_limpo = "".join(ch for ch in cnpj if ch.isdigit())
    slug = slugify_razao_social(razao_social) or "cnpj"
    return f"https://casadosdados.com.br/solucao/cnpj/{slug}-{cnpj_limpo}"


def _extrair_bloco_nuxt(html: str) -> Optional[str]:
    match = re.search(
        r'<script[^>]+id="__NUXT_DATA__"[^>]*>(.*?)</script>',
        html,
        flags=re.S,
    )
    if match:
        return match.group(1)

    idx = html.find('id="__NUXT_DATA__"')
    if idx >= 0:
        start = html.find(">", idx) + 1
        end = html.find("</script>", start)
        if start > 0 and end > start:
            return html[start:end]
    return None


def _resolver_referencias(payload: List[Any]) -> Any:
    """Resolve referencias numericas do formato compacto do Nuxt 3."""
    cache: Dict[int, Any] = {}

    def resolve(idx: int) -> Any:
        if idx in cache:
            return cache[idx]
        if idx < 0 or idx >= len(payload):
            return None

        valor = payload[idx]
        cache[idx] = valor

        if isinstance(valor, list) and len(valor) == 2 and isinstance(valor[0], str):
            tipo, ref = valor
            if tipo == "ShallowReactive":
                return resolve(ref)
            if tipo == "Reactive":
                return resolve(ref)
            if tipo == "Set":
                return resolve(ref)
            if tipo == "Ref":
                return resolve(ref)

        if isinstance(valor, list):
            return [resolve(v) if isinstance(v, int) else v for v in valor]

        if isinstance(valor, dict):
            return {k: resolve(v) if isinstance(v, int) else v for k, v in valor.items()}

        return valor

    return resolve(0)


def _buscar_cnpj_dict(obj: Any) -> Optional[Dict[str, Any]]:
    if isinstance(obj, dict) and obj.get("cnpj") and obj.get("razao_social"):
        return obj
    if isinstance(obj, dict):
        for valor in obj.values():
            encontrado = _buscar_cnpj_dict(valor)
            if encontrado:
                return encontrado
    elif isinstance(obj, list):
        for item in obj:
            encontrado = _buscar_cnpj_dict(item)
            if encontrado:
                return encontrado
    return None


def extrair_dados_cnpj_html(html: str) -> Dict[str, Any]:
    bloco = _extrair_bloco_nuxt(html)
    if not bloco:
        raise ValueError("Bloco __NUXT_DATA__ nao encontrado na pagina HTML")

    payload = json.loads(bloco)
    resolvido = _resolver_referencias(payload)
    dados = _buscar_cnpj_dict(resolvido)
    if not dados:
        raise ValueError("Dados de CNPJ nao encontrados no __NUXT_DATA__")
    return dados


def mapear_html_para_empresa(html: str) -> EmpresaCnpj:
    dados = extrair_dados_cnpj_html(html)
    empresa = mapear_json_para_empresa(dados)

    if not empresa.ultima_atualizacao and dados.get("data_consulta"):
        empresa.ultima_atualizacao = str(dados.get("data_consulta", ""))

    if dados.get("descricao_natureza_juridica") and not empresa.natureza_juridica:
        codigo = dados.get("codigo_natureza_juridica", "")
        empresa.natureza_juridica = f"{codigo} - {dados.get('descricao_natureza_juridica')}".strip(" -")

    if dados.get("porte_empresa") and isinstance(dados["porte_empresa"], dict):
        empresa.porte = str(dados["porte_empresa"].get("descricao", ""))

    if dados.get("contato_email") and isinstance(dados["contato_email"], list):
        emails = []
        for item in dados["contato_email"]:
            if isinstance(item, dict) and item.get("email"):
                emails.append(str(item["email"]))
        if emails and not empresa.email:
            empresa.email = emails[0]

    if dados.get("contato_telefonico") and isinstance(dados["contato_telefonico"], list):
        tels = []
        for item in dados["contato_telefonico"]:
            if isinstance(item, dict):
                ddd = str(item.get("ddd", ""))
                numero = str(item.get("numero", ""))
                if ddd and numero:
                    tels.append(f"({ddd}) {numero}")
        if tels:
            empresa.telefone1 = tels[0]
            if len(tels) > 1:
                empresa.telefone2 = tels[1]

    if dados.get("quadro_societario") and isinstance(dados["quadro_societario"], list):
        socios = []
        for socio in dados["quadro_societario"]:
            if isinstance(socio, dict):
                nome = socio.get("nome", "")
                qual = socio.get("qualificacao", "")
                if isinstance(qual, dict):
                    qual = qual.get("descricao", "")
                if nome:
                    socios.append(f"{nome} ({qual})" if qual else nome)
        if socios:
            empresa.socios = " | ".join(socios)

    if dados.get("atividade_secundaria") and isinstance(dados["atividade_secundaria"], list):
        sec = []
        for item in dados["atividade_secundaria"]:
            if isinstance(item, dict):
                sec.append(f"{item.get('codigo', '')} - {item.get('descricao', '')}".strip(" -"))
        if sec:
            empresa.cnaes_secundarios = " | ".join(sec)

    if dados.get("atividade_principal") and isinstance(dados["atividade_principal"], dict):
        ap = dados["atividade_principal"]
        empresa.cnae_principal_codigo = str(ap.get("codigo", ""))
        empresa.cnae_principal_descricao = str(ap.get("descricao", ""))

    if isinstance(dados.get("endereco"), dict):
        end = dados["endereco"]
        if not empresa.logradouro:
            tipo = end.get("tipo_logradouro", "")
            log = end.get("logradouro", "")
            empresa.logradouro = f"{tipo} {log}".strip() if tipo else str(log)
        empresa.numero = empresa.numero or str(end.get("numero", ""))
        empresa.complemento = empresa.complemento or str(end.get("complemento", ""))
        empresa.bairro = empresa.bairro or str(end.get("bairro", ""))
        empresa.cep = empresa.cep or str(end.get("cep", ""))
        empresa.uf = empresa.uf or str(end.get("uf", ""))
        if isinstance(end.get("municipio"), str):
            empresa.municipio = empresa.municipio or end.get("municipio", "")
        elif isinstance(end.get("municipio"), dict):
            empresa.municipio = empresa.municipio or str(end.get("municipio", {}).get("nome", ""))

    if isinstance(dados.get("situacao_cadastral"), dict):
        sit = dados["situacao_cadastral"]
        empresa.situacao_cadastral = empresa.situacao_cadastral or str(sit.get("situacao_atual", ""))
        empresa.motivo_situacao = empresa.motivo_situacao or str(sit.get("motivo", ""))
        if sit.get("data") and not empresa.data_situacao:
            empresa.data_situacao = str(sit.get("data", ""))

    if dados.get("mei") is False:
        empresa.mei = "Nao"
    elif dados.get("mei") is True:
        empresa.mei = "Sim"

    if dados.get("simples") is False:
        empresa.simples = "Nao"
    elif dados.get("simples") is True:
        empresa.simples = "Sim"

    return empresa
