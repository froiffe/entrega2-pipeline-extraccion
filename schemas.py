from enum import Enum
from pydantic import BaseModel, Field, field_validator


class NivelCriticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class AnalisisTecnico(BaseModel):
    """Entidades técnicas extraídas de un texto (descripción de arquitectura o log de error)."""

    tecnologias: list[str] = Field(
        description=(
            "Tecnologías, lenguajes, frameworks o servicios mencionados explícitamente por su nombre en el texto. "
            "No inventes ni uses términos genéricos como 'sistema', 'servidor' o 'aplicación'. "
            "Si el texto no menciona ninguna tecnología, devolvé una lista vacía."
        ),
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Gravedad del problema descrito: baja, media o alta.",
    )
    resumen_tecnico: str = Field(
        description="Resumen técnico de una o dos oraciones.",
    )

    @field_validator("tecnologias")
    @classmethod
    def tecnologias_no_vacia(cls, valor: list[str]) -> list[str]:
        if not valor:
            raise ValueError("El texto no menciona ninguna tecnología identificable")
        return valor