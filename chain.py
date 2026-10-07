import asyncio
import os
import openai                                                # NUEVO
from dotenv import load_dotenv
from pydantic import ValidationError                         # NUEVO
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException  # NUEVO
from schemas import AnalisisTecnico

load_dotenv()

model = ChatOpenAI(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=0,
    max_retries=0,  # NUEVO
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sos un ingeniero de software senior. Analizás textos técnicos "
               "(descripciones de arquitectura o logs de error) y extraés sus entidades técnicas."),
    ("human", "Analizá el siguiente texto:\n\n{texto}"),
])

ERRORES_REINTENTABLES = (           # NUEVO
    openai.RateLimitError,          # 429: demasiadas solicitudes
    openai.InternalServerError,     # 5xx: servidor con problemas (incluye el 503)
    openai.APIConnectionError,      # se cortó la red o tardó demasiado
    ValidationError,                # el modelo no cumplió el contrato
    OutputParserException,          # la respuesta no se pudo convertir al contrato
)

structured_model = model.with_structured_output(AnalisisTecnico).with_retry(  # CAMBIA
    retry_if_exception_type=ERRORES_REINTENTABLES,
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

chain = prompt | structured_model

async def main():
    resultado = await chain.ainvoke(
        {"texto": "Nuestra API en FastAPI usa Redis como caché y PostgreSQL como base de datos. Con 500 usuarios concurrentes se cae."}
    )
    print(resultado)
    print(resultado.tecnologias)

if __name__ == "__main__":
    asyncio.run(main())