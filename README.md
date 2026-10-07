# Pipeline de Extracción de Entidades Técnicas

Pre-entrega del Módulo 2 del curso de AI Engineering. Pipeline construido con LangChain (LCEL) que recibe un texto técnico (descripción de arquitectura o log de error) y devuelve un objeto validado con Pydantic.

## Estructura

- `schemas.py`: contrato de datos (`AnalisisTecnico`) con Pydantic.
- `chain.py`: cadena LCEL `prompt | model.with_structured_output(AnalisisTecnico)` con reintentos (`.with_retry()`) y la función asíncrona `process_text()` con logs.
- `prueba_pipeline.py`: script de prueba asíncrono con tres casos, incluida una prueba de estrés.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copiar `.env.example` como `.env` y completar la key de Google AI Studio.

## Uso

```bash
python prueba_pipeline.py
```

## Ejemplo de salida

Entrada:

> ERROR 2026-10-05 03:12:44 worker-celery: ConnectionRefusedError al conectar con RabbitMQ en amqp://rabbit:5672. Reintentos agotados. 1.200 tareas de facturación en cola.

Salida:

```json
{
  "tecnologias": ["Celery", "RabbitMQ"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "Fallo de conexión crítico entre Celery y RabbitMQ tras agotar los reintentos, dejando 1200 tareas de facturación en cola."
}
```

## Decisiones de diseño

- **Modelo:** Gemini (`gemini-3.5-flash-lite`) a través de `ChatOpenAI`, usando el endpoint compatible con OpenAI de Google.
- **Contrato:** `nivel_de_criticidad` es un enum (`baja`, `media`, `alta`). Las descripciones de cada campo funcionan como instrucciones para el modelo; por ejemplo, `tecnologias` pide solo las mencionadas explícitamente, para evitar que el modelo deduzca tecnologías implícitas.
- **Reintentos:** hasta 3 intentos con backoff exponencial y jitter, **solo** para errores transitorios (429, 5xx, red) y de formato (`ValidationError`, `OutputParserException`). Los errores permanentes (401, 404, 400) no se reintentan. Los reintentos internos del cliente de OpenAI están desactivados (`max_retries=0`) para que haya una sola capa de reintentos y los logs reflejen cada intento.
- **Logs:** nivel INFO. Cada pedido HTTP queda registrado con su código de respuesta, lo que permite contar los intentos; `process_text` registra el inicio, la validación exitosa o el error final.
- **Respuestas truncadas (`finish_reason`):** si el modelo corta la respuesta, el JSON llega incompleto, la validación falla y se reintenta.

## Prueba de estrés: lo que se encontró

Con un texto que no menciona ninguna tecnología, la primera versión usaba `min_length=1` en `tecnologias`. Gemini aplica esa regla al generar la respuesta, así que el modelo no podía devolver una lista vacía e **inventaba** un valor genérico (`"sistema"`), que pasaba la validación.

La solución fue reemplazar `min_length=1` por un `field_validator` de Pydantic: la regla "lista no vacía" se sigue cumpliendo, pero la controla Pydantic al recibir la respuesta y no el proveedor al generarla. Ahora el modelo devuelve la lista vacía, la validación la rechaza y el pipeline falla de forma visible en lugar de devolver datos falsos.

## Limitaciones conocidas

- Un texto sin tecnologías consume 3 pedidos antes de fallar, porque `ValidationError` está entre los errores reintentables. Una mejora posible sería distinguir este caso de los errores de formato que sí pueden resolverse reintentando.
- Pydantic valida que la respuesta cumpla el contrato, no que sea correcta: la criticidad la decide el modelo.