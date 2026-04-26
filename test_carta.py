"""
Test Carta Astral: muestra el mapeo completo de datos, analiza campos faltantes
y genera una preview del Bloque 1 con Claude (primeras 300 palabras).
"""
import asyncio
import json
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

sys.path.insert(0, os.path.dirname(__file__))

from src.api.engine import get_birth_data
from prompts.carta import (
    BLOCK_TITLES,
    SYSTEM,
    build_block_message,
    get_block_context,
    prepare_carta_context,
)

NOMBRE = "Nicolas Jimenez"
FECHA  = "2003-03-28"
HORA   = "08:07"
CIUDAD = "Bogota, Colombia"


def sep(title: str = "") -> None:
    print()
    print("=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def print_block_mapping(num: int, block_ctx: dict) -> None:
    print(f"\n--- BLOQUE {num}: {BLOCK_TITLES[num]} ---")
    for key, val in block_ctx.items():
        if key == "planetas_d1":
            print(f"  planetas_d1: [{len(val)} planetas]")
            for p in val:
                retro = " R" if p.get("retrograde") else ""
                print(
                    f"    {p['planeta']:12} {p.get('grado',''):15} "
                    f"{p.get('signo',''):12} Casa {p.get('casa','')} "
                    f"{p.get('dignidad','—')}{retro}"
                )
        elif key == "casas":
            print("  casas: [12 Whole Sign]")
            for h_num, h in val.items():
                ocup = ", ".join(o["planeta"] for o in h.get("ocupantes", []))
                print(
                    f"    Casa {h_num:2}: {h['signo']:12} "
                    f"Senor {h['senor']:10} en Casa {h.get('senor_en_casa','?')} "
                    f"| Ocupantes: {ocup or '--'}"
                )
        elif key == "shad_bala":
            print("  shad_bala:")
            for p in val:
                estado = "OK  " if p["sobre_minimo"] else "BAJO"
                print(
                    f"    [{p['rango']}] {p['planeta']:10} "
                    f"{p['rupas']:.3f} Rupas ({p['pct_minimo']:.0f}% min) "
                    f"{p['dignidad_d1']:15} {estado}"
                )
        elif key == "karakas_jaimini":
            print("  karakas_jaimini:")
            for k in val:
                print(
                    f"    {k['abrev']:4} {k['karaka']:25} -> "
                    f"{k['planeta']:10} {k.get('signo',''):12} Casa {k.get('casa','')}"
                )
        elif key in ("nakshatra_lagna", "nakshatra_luna", "nakshatra_sol"):
            nk = val
            print(
                f"  {key}: {nk.get('nombre','?')} Pada {nk.get('pada','?')} "
                f"| regente {nk.get('regente','?')} / {nk.get('deidad','?')}"
            )
        elif key == "doshas":
            print(f"  doshas: {json.dumps(val, ensure_ascii=False)}")
        elif key == "lagna":
            print(f"  lagna: {json.dumps(val, ensure_ascii=False)}")
        elif key == "yogas":
            nombres = [y.get("nombre", "?") for y in val[:5]]
            print(f"  yogas: {len(val)} total — {nombres}")
        elif key == "sade_sati":
            print(f"  sade_sati: {json.dumps(val, ensure_ascii=False)}")
        elif key == "dasha_actual":
            print(f"  dasha_actual: {json.dumps(val, ensure_ascii=False)}")
        elif key == "d9_lagna":
            print(f"  d9_lagna: {json.dumps(val, ensure_ascii=False)}")
        else:
            print(f"  {key}: {val}")


def check_missing(ctx: dict) -> list[str]:
    missing: list[str] = []

    doshas = ctx.get("doshas", {})
    if not doshas:
        missing.append("doshas_ayurvedicos — ausente del engine output")
    else:
        if not doshas.get("predominante"):
            missing.append("doshas.predominante — falta el dosha dominante")
        if not doshas.get("breakdown_pct"):
            missing.append("doshas.breakdown_pct — falta el desglose porcentual")

    if not ctx.get("yogas"):
        missing.append("yogas — lista vacia o ausente")

    if not ctx.get("d9_lagna"):
        missing.append("d9_lagna — lagna del Navamsha ausente")

    if not ctx.get("nakshatra_lagna", {}).get("nombre"):
        missing.append("nakshatra_lagna — Lagna no tiene nakshatra en planetas_d1")

    if not ctx.get("nakshatra_sol", {}).get("nombre"):
        missing.append("nakshatra_sol — Sol no tiene nakshatra en planetas_d1")

    shad = ctx.get("shad_bala", [])
    if not shad:
        missing.append("shad_bala — tabla vacia")
    else:
        no_ishta = [
            p["planeta"] for p in shad
            if p.get("ishta_phala", 0) == 0 and p.get("kashta_phala", 0) == 0
        ]
        if no_ishta:
            missing.append(
                f"shad_bala.ishta_phala/kashta_phala = 0 para: {', '.join(no_ishta)} "
                "(posiblemente no calculados por el engine)"
            )

    empty_karakas = [
        k["karaka"] for k in ctx.get("karakas_jaimini", []) if not k["planeta"]
    ]
    if empty_karakas:
        missing.append(
            f"karakas_jaimini — sin planeta para: {', '.join(empty_karakas)}"
        )

    casas = ctx.get("casas", {})
    if len(casas) < 12:
        missing.append(f"casas — solo {len(casas)} de 12 casas calculadas")

    return missing


async def run_block1_preview(birth_data: dict, nombre: str) -> str:
    """Corre el Bloque 1 con Claude — retorna las primeras ~300 palabras."""
    from anthropic import AsyncAnthropic
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "ERROR: ANTHROPIC_API_KEY no configurada"

    client = AsyncAnthropic(api_key=api_key)
    system = SYSTEM.format(nombre=nombre)
    ctx = prepare_carta_context(birth_data, nombre)
    block_ctx = get_block_context(1, ctx)
    user_msg = build_block_message(1, block_ctx)

    text = ""
    print("Generando Bloque 1 con Claude (limite 600 tokens para preview)...")
    print("-" * 70)
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        async for chunk in stream.text_stream:
            text += chunk

    words = text.split()
    return " ".join(words[:300])


async def main() -> None:
    sep("AstroGuia -- Test Carta Astral (Lectura de Primera Cita)")
    print(f"\nCalculando carta de {NOMBRE} ({FECHA} {HORA} - {CIUDAD})...")
    birth_data = get_birth_data(NOMBRE, FECHA, HORA, CIUDAD)
    ctx = prepare_carta_context(birth_data, NOMBRE)
    print("OK  Carta calculada.")

    # ── 1. Mapeo de datos ──────────────────────────────────────────────────
    sep("1. MAPEO COMPLETO JSON -> BLOQUES")
    for num in range(1, 6):
        block_ctx = get_block_context(num, ctx)
        print_block_mapping(num, block_ctx)

    # ── 2. Datos faltantes ─────────────────────────────────────────────────
    sep("2. ANALISIS DE DATOS FALTANTES / INCOMPLETOS")
    missing = check_missing(ctx)
    if missing:
        for m in missing:
            print(f"  FALTANTE: {m}")
    else:
        print("  Todos los campos disponibles. OK")

    # ── 3. Preview Bloque 1 ────────────────────────────────────────────────
    sep("3. BLOQUE 1 -- PRIMERAS 300 PALABRAS (generadas por Claude)")
    preview = await run_block1_preview(birth_data, NOMBRE)
    print(preview)
    print("\n[... continua ...]")

    sep()
    print("  Test completado.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
