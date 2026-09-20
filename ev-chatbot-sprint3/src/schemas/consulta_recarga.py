"""Schema Pydantic v2 do domínio EV (Aula 03). Extrai da pergunta do usuário os dados estruturados
de uma consulta de recarga. Os limites vêm da base: 16 códigos de erro e 3 modelos HCA G2."""
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

TipoConsulta = Literal[
    "diagnostico_erro", "faturamento", "potencia_carga", "instalacao",
    "operacao_comercial", "emergencia", "fora_escopo",
]


class ConsultaRecarga(BaseModel):
    tipo_consulta: TipoConsulta = Field(description="Categoria principal da pergunta")
    resumo: str = Field(max_length=200, description="Resumo da pergunta em uma frase curta")
    modelo_carregador: Optional[Literal["GW7K-HCA-20", "GW11K-HCA-20", "GW22K-HCA-20"]] = Field(
        None, description="Modelo do carregador citado; null se não houver ou se não for um dos 3 modelos"
    )
    codigo_erro: Optional[int] = Field(
        None, description="Número do código de erro citado (1 a 16), apenas o número inteiro, sem aspas; null se não houver"
    )
    estado_carregador: Optional[Literal["disponivel", "carregando", "falha", "desligado", "desconhecido"]] = Field(
        None, description="Estado do carregador descrito pelo usuário; null se não mencionado"
    )
    potencia_kw: Optional[float] = Field(None, description="Potência em kW citada (número positivo); null se não houver")
    consumo_kwh: Optional[float] = Field(None, description="Consumo em kWh citado (número >= 0); null se não houver")
    risco_eletrico: bool = Field(False, description="true se há fumaça, faísca, cheiro de queimado ou choque")
    requer_profissional: bool = Field(False, description="true se a situação exige técnico/eletricista habilitado")
    confianca: float = Field(ge=0, le=1, description="Confiança da extração entre 0 e 1")

    @field_validator("codigo_erro", mode="before")
    @classmethod
    def _limpar_codigo(cls, v):
        # LLMs costumam devolver "E5" ou "erro 5"
        if isinstance(v, str):
            m = re.search(r"\d+", v)
            return int(m.group()) if m else None
        return v

    @field_validator("codigo_erro")
    @classmethod
    def _codigo_na_base(cls, v):
        if v is not None and not 1 <= v <= 16:
            raise ValueError("codigo_erro deve estar entre 1 e 16 (códigos existentes na base)")
        return v

    @field_validator("potencia_kw")
    @classmethod
    def _potencia_positiva(cls, v):
        if v is not None and v <= 0:
            raise ValueError("potencia_kw deve ser positiva")
        return v

    @field_validator("consumo_kwh")
    @classmethod
    def _consumo_nao_negativo(cls, v):
        if v is not None and v < 0:
            raise ValueError("consumo_kwh não pode ser negativo")
        return v

    @model_validator(mode="after")
    def _emergencia_implica_risco(self):
        if self.tipo_consulta == "emergencia":
            self.risco_eletrico = True
            self.requer_profissional = True
        return self
