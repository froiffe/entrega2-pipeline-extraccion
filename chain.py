import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate     
from langchain_core.output_parsers import StrOutputParser 

load_dotenv()

model = ChatOpenAI(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([                                      
    ("system", "Sos un ingeniero de software senior que analiza textos técnicos."),
    ("human", "Listá las tecnologías mencionadas en este texto: {texto}"),      
])                                                                               

parser = StrOutputParser()

chain = prompt | model | parser

async def main():
    resultado = await chain.ainvoke(
        {"texto": "Nuestra API en FastAPI usa Redis como caché y PostgreSQL como base de datos. Con 500 usuarios concurrentes se cae."}
    )
    print(resultado)

if __name__ == "__main__":
    asyncio.run(main())