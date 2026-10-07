import asyncio
from chain import process_text

TEXTOS = {
    "log de error": (
        "ERROR 2026-10-05 03:12:44 worker-celery: ConnectionRefusedError al conectar con "
        "RabbitMQ en amqp://rabbit:5672. Reintentos agotados. 1.200 tareas de facturación en cola."
    ),
    "arquitectura": (
        "El frontend en React consume una API GraphQL en Node.js. Las imágenes se guardan en "
        "Amazon S3 y los usuarios se autentican con Auth0. Todo corre en Kubernetes."
    ),
    "ambiguo (prueba de estrés)": (
        "Ayer el sistema anduvo lento un rato, pero después se normalizó. No sabemos bien qué pasó."
    ),
}


async def main():
    for nombre, texto in TEXTOS.items():
        print(f"\n===== Caso: {nombre} =====")
        try:
            resultado = await process_text(texto)
            print(resultado.model_dump_json(indent=2))
        except Exception:
            print("No se pudo obtener un resultado válido para este caso (ver logs).")


if __name__ == "__main__":
    asyncio.run(main())