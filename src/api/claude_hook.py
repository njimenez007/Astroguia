"""Generador de revelaciones con streaming vía Anthropic Claude."""
import os
import json
import sys
from pathlib import Path
from typing import AsyncGenerator

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prompts.gancho import (  # noqa: E402
    SYSTEM_INDIVIDUAL,
    SYSTEM_PAREJA,
    prepare_context_individual,
    prepare_context_pareja,
)

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no está configurada en .env")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


async def stream_hook(
    birth_data: dict,
    nombre: str,
    tipo: str = "individual",
    birth_data2: dict | None = None,
    nombre2: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Async generator que emite Server-Sent Events mientras Claude genera.

    Flujo individual: 2 revelaciones (personalidad + predicción).
    Flujo pareja:     1 revelación (compatibilidad).

    Eventos:
      data: {"e":"c","t":"<chunk>"}   — fragmento de texto
      data: {"e":"done"}              — stream completo
      data: {"e":"err","m":"<msg>"}   — error
    """
    client = _get_client()

    if tipo == "pareja" and birth_data2 and nombre2:
        system = SYSTEM_PAREJA
        context = prepare_context_pareja(birth_data, nombre, birth_data2, nombre2)
        user_msg = f"Genera la revelación de compatibilidad para esta pareja:\n\n{context}"
    else:
        system = SYSTEM_INDIVIDUAL.format(nombre=nombre)
        context = prepare_context_individual(birth_data, nombre)
        user_msg = f"Genera las 2 revelaciones para esta carta:\n\n{context}"

    try:
        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        ) as stream:
            async for chunk in stream.text_stream:
                payload = json.dumps({"e": "c", "t": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        yield 'data: {"e":"done"}\n\n'

    except Exception as ex:
        err_payload = json.dumps({"e": "err", "m": str(ex)}, ensure_ascii=False)
        yield f"data: {err_payload}\n\n"
