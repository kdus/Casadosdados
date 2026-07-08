from dataclasses import dataclass, field, fields
from typing import List


@dataclass
class EmpresaCnpj:
    """Dados cadastrais de um CNPJ (uma empresa = uma linha no arquivo de saida)."""

    cnpj: str = ""
    razao_social: str = ""
    nome_fantasia: str = ""
    situacao_cadastral: str = ""
    data_situacao: str = ""
    motivo_situacao: str = ""
    data_abertura: str = ""
    matriz_filial: str = ""
    natureza_juridica: str = ""
    mei: str = ""
    simples: str = ""
    capital_social: str = ""
    porte: str = ""
    cnae_principal_codigo: str = ""
    cnae_principal_descricao: str = ""
    cnaes_secundarios: str = ""
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cep: str = ""
    municipio: str = ""
    uf: str = ""
    telefone1: str = ""
    telefone2: str = ""
    email: str = ""
    socios: str = ""
    ultima_atualizacao: str = ""

    @classmethod
    def nomes_campos(cls) -> List[str]:
        """Retorna os nomes das colunas na ordem definida (cabecalho do arquivo)."""
        return [f.name for f in fields(cls)]

    def to_linha(self) -> List[str]:
        """Retorna os valores na mesma ordem das colunas."""
        return [str(getattr(self, nome, "")) for nome in self.nomes_campos()]
