import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas import AnalisisTecnico  # NUEVO

load_dotenv()

model = ChatOpenAI(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sos un ingeniero de software senior. Analizás textos técnicos "   # CAMBIA
               "(descripciones de arquitectura o logs de error) y extraés sus entidades técnicas."),
    ("human", "Analizá el siguiente texto:\n\n{texto}"),                          # CAMBIA
])

structured_model = model.with_structured_output(AnalisisTecnico)  # NUEVO

chain = prompt | structured_model  # CAMBIA

async def main():
    resultado = await chain.ainvoke(
        {"texto": "Nuestra API en FastAPI usa Redis como caché y PostgreSQL como base de datos. Con 500 usuarios concurrentes se cae."}
    )
    print(resultado)               # CAMBIA (antes imprimía texto)
    print(resultado.tecnologias)   # NUEVO

if __name__ == "__main__":
    asyncio.run(main())