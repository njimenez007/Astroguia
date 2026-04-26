"""Generador de Carta Astral completa — 5 bloques secuenciales con streaming."""
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

from prompts.carta import (  # noqa: E402
    SYSTEM,
    BLOCK_TITLES,
    prepare_carta_context,
    get_block_context,
    build_block_message,
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


async def generate_carta_astral(
    birth_data: dict, nombre: str
) -> AsyncGenerator[str, None]:
    """
    Async generator que corre los 5 bloques de la Carta Astral secuencialmente.
    Mantiene historial de conversación para coherencia entre bloques.

    Eventos SSE emitidos:
      {"e":"block_start","num":N,"titulo":"..."}   — inicio de bloque
      {"e":"c","block":N,"t":"chunk"}              — fragmento de texto
      {"e":"block_done","num":N}                   — bloque completado
      {"e":"done"}                                 — informe completo
      {"e":"err","m":"msg"}                        — error
    """
    client = _get_client()
    system = SYSTEM.format(nombre=nombre)
    ctx = prepare_carta_context(birth_data, nombre)

    # Historial crece con cada bloque para mantener coherencia y evitar repetición
    messages: list[dict] = []

    try:
        for num in range(1, 6):
            block_ctx = get_block_context(num, ctx)
            user_msg = build_block_message(num, block_ctx)
            messages.append({"role": "user", "content": user_msg})

            start_payload = json.dumps(
                {"e": "block_start", "num": num, "titulo": BLOCK_TITLES[num]},
                ensure_ascii=False,
            )
            yield f"data: {start_payload}\n\n"

            block_text = ""
            async with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                system=system,
                messages=messages,
            ) as stream:
                async for chunk in stream.text_stream:
                    block_text += chunk
                    payload = json.dumps(
                        {"e": "c", "block": num, "t": chunk},
                        ensure_ascii=False,
                    )
                    yield f"data: {payload}\n\n"

            # Guardar respuesta del asistente para el siguiente bloque
            messages.append({"role": "assistant", "content": block_text})

            done_payload = json.dumps(
                {"e": "block_done", "num": num}, ensure_ascii=False
            )
            yield f"data: {done_payload}\n\n"

        yield 'data: {"e":"done"}\n\n'

    except Exception as ex:
        err_payload = json.dumps({"e": "err", "m": str(ex)}, ensure_ascii=False)
        yield f"data: {err_payload}\n\n"
