"""Generador de revelaciones con validación automática y streaming simulado."""
import os
import json
import asyncio
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

# Términos técnicos prohibidos en el output final
_FORBIDDEN = [
    'sade sati', 'mahadasha', 'antardasha', 'nakshatra', 'lagna',
    'vimshottari', 'rahu', 'ketu', 'ashta-koota', 'ashtakoota',
    'kundali', 'graha', 'dasha',
]


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no está configurada en .env")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


def _has_forbidden(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in _FORBIDDEN)


async def _generate_clean(system: str, user_msg: str) -> str:
    """
    Genera la respuesta completa. Si contiene términos técnicos prohibidos,
    pide a Claude que la reescriba una vez más en lenguaje cotidiano.
    """
    client = _get_client()
    messages: list[dict] = [{"role": "user", "content": user_msg}]

    for attempt in range(2):
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=system,
            messages=messages,
        )
        text = response.content[0].text

        if not _has_forbidden(text):
            return text

        if attempt == 0:
            messages.append({"role": "assistant", "content": text})
            messages.append({
                "role": "user",
                "content": (
                    "Tu respuesta contiene términos técnicos de astrología prohibidos. "
                    "Reescríbela completamente usando SOLO lenguaje cotidiano — "
                    "sin nombrar planetas, signos zodiacales, ni términos sánscritos. "
                    "Mantén exactamente los mismos marcadores [R1T], [R1C], [R1P], etc. "
                    "y las frases de cierre exactas."
                ),
            })

    return text  # Devuelve el último intento aunque tenga términos


async def stream_hook(
    birth_data: dict,
    nombre: str,
    tipo: str = "individual",
    birth_data2: dict | None = None,
    nombre2: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Async generator que emite Server-Sent Events.

    Genera la respuesta completa, valida que no tenga tecnicismos,
    y luego la transmite en chunks para dar sensación de streaming.

    Eventos:
      data: {"e":"c","t":"<chunk>"}   — fragmento de texto
      data: {"e":"done"}              — stream completo
      data: {"e":"err","m":"<msg>"}   — error
    """
    if tipo == "pareja" and birth_data2 and nombre2:
        system = SYSTEM_PAREJA
        context = prepare_context_pareja(birth_data, nombre, birth_data2, nombre2)
        user_msg = f"Genera la revelación de compatibilidad:\n\n{context}"
    else:
        system = SYSTEM_INDIVIDUAL.format(nombre=nombre)
        context = prepare_context_individual(birth_data, nombre)
        user_msg = f"Genera las 2 revelaciones para {nombre}:\n\n{context}"

    try:
        text = await _generate_clean(system, user_msg)

        # Transmitir en chunks para sensación de streaming natural
        chunk_size = 10
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            yield f"data: {json.dumps({'e': 'c', 't': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)

        yield 'data: {"e":"done"}\n\n'

    except Exception as ex:
        yield f"data: {json.dumps({'e': 'err', 'm': str(ex)}, ensure_ascii=False)}\n\n"
