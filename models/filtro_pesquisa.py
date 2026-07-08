from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from models.empresa_cnpj import EmpresaCnpj

LIMITE_PESQUISA_GRATUITA = 20


def _parse_data(valor: Optional[str]) -> Optional[date]:
    """Converte ISO (2022-01-01, 2022-01-01T00:00:00Z) ou BR (01/01/2022) em date."""
    texto = (valor or "").strip()
    if not texto:
        return None
    if len(texto) >= 10 and texto[4] == "-" and texto[7] == "-":
        return datetime.strptime(texto[:10], "%Y-%m-%d").date()
    if len(texto) >= 10 and texto[2] == "/" and texto[5] == "/":
        return datetime.strptime(texto[:10], "%d/%m/%Y").date()
    return None


def _formatar_data_api(valor: Optional[str]) -> Optional[str]:
    """Converte data do filtro para YYYY-MM-DD (formato da API do site)."""
    data = _parse_data(valor)
    return data.isoformat() if data else None


@dataclass
class FiltroPesquisa:
    """Filtros da pesquisa avancada de CNPJ (equivalente aos campos do site)."""

    termo: List[str] = field(default_factory=list)
    atividade_principal: List[str] = field(default_factory=list)
    natureza_juridica: List[str] = field(default_factory=list)
    uf: List[str] = field(default_factory=list)
    municipio: List[str] = field(default_factory=list)
    bairro: List[str] = field(default_factory=list)
    cep: List[str] = field(default_factory=list)
    ddd: List[str] = field(default_factory=list)
    situacao_cadastral: str = "ATIVA"

    somente_mei: bool = False
    excluir_mei: bool = False
    com_email: bool = False
    incluir_atividade_secundaria: bool = False
    com_contato_telefonico: bool = False
    somente_fixo: bool = False
    somente_celular: bool = False
    somente_matriz: bool = False
    somente_filial: bool = False

    data_abertura_gte: Optional[str] = None
    data_abertura_lte: Optional[str] = None
    capital_social_gte: Optional[float] = None
    capital_social_lte: Optional[float] = None

    def to_payload_publico(self, page: int = 1, limite: int = None) -> dict:
        """Payload igual ao enviado pelo site (funcao R() em pesquisa-avancada)."""
        if limite is None:
            limite = LIMITE_PESQUISA_GRATUITA

        data_abertura: dict = {}
        inicio = _formatar_data_api(self.data_abertura_gte)
        fim = _formatar_data_api(self.data_abertura_lte)
        if inicio:
            data_abertura["inicio"] = inicio
        if fim:
            data_abertura["fim"] = fim

        payload: dict = {
            "cnpj": [],
            "cnpj_raiz": [],
            "codigo_atividade_principal": self.atividade_principal or [],
            "codigo_natureza_juridica": self.natureza_juridica or [],
            "incluir_atividade_secundaria": self.incluir_atividade_secundaria,
            "situacao_cadastral": [self.situacao_cadastral] if self.situacao_cadastral else [],
            "uf": self.uf or [],
            "municipio": self.municipio or [],
            "bairro": self.bairro or [],
            "cep": self.cep or [],
            "ddd": self.ddd or [],
            "data_abertura": data_abertura,
            "capital_social": {
                "minimo": self.capital_social_gte or 0,
                "maximo": self.capital_social_lte or 0,
            },
            "mei": {
                "optante": self.somente_mei,
                "excluir_optante": self.excluir_mei,
            },
            "simples": {
                "optante": False,
                "excluir_optante": False,
            },
            "mais_filtros": {
                "somente_matriz": self.somente_matriz,
                "somente_filial": self.somente_filial,
                "com_email": self.com_email,
                "com_telefone": self.com_contato_telefonico,
                "somente_fixo": self.somente_fixo,
                "somente_celular": self.somente_celular,
            },
            "limite": limite,
            "pagina": page,
        }

        if self.termo:
            payload["busca_textual"] = [
                {
                    "texto": self.termo,
                    "tipo_busca": "exata",
                    "razao_social": True,
                    "nome_fantasia": True,
                    "nome_socio": True,
                }
            ]

        return payload

    def atende_empresa(self, empresa: EmpresaCnpj) -> bool:
        """Valida se a empresa atende filtros verificaveis apenas no detalhe."""
        if self.data_abertura_gte:
            data_empresa = _parse_data(empresa.data_abertura)
            data_minima = _parse_data(self.data_abertura_gte)
            if data_minima and data_empresa and data_empresa < data_minima:
                return False
            if data_minima and not data_empresa:
                return False

        if self.data_abertura_lte:
            data_empresa = _parse_data(empresa.data_abertura)
            data_maxima = _parse_data(self.data_abertura_lte)
            if data_maxima and data_empresa and data_empresa > data_maxima:
                return False

        return True

    def resumo_filtros(self) -> str:
        """Texto legivel dos filtros ativos para log."""
        partes = [self.descricao_curta()]
        if self.data_abertura_gte:
            data = _parse_data(self.data_abertura_gte)
            if data:
                partes.append(f"abertura_a_partir_de_{data.strftime('%d-%m-%Y')}")
            else:
                partes.append(f"abertura_gte_{self.data_abertura_gte}")
        if self.data_abertura_lte:
            data = _parse_data(self.data_abertura_lte)
            if data:
                partes.append(f"abertura_ate_{data.strftime('%d-%m-%Y')}")
        return "_".join(partes)

    def to_payload(self, page: int) -> dict:
        """Monta o corpo JSON legado (endpoint antigo /v2/public/cnpj/search)."""
        return {
            "query": {
                "termo": self.termo,
                "atividade_principal": self.atividade_principal,
                "natureza_juridica": self.natureza_juridica,
                "uf": self.uf,
                "municipio": self.municipio,
                "bairro": self.bairro,
                "situacao_cadastral": self.situacao_cadastral,
                "cep": self.cep,
                "ddd": self.ddd,
            },
            "range_query": {
                "data_abertura": {
                    "lte": self.data_abertura_lte,
                    "gte": self.data_abertura_gte,
                },
                "capital_social": {
                    "lte": self.capital_social_lte,
                    "gte": self.capital_social_gte,
                },
            },
            "extras": {
                "somente_mei": self.somente_mei,
                "excluir_mei": self.excluir_mei,
                "com_email": self.com_email,
                "incluir_atividade_secundaria": self.incluir_atividade_secundaria,
                "com_contato_telefonico": self.com_contato_telefonico,
                "somente_fixo": self.somente_fixo,
                "somente_celular": self.somente_celular,
                "somente_matriz": self.somente_matriz,
                "somente_filial": self.somente_filial,
            },
            "page": page,
        }

    def descricao_curta(self) -> str:
        """Texto curto para compor o nome do arquivo de saida."""
        partes = []
        if self.termo:
            partes.append("-".join(self.termo))
        if self.uf:
            partes.append("-".join(self.uf))
        if self.municipio:
            partes.append("-".join(self.municipio))
        if self.bairro:
            partes.append("-".join(self.bairro))
        texto = "_".join(partes) if partes else "pesquisa"
        # Sanitiza para nome de arquivo
        for ch in ' /\\:*?"<>|':
            texto = texto.replace(ch, "-")
        return texto.lower()
