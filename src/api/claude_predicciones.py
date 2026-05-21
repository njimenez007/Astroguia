"""Generador de Lectura de Predicciones — Sade Sati + Dashas, 5 bloques con streaming."""
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

from prompts.predicciones import (  # noqa: E402
    SYSTEM,
    BLOCK_TITLES,
    prepare_predicciones_context,
    get_block_context,
    build_block_message,
)

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no está configurada")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


async def generate_predicciones(
    birth_data: dict, nombre: str
) -> AsyncGenerator[str, None]:
    """
    Genera la Lectura de Predicciones (5 bloques) vía SSE streaming.
    Eventos: block_start → c → block_done → done | err
    """
    client = _get_client()
    system = SYSTEM.format(nombre=nombre)
    ctx = prepare_predicciones_context(birth_data, nombre)
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
                max_tokens=6000,
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

            messages.append({"role": "assistant", "content": block_text})

            done_payload = json.dumps({"e": "block_done", "num": num}, ensure_ascii=False)
            yield f"data: {done_payload}\n\n"

        yield 'data: {"e":"done"}\n\n'

    except Exception as ex:
        err_payload = json.dumps({"e": "err", "m": str(ex)}, ensure_ascii=False)
        yield f"data: {err_payload}\n\n"
