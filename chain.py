import logging                                               
import os
import openai
from dotenv import load_dotenv
from pydantic import ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException
from schemas import AnalisisTecnico

load_dotenv()

logging.basicConfig(                                                        
    level=logging.INFO,                                                     
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",          
)                                                                           
logger = logging.getLogger("pipeline")                                      

model = ChatOpenAI(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=0,
    max_retries=0,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sos un ingeniero de software senior. Analizás textos técnicos "
               "(descripciones de arquitectura o logs de error) y extraés sus entidades técnicas."),
    ("human", "Analizá el siguiente texto:\n\n{texto}"),
])

ERRORES_REINTENTABLES = (
    openai.RateLimitError,
    openai.InternalServerError,
    openai.APIConnectionError,
    ValidationError,
    OutputParserException,
)

structured_model = model.with_structured_output(AnalisisTecnico).with_retry(
    retry_if_exception_type=ERRORES_REINTENTABLES,
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

chain = prompt | structured_model


async def process_text(text: str) -> AnalisisTecnico:                       
    logger.info(f"Procesando texto de {len(text)} caracteres")
    try:
        resultado = await chain.ainvoke({"texto": text})
    except Exception as error:
        logger.error(f"Falló el procesamiento ({type(error).__name__}): {error}")
        raise
    logger.info(
        f"Validación OK: {len(resultado.tecnologias)} tecnologías, "
        f"criticidad={resultado.nivel_de_criticidad.value}"
    )
    return resultado
