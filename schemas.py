from enum import Enum
from pydantic import BaseModel, Field


class NivelCriticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class AnalisisTecnico(BaseModel):
    """Entidades técnicas extraídas de un texto (descripción de arquitectura o log de error)."""

    tecnologias: list[str] = Field(
        min_length=1,
        description="Tecnologías, lenguajes, frameworks o servicios mencionados explícitamente en el texto.",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Gravedad del problema descrito: baja, media o alta.",
    )
    resumen_tecnico: str = Field(
        description="Resumen técnico de una o dos oraciones.",
    )