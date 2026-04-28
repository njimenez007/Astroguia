"""Mini-prompts: respuestas cortas a preguntas específicas del consultante."""
import os
import json
import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prompts.gancho import (  # noqa: E402
    MINI_PERSONALIDAD,
    MINI_PREDICCIONES,
    MINI_COMPATIBILIDAD,
    classify_pregunta,
    prepare_context_individual,
    prepare_context_pareja,
)

_client: AsyncAnthropic | None = None

_FORBIDDEN = [
    'sade sati', 'mahadasha', 'antardasha', 'nakshatra', 'lagna',
    'vimshottari', 'rahu', 'ketu', 'dasha',
]


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no está configurada")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


def _has_forbidden(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in _FORBIDDEN)


async def stream_pregunta(
    pregunta: str,
    tipo: str,
    birth_data: dict,
    nombre: str,
    birth_data2: dict | None = None,
    nombre2: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Genera una respuesta corta a la pregunta del consultante usando el
    mini-prompt correcto según el tipo de flujo y la naturaleza de la pregunta.
    """
    client = _get_client()

    if tipo == "pareja" and birth_data2 and nombre2:
        system = MINI_COMPATIBILIDAD.format(pregunta=pregunta)
        context = prepare_context_pareja(birth_data, nombre, birth_data2, nombre2)
    else:
        subtipo = classify_pregunta(pregunta)
        template = MINI_PREDICCIONES if subtipo == "predicciones" else MINI_PERSONALIDAD
        system = template.format(pregunta=pregunta)
        context = prepare_context_individual(birth_data, nombre)

    user_msg = f"Datos astrológicos del consultante:\n\n{context}"
    messages: list[dict] = [{"role": "user", "content": user_msg}]

    try:
        text = ""
        for attempt in range(2):
            response = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=600,
                system=system,
                messages=messages,
            )
            text = response.content[0].text

            if not _has_forbidden(text):
                break

            if attempt == 0:
                messages.append({"role": "assistant", "content": text})
                messages.append({
                    "role": "user",
                    "content": (
                        "Tu respuesta contiene términos técnicos de astrología. "
                        "Reescríbela con lenguaje cotidiano — sin planetas, signos ni términos sánscritos. "
                        "Segunda persona, íntimo, máximo 4 líneas + frase de cierre exacta."
                    ),
                })

        # Transmitir en chunks con sensación de streaming
        for i in range(0, len(text), 8):
            chunk = text[i:i + 8]
            yield f"data: {json.dumps({'e': 'c', 't': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)

        yield 'data: {"e":"done"}\n\n'

    except Exception as ex:
        yield f"data: {json.dumps({'e': 'err', 'm': str(ex)}, ensure_ascii=False)}\n\n"
