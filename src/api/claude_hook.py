"""Generador de revelaciones con streaming vía Anthropic Claude."""
import os
import json
import sys
from pathlib import Path
from typing import AsyncGenerator

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is importable
ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prompts.gancho import SYSTEM, prepare_context  # noqa: E402

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
    birth_data: dict, nombre: str
) -> AsyncGenerator[str, None]:
    """
    Async generator que emite Server-Sent Events mientras Claude genera.

    Eventos emitidos:
      data: {"e":"c","t":"<chunk>"}   — fragmento de texto de Claude
      data: {"e":"done"}              — stream completo
      data: {"e":"err","m":"<msg>"}   — error
    """
    client = _get_client()
    system = SYSTEM.format(nombre=nombre)
    context = prepare_context(birth_data, nombre)

    try:
        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"Genera las 4 revelaciones para esta carta:\n\n{context}",
                }
            ],
        ) as stream:
            async for chunk in stream.text_stream:
                payload = json.dumps({"e": "c", "t": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        yield 'data: {"e":"done"}\n\n'

    except Exception as ex:
        err_payload = json.dumps({"e": "err", "m": str(ex)}, ensure_ascii=False)
        yield f"data: {err_payload}\n\n"
