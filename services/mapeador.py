"""Mapeamento do JSON de resposta da Casa dos Dados para EmpresaCnpj."""

from typing import Any, Dict, List, Optional

from models import EmpresaCnpj


def _texto(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "Sim" if valor else "Nao"
    return str(valor).strip()


def _formatar_cnpj(cnpj: Any) -> str:
    numeros = "".join(ch for ch in str(cnpj or "") if ch.isdigit())
    if len(numeros) == 14:
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    return numeros


def _formatar_data(valor: Any) -> str:
    texto = _texto(valor)
    if len(texto) >= 10 and texto[4] == "-" and texto[7] == "-":
        return f"{texto[8:10]}/{texto[5:7]}/{texto[0:4]}"
    return texto


def _formatar_moeda(valor: Any) -> str:
    if valor is None or valor == "":
        return ""
    try:
        numero = float(valor)
        return f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return _texto(valor)


def _extrair_cnae(cnae: Any) -> tuple:
    if not isinstance(cnae, dict):
        return "", ""
    codigo = _texto(cnae.get("codigo") or cnae.get("code"))
    descricao = _texto(cnae.get("descricao") or cnae.get("description"))
    return codigo, descricao


def _formatar_cnaes_secundarios(cnaes: Any) -> str:
    if not isinstance(cnaes, list):
        return ""
    partes = []
    for item in cnaes:
        codigo, descricao = _extrair_cnae(item)
        if codigo or descricao:
            partes.append(f"{codigo} - {descricao}".strip(" -"))
    return " | ".join(partes)


def _formatar_socios(qsa: Any) -> str:
    if not isinstance(qsa, list):
        return ""
    partes = []
    for socio in qsa:
        if not isinstance(socio, dict):
            continue
        nome = _texto(socio.get("nome") or socio.get("nome_socio"))
        qualificacao = _texto(socio.get("qualificacao") or socio.get("qualificacao_socio"))
        if nome:
            partes.append(f"{nome} ({qualificacao})" if qualificacao else nome)
    return " | ".join(partes)


def _extrair_telefones(dados: Dict[str, Any]) -> tuple:
    telefones = dados.get("telefones") or dados.get("contato_telefonico") or []
    if isinstance(telefones, str):
        return telefones, ""
    if not isinstance(telefones, list):
        return "", ""

    formatados = []
    for tel in telefones:
        if isinstance(tel, dict):
            ddd = _texto(tel.get("ddd"))
            numero = _texto(tel.get("numero") or tel.get("telefone"))
            if ddd and numero:
                formatados.append(f"({ddd}) {numero}")
            elif numero:
                formatados.append(numero)
        else:
            formatados.append(_texto(tel))

    tel1 = formatados[0] if len(formatados) > 0 else ""
    tel2 = formatados[1] if len(formatados) > 1 else ""
    return tel1, tel2


def _extrair_endereco(dados: Dict[str, Any]) -> Dict[str, str]:
    endereco = dados.get("endereco") or dados.get("estabelecimento") or {}
    if not isinstance(endereco, dict):
        endereco = {}

    return {
        "logradouro": _texto(
            endereco.get("logradouro")
            or endereco.get("tipo_logradouro", "") + " " + endereco.get("logradouro", "")
        ).strip(),
        "numero": _texto(endereco.get("numero")),
        "complemento": _texto(endereco.get("complemento")),
        "bairro": _texto(endereco.get("bairro")),
        "cep": _texto(endereco.get("cep")),
        "municipio": _texto(endereco.get("municipio") or endereco.get("cidade")),
        "uf": _texto(endereco.get("uf") or endereco.get("estado")),
    }


def mapear_json_para_empresa(dados: Dict[str, Any]) -> EmpresaCnpj:
    """Converte o JSON de detalhe (gratuito ou oficial) em EmpresaCnpj."""
    if not dados:
        return EmpresaCnpj()

    # Alguns endpoints retornam os dados aninhados
    raiz = dados.get("data") if isinstance(dados.get("data"), dict) else dados
    if isinstance(raiz.get("cnpj"), dict):
        raiz = raiz["cnpj"]

    endereco = _extrair_endereco(raiz)
    tel1, tel2 = _extrair_telefones(raiz)

    cnae_principal = raiz.get("atividade_principal") or raiz.get("cnae_principal") or {}
    cnae_codigo, cnae_descricao = _extrair_cnae(cnae_principal)
    cnaes_sec = raiz.get("atividades_secundarias") or raiz.get("cnaes_secundarios") or []

    natureza = raiz.get("natureza_juridica") or {}
    if isinstance(natureza, dict):
        natureza_texto = f"{_texto(natureza.get('codigo'))} - {_texto(natureza.get('descricao'))}".strip(" -")
    else:
        natureza_texto = _texto(natureza)

    matriz_filial = _texto(raiz.get("matriz_filial") or raiz.get("identificador_matriz_filial"))
    if matriz_filial.upper() in ("1", "MATRIZ"):
        matriz_filial = "MATRIZ"
    elif matriz_filial.upper() in ("2", "FILIAL"):
        matriz_filial = "FILIAL"

    simples = raiz.get("simples") or {}
    if isinstance(simples, dict):
        simples_texto = "Sim" if simples.get("optante") else "Nao"
    else:
        simples_texto = _texto(simples)

    mei = raiz.get("mei") or raiz.get("empresa_mei")
    if isinstance(mei, dict):
        mei_texto = "Sim" if mei.get("optante") else "Nao"
    elif isinstance(mei, bool):
        mei_texto = "Sim" if mei else "Nao"
    else:
        mei_texto = _texto(mei) or ("Sim" if str(raiz.get("opcao_mei", "")).lower() in ("s", "sim", "true") else "Nao")

    situacao = raiz.get("situacao_cadastral") or raiz.get("situacao")
    if isinstance(situacao, dict):
        situacao_texto = _texto(situacao.get("situacao_atual") or situacao.get("nome"))
    else:
        situacao_texto = _texto(situacao)

    return EmpresaCnpj(
        cnpj=_formatar_cnpj(raiz.get("cnpj") or raiz.get("cnpj_raiz")),
        razao_social=_texto(raiz.get("razao_social") or raiz.get("nome")),
        nome_fantasia=_texto(raiz.get("nome_fantasia") or raiz.get("fantasia") or "-"),
        situacao_cadastral=situacao_texto,
        data_situacao=_formatar_data(raiz.get("data_situacao") or raiz.get("data_situacao_cadastral")),
        motivo_situacao=_texto(raiz.get("motivo_situacao") or raiz.get("motivo_situacao_cadastral")),
        data_abertura=_formatar_data(raiz.get("data_abertura") or raiz.get("data_inicio_atividade")),
        matriz_filial=matriz_filial,
        natureza_juridica=natureza_texto,
        mei=mei_texto,
        simples=simples_texto,
        capital_social=_formatar_moeda(raiz.get("capital_social")),
        porte=_texto(raiz.get("porte") or raiz.get("porte_empresa")),
        cnae_principal_codigo=cnae_codigo,
        cnae_principal_descricao=cnae_descricao,
        cnaes_secundarios=_formatar_cnaes_secundarios(cnaes_sec),
        logradouro=endereco["logradouro"],
        numero=endereco["numero"],
        complemento=endereco["complemento"],
        bairro=endereco["bairro"],
        cep=endereco["cep"],
        municipio=endereco["municipio"],
        uf=endereco["uf"],
        telefone1=tel1,
        telefone2=tel2,
        email=_texto(raiz.get("email") or raiz.get("correio_eletronico")),
        socios=_formatar_socios(raiz.get("qsa") or raiz.get("socios")),
        ultima_atualizacao=_texto(raiz.get("ultima_atualizacao") or raiz.get("updated_at")),
    )


def extrair_cnpjs_da_pesquisa(resposta: Dict[str, Any]) -> List[str]:
    """Extrai lista de CNPJs (somente digitos) da resposta da pesquisa."""
    cnpjs = []

    candidatos = [
        resposta.get("data"),
        resposta.get("cnpjs"),
        resposta.get("resultados"),
        resposta.get("results"),
    ]

    for bloco in candidatos:
        if not isinstance(bloco, list):
            continue
        for item in bloco:
            if isinstance(item, str):
                cnpjs.append("".join(ch for ch in item if ch.isdigit()))
            elif isinstance(item, dict):
                valor = item.get("cnpj") or item.get("cnpj_cpf") or item.get("id")
                cnpjs.append("".join(ch for ch in str(valor or "") if ch.isdigit()))

    return [c for c in cnpjs if len(c) == 14]
